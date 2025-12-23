#!/usr/bin/env python3
"""
Linux Voice AI Assistant (LVA) v0
Main application entry point.
"""

import yaml
import logging
import signal
import sys
from pathlib import Path
from pynput import keyboard

# Import modules
from audio import AudioRecorder, AudioPlayer
from stt import WhisperEngine
from parser import CommandParser
from actions import AppController, SystemInfo
from tts.google_tts import GoogleTTS
from utils import setup_logging, generate_response, get_error_response
from ui import SiriUI
from llm import OllamaClient, SmartRouter, SystemPrompts

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Main voice assistant application."""
    
    def __init__(self, config_file="config/config.yaml"):
        """
        Initialize the voice assistant.
        
        Args:
            config_file: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Setup logging
        log_config = self.config.get('logging', {})
        setup_logging(
            log_file=log_config.get('file', 'logs/lva.log'),
            level=log_config.get('level', 'INFO'),
            max_bytes=log_config.get('max_bytes', 10485760),
            backup_count=log_config.get('backup_count', 5)
        )
        
        logger.info("=" * 60)
        logger.info("Linux Voice AI Assistant v1 - Starting")
        logger.info("=" * 60)
        
        # Initialize components
        self._init_components()
        
        # State
        self.is_recording = False
        self.hotkey_listener = None
        
        # Initialize UI
        self.ui = SiriUI()
        self.ui.start()
        logger.info("Visual UI initialized")
        
        logger.info("Voice Assistant initialized successfully")
        logger.info(f"Hotkey: {self.config['hotkey']['combination']}")
    
    def _load_config(self, config_file):
        """Load configuration from YAML file."""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _init_components(self):
        """Initialize all components."""
        # Audio
        audio_config = self.config.get('audio', {})
        self.recorder = AudioRecorder(
            sample_rate=audio_config.get('sample_rate', 16000),
            channels=audio_config.get('channels', 1),
            temp_dir=self.config['paths']['temp_audio']
        )
        self.player = AudioPlayer()
        
        # STT
        stt_config = self.config.get('stt', {})
        self.stt = WhisperEngine(
            model_name=stt_config.get('model_name', 'tiny'),
            device=stt_config.get('device', 'cpu'),
            compute_type=stt_config.get('compute_type', 'int8'),
            language=stt_config.get('language', 'en')
        )
        
        # Parser (rule-based fallback)
        self.parser = CommandParser()
        
        # LLM
        llm_config = self.config.get('llm', {})
        self.llm_client = None
        self.router = None
        
        if llm_config.get('enabled', True):
            try:
                self.llm_client = OllamaClient(
                    base_url=llm_config.get('base_url', 'http://localhost:11434'),
                    model=llm_config.get('model', 'functiongemma:270m'),
                    timeout=llm_config.get('timeout', 30)
                )
                
                # Check if model is available
                if self.llm_client.check_connection():
                    if not self.llm_client.check_model_available():
                        logger.warning(f"Model {llm_config.get('model')} not found. Run: ollama pull {llm_config.get('model')}")
                    else:
                        logger.info(f"LLM ready: {llm_config.get('model')}")
                else:
                    logger.warning("Ollama not running. Start with: ollama serve")
                
                # Initialize router
                self.router = SmartRouter(self.llm_client, self.parser, self.config)
                logger.info("Smart router initialized (hybrid mode)")
                
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                logger.info("Falling back to rule-based mode")
        else:
            logger.info("LLM disabled in config")
        
        # Actions
        self.app_controller = AppController(self.parser)
        self.system_info = SystemInfo(self.parser)
        
        # TTS
        tts_config = self.config.get('tts', {})
        self.tts = GoogleTTS(
            lang=tts_config.get('lang', 'en'),
            tld=tts_config.get('tld', 'com')
        )
    
    def process_voice_command(self):
        """Process a voice command (full pipeline)."""
        logger.info("Processing voice command...")
        
        # 1. Record audio
        logger.info("Recording audio... (5 seconds)")
        print("\n🎤 Listening...")
        self.ui.set_listening(True)
        
        audio_file = self.recorder.record_audio(duration=5)
        
        self.ui.set_processing(True)
        
        if not audio_file:
            logger.error("Failed to record audio")
            self._speak(get_error_response('no_audio', self.parser))
            return
        
        # 2. Transcribe
        print("🔄 Transcribing...")
        text = self.stt.transcribe(audio_file)
        
        if not text:
            logger.warning("Transcription failed or empty")
            self._speak(get_error_response('transcription_failed', self.parser))
            return
        
        print(f"📝 You said: \"{text}\"")
        
        # 3. Route command (rules vs LLM)
        if self.router:
            processor_type, data = self.router.route(text)
            print(f"🧠 Using: {processor_type.upper()}")
        else:
            # Fallback to rules only
            processor_type = 'rules'
            data = self.parser.parse(text)
        
        # 4. Process based on route
        if processor_type == 'llm':
            response_text = self._process_with_llm(data['text'], data.get('context'))
        else:
            # Rule-based processing
            intent = data
            
            if not intent or intent['intent'] == 'unknown':
                logger.warning("Unknown command")
                self._speak(get_error_response('unknown_command', self.parser))
                return
            
            print(f"⚙️  Executing: {intent['intent']} - {intent['target']}")
            result = self._execute_action(intent)
            response_text = generate_response(result, self.parser)
        
        print(f"💬 Response: {response_text}")
        
        # 5. Speak response
        self._speak(response_text)
        
        # Return to idle
        self.ui.set_idle()
        
        # Cleanup
        self.recorder.cleanup_old_recordings(keep_last=5)
    
    def _process_with_llm(self, text, context=None):
        """
        Process command using LLM.
        
        Args:
            text: User command
            context: Optional conversation context
            
        Returns:
            str: Response text
        """
        try:
            # Get system prompt
            system_prompt = SystemPrompts.get_system_prompt()
            
            # Generate response
            result = self.llm_client.generate(
                prompt=text,
                system=system_prompt,
                temperature=self.config.get('llm', {}).get('temperature', 0.7),
                max_tokens=self.config.get('llm', {}).get('max_tokens', 512)
            )
            
            if result.get('success'):
                return result.get('response', 'I processed your request.')
            else:
                logger.error(f"LLM error: {result.get('message')}")
                # Fallback to rule-based
                intent = self.parser.parse(text)
                if intent and intent['intent'] != 'unknown':
                    exec_result = self._execute_action(intent)
                    return generate_response(exec_result, self.parser)
                return "I'm having trouble understanding that. Could you rephrase?"
                
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return "I encountered an error. Please try again."
    
    def _execute_action(self, intent):
        """
        Execute action based on intent.
        
        Args:
            intent: Parsed intent dictionary
            
        Returns:
            dict: Action result
        """
        intent_type = intent['intent']
        target = intent['target']
        
        if intent_type == 'open_app':
            return self.app_controller.open_app(target)
        elif intent_type == 'close_app':
            return self.app_controller.close_app(target)
        elif intent_type == 'system_info':
            return self.system_info.get_info(target)
        else:
            return {
                'success': False,
                'message': "Unknown action type."
            }
    
    def _speak(self, text):
        """
        Speak text using TTS.
        
        Args:
            text: Text to speak
        """
        print("🔊 Speaking...")
        
        audio_file = self.tts.speak(text)
        
        if audio_file:
            self.player.play_file(audio_file)
        else:
            logger.error("TTS synthesis failed")
    
    def _on_hotkey_press(self):
        """Callback when hotkey is pressed."""
        if not self.is_recording:
            self.is_recording = True
            try:
                self.process_voice_command()
            except Exception as e:
                logger.error(f"Error processing command: {e}", exc_info=True)
            finally:
                self.is_recording = False
    
    def start(self):
        """Start the voice assistant."""
        logger.info("Starting voice assistant...")
        print("\n" + "=" * 60)
        print("🎙️  Linux Voice AI Assistant v1 (LLM-Powered)")
        print("=" * 60)
        
        # Show LLM status
        if self.llm_client and self.llm_client.check_connection():
            print(f"🧠 LLM: {self.config.get('llm', {}).get('model', 'functiongemma:270m')} (Hybrid Mode)")
        else:
            print("⚙️  Mode: Rule-based only (LLM unavailable)")
        
        print(f"\nPress {self.config['hotkey']['combination'].upper()} to speak")
        print("Press Ctrl+C to exit\n")
        
        # Parse hotkey combination
        hotkey_combo = self.config['hotkey']['combination']
        
        # Start hotkey listener
        try:
            with keyboard.GlobalHotKeys({
                hotkey_combo: self._on_hotkey_press
            }) as self.hotkey_listener:
                self.hotkey_listener.join()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the voice assistant."""
        logger.info("Stopping voice assistant...")
        if self.ui:
            self.ui.stop()
        print("\n👋 Goodbye!")
        sys.exit(0)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n👋 Shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start assistant
    try:
        assistant = VoiceAssistant()
        assistant.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

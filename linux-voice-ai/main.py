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
from stt import WhisperEngine, WakeWordManager
from parser import CommandParser
from actions import AppController, SystemInfo
from tts.google_tts import GoogleTTS
from utils import setup_logging, generate_response, get_error_response
from ui import SiriUI
from llm import OllamaClient, SmartRouter, SystemPrompts
from tools import ToolRegistry, ToolExecutor
from tools.builtin import (
    ListFilesTool, ReadFileTool, SearchFilesTool,
    GetSystemInfoTool, GetProcessesTool, ExecuteCommandTool,
    SearchWebTool, FetchURLTool,
    OpenAppTool, RunScriptTool, CloseAppTool
)

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
        self.wake_word_active = False
        
        # Initialize UI
        self.ui = SiriUI()
        self.ui.start()
        logger.info("Visual UI initialized")
        
        logger.info("Voice Assistant initialized successfully")
        
        # Show activation methods
        hotkey = self.config['hotkey']['combination']
        wake_config = self.config.get('wake_word', {})
        logger.info(f"Hotkey: {hotkey}")
        if wake_config.get('enabled', False) and self.wake_word_manager:
            logger.info(f"Wake word: Say 'Hey JARVIS' for hands-free activation")
    
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
        
        # Tools
        self.tool_registry = ToolRegistry()
        self.tool_executor = None
        
        # Register built-in tools
        self._register_tools()
        
        # Initialize tool executor
        if self.llm_client:
            self.tool_executor = ToolExecutor(self.tool_registry)
            logger.info(f"Tool executor initialized with {len(self.tool_registry)} tools")
        
        # TTS
        tts_config = self.config.get('tts', {})
        self.tts = GoogleTTS(
            lang=tts_config.get('lang', 'en'),
            tld=tts_config.get('tld', 'com')
        )
        
        # Wake Word Detection
        self.wake_word_manager = None
        wake_config = self.config.get('wake_word', {})
        if wake_config.get('enabled', False):
            try:
                self.wake_word_manager = WakeWordManager(
                    config=wake_config,
                    on_wake=self._on_wake_word_detected
                )
                if self.wake_word_manager.is_available():
                    logger.info(f"Wake word detection ready: '{wake_config.get('model', 'hey_jarvis')}'")
                else:
                    logger.warning("Wake word not available - install openwakeword")
                    self.wake_word_manager = None
            except Exception as e:
                logger.error(f"Failed to initialize wake word: {e}")
                self.wake_word_manager = None
    
    def _register_tools(self):
        """Register all built-in tools"""
        tools = [
            # Filesystem tools
            ListFilesTool(),
            ReadFileTool(),
            SearchFilesTool(),
            # System tools
            GetSystemInfoTool(),
            GetProcessesTool(),
            ExecuteCommandTool(),
            # Web tools
            SearchWebTool(),
            FetchURLTool(),
            # App control tools
            OpenAppTool(),
            RunScriptTool(),
            CloseAppTool(),
        ]
        
        for tool in tools:
            self.tool_registry.register(tool)
        
        logger.info(f"Registered {len(tools)} built-in tools")
    
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
        Process command using LLM with text-based tool calling.
        
        Args:
            text: User command
            context: Optional conversation context
            
        Returns:
            str: Response text
        """
        try:
            # Get system prompt with tools
            tool_schemas = self.tool_registry.get_all_schemas() if self.tool_executor else []
            system_prompt = SystemPrompts.get_system_prompt(
                include_tools=len(tool_schemas) > 0,
                tools=tool_schemas
            )
            
            # First LLM call - ask if it needs tools
            result = self.llm_client.generate(
                prompt=text,
                system=system_prompt,
                temperature=self.config.get('llm', {}).get('temperature', 0.7),
                max_tokens=self.config.get('llm', {}).get('max_tokens', 512)
            )
            
            if not result.get('success'):
                logger.error(f"LLM error: {result.get('message')}")
                # Fallback to rule-based
                intent = self.parser.parse(text)
                if intent and intent['intent'] != 'unknown':
                    exec_result = self._execute_action(intent)
                    return generate_response(exec_result, self.parser)
                return "I'm having trouble understanding that. Could you rephrase?"
            
            response = result.get('response', '')
            
            # Check if LLM wants to use a tool (text-based format)
            if 'TOOL:' in response and self.tool_executor:
                logger.info("LLM requested tool usage (text-based)")
                
                # Parse tool call from response
                tool_call = self._parse_tool_call(response)
                
                if tool_call:
                    tool_name = tool_call['name']
                    tool_params = tool_call['params']
                    
                    logger.info(f"Executing tool: {tool_name} with params: {tool_params}")
                    
                    # Execute the tool
                    tool_result = self.tool_executor.execute(tool_name, tool_params)
                    
                    # Format result clearly
                    result_text = self.tool_executor.format_result_for_llm(tool_result)
                    
                    logger.debug(f"Tool result formatted: {result_text}")
                    
                    # Get final response from LLM with tool results
                    final_prompt = f"""I asked: "{text}"

The {tool_name} tool returned this data:
{result_text}

Answer my question using the data above. Be specific with numbers.
Keep it brief (1-2 sentences) since it will be spoken aloud."""
                    
                    final_result = self.llm_client.generate(
                        prompt=final_prompt,
                        system="You are JARVIS. Answer using the data provided. Use specific numbers.",
                        temperature=0.3,  # Lower for accuracy
                        max_tokens=100
                    )
                    
                    if final_result.get('success'):
                        final_response = final_result.get('response', '')
                        # If LLM still refuses, provide direct answer from data
                        if any(word in final_response.lower() for word in ['cannot', 'unable', 'sorry', "don't have"]):
                            return self._generate_direct_answer(tool_name, tool_result, text)
                        return final_response
                    else:
                        # LLM failed, generate direct answer
                        return self._generate_direct_answer(tool_name, tool_result, text)
            
            # No tools needed or tool execution failed, return direct response
            return response
                
        except Exception as e:
            logger.error(f"LLM processing failed: {e}", exc_info=True)
            return "I encountered an error. Please try again."
    
    def _parse_tool_call(self, response: str) -> dict:
        """Parse tool call from LLM text response."""
        import re
        
        VALID_TOOLS = {
            'open_app', 'close_app', 'run_script',
            'get_system_info', 'get_processes', 'list_files',
            'read_file', 'search_files', 'execute_command',
            'search_web', 'fetch_url'
        }
        
        try:
            match = re.search(r'TOOL:\s*([\w_]+)\(([^)]*)\)', response)
            if not match:
                return None
            
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Validate tool name
            if tool_name not in VALID_TOOLS:
                logger.warning(f"Invalid tool: {tool_name}")
                return None
            
            # Parse parameters  
            params = {}
            if params_str.strip():
                for m in re.findall(r'(\w+)\s*=\s*"([^"]*)"', params_str):
                    params[m[0]] = m[1]
                for m in re.findall(r"(\w+)\s*=\s*'([^']*)'", params_str):
                    params[m[0]] = m[1]
            
            logger.info(f"Parsed: {tool_name} params: {params}")
            return {'name': tool_name, 'params': params}
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _generate_direct_answer(self, tool_name: str, tool_result: dict, question: str) -> str:
        """
        Generate a direct answer from tool results when LLM fails.
        
        Args:
            tool_name: Name of the tool that was called
            tool_result: Raw tool execution result
            question: Original user question
            
        Returns:
            str: Direct answer based on tool data
        """
        if not tool_result.get('success'):
            return "I encountered an error getting that information."
        
        result = tool_result.get('result', {})
        
        # Handle different tool results
        if tool_name == 'get_system_info':
            parts = []
            if 'cpu' in result:
                cpu = result['cpu']
                parts.append(f"CPU usage is at {cpu.get('usage_percent', 0):.1f}%")
            if 'memory' in result:
                mem = result['memory']
                used_gb = mem.get('used_gb', 0)
                total_gb = mem.get('total_gb', 0)
                percent = mem.get('percent', 0)
                parts.append(f"Memory is {percent:.0f}% used ({used_gb:.1f}GB of {total_gb:.1f}GB)")
            if 'disk' in result:
                disk = result['disk']
                free_gb = disk.get('free_gb', 0)
                parts.append(f"Disk has {free_gb:.1f}GB free")
            return ". ".join(parts) if parts else "System information retrieved."
        
        elif tool_name == 'list_files':
            count = result.get('count', 0)
            path = result.get('path', '.')
            return f"I found {count} files in {path}."
        
        elif tool_name == 'get_processes':
            processes = result.get('processes', [])
            return f"There are {len(processes)} active processes running."
        
        elif tool_name == 'search_web':
            results = result.get('results', [])
            if results:
                return f"I found {len(results)} results. The top result is: {results[0].get('title', 'Unknown')}"
            return "No search results found."
        
        else:
            # Generic response
            return "I retrieved the information you requested."
    
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
    
    def _on_wake_word_detected(self):
        """Callback when wake word is detected."""
        logger.info("Wake word detected - triggering voice command")
        if not self.is_recording:
            self.is_recording = True
            try:
                # Play acknowledgment sound or speak
                print("\n🎤 Yes? I'm listening...")
                self.process_voice_command()
            except Exception as e:
                logger.error(f"Error processing wake word command: {e}", exc_info=True)
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
        
        # Activation methods
        print(f"\nPress {self.config['hotkey']['combination'].upper()} to speak")
        
        # Start wake word detection if available
        if self.wake_word_manager and self.wake_word_manager.is_available():
            if self.wake_word_manager.start():
                self.wake_word_active = True
                wake_model = self.config.get('wake_word', {}).get('model', 'hey_jarvis')
                print(f"🗣️  Or say 'Hey JARVIS' for hands-free activation")
                logger.info(f"Wake word listening active: {wake_model}")
        
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
        
        # Stop wake word detection
        if self.wake_word_manager:
            self.wake_word_manager.stop()
            self.wake_word_active = False
        
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

#!/usr/bin/env python3
"""
JARVIS - Linux Voice AI Assistant v2.0
Improved architecture with:
- Platform detection and adaptation
- Robust tool parsing
- Unified TTS with fallbacks
- Intent-based routing
- Sandboxed script execution
"""

import yaml
import logging
import signal
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from pynput import keyboard

# Core imports
from audio import AudioRecorder, AudioPlayer
from stt import WhisperEngine, WakeWordManager
from parser import CommandParser
from actions import AppController, SystemInfo
from utils import setup_logging, generate_response, get_error_response
from ui import SiriUI

# LLM imports
from llm import OllamaClient, SmartRouter
from llm.improved_prompts import ImprovedPrompts, DynamicPromptBuilder

# Tool system imports
from tools import ToolRegistry, ToolExecutor
from tools.builtin import (
    ListFilesTool, ReadFileTool, SearchFilesTool,
    GetSystemInfoTool, GetProcessesTool, ExecuteCommandTool,
    SearchWebTool, FetchURLTool,
    OpenAppTool, RunScriptTool, CloseAppTool
)

# New v2 imports
from capabilities import PlatformDetector, PlatformAdapter, get_manifest
from intents import create_registry_with_defaults
from execution import ToolCallParser, create_sandbox
from tts.engine import UnifiedTTSEngine

logger = logging.getLogger(__name__)


class JarvisAssistant:
    """
    JARVIS Voice Assistant v2.0

    Improvements over v1:
    - Cross-platform support (Ubuntu/Arch, X11/Wayland)
    - Unified TTS with automatic fallbacks
    - Robust tool call parsing
    - Intent-based command understanding
    - Sandboxed script execution
    - Dynamic capability awareness
    """

    def __init__(self, config_file="config/config.yaml"):
        """Initialize the voice assistant."""

        # Detect platform first
        self.platform = PlatformDetector.detect()
        self.platform_adapter = PlatformAdapter()

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
        logger.info("JARVIS Voice AI Assistant v2.0 - Starting")
        logger.info("=" * 60)
        logger.info(f"Platform: {self.platform.distribution.value}")
        logger.info(f"Display: {self.platform.display_server.value}")
        logger.info(f"Audio: {self.platform.audio_system.value}")
        logger.info(f"Desktop: {self.platform.desktop_environment.value}")

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

        logger.info("JARVIS initialized successfully")

        # Show activation methods
        hotkey = self.config['hotkey']['combination']
        wake_config = self.config.get('wake_word', {})
        logger.info(f"Hotkey: {hotkey}")
        if wake_config.get('enabled', False) and self.wake_word_manager:
            logger.info("Wake word: Say 'Hey JARVIS' for hands-free activation")

    def _load_config(self, config_file):
        """Load configuration from YAML file."""
        config_path = Path(__file__).parent / config_file
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_components(self):
        """Initialize all components."""

        # Audio (with platform adaptation)
        audio_config = self.config.get('audio', {})
        self.recorder = AudioRecorder(
            sample_rate=audio_config.get('sample_rate', 16000),
            channels=audio_config.get('channels', 1),
            temp_dir=self.config['paths']['temp_audio']
        )
        self.player = AudioPlayer()

        # STT (Speech-to-Text)
        stt_config = self.config.get('stt', {})
        self.stt = WhisperEngine(
            model_name=stt_config.get('model_name', 'tiny'),
            device=stt_config.get('device', 'cpu'),
            compute_type=stt_config.get('compute_type', 'int8'),
            language=stt_config.get('language', 'en')
        )

        # Rule-based parser (fallback)
        self.parser = CommandParser()

        # LLM
        self._init_llm()

        # Actions
        self.app_controller = AppController(self.parser)
        self.system_info = SystemInfo(self.parser)

        # Tools
        self.tool_registry = ToolRegistry()
        self._register_tools()

        # Tool executor
        if self.llm_client:
            self.tool_executor = ToolExecutor(self.tool_registry)
            logger.info(f"Tool executor initialized with {len(self.tool_registry)} tools")

        # Tool parser (improved)
        self.tool_parser = ToolCallParser(
            valid_tools=set(self.tool_registry.list_tools())
        )

        # TTS (unified with fallbacks)
        tts_config = self.config.get('tts', {})
        self.tts = UnifiedTTSEngine({
            'google': {
                'lang': tts_config.get('lang', 'en'),
                'tld': tts_config.get('tld', 'com')
            }
        })
        logger.info(f"TTS initialized: {self.tts.get_status()}")

        # Capability manifest
        self.capability_manifest = get_manifest()
        logger.info(f"Capabilities: {self.capability_manifest.count_available()} available")

        # Intent registry
        self.intent_registry = create_registry_with_defaults()

        # Dynamic prompt builder
        self.prompt_builder = DynamicPromptBuilder(self.capability_manifest)

        # Sandbox for script execution
        sandbox_config = self.config.get('sandbox', {})
        self.sandbox = create_sandbox(sandbox_config)

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

    def _init_llm(self):
        """Initialize LLM client."""
        llm_config = self.config.get('llm', {})
        self.llm_client = None
        self.router = None

        if llm_config.get('enabled', True):
            try:
                self.llm_client = OllamaClient(
                    base_url=llm_config.get('base_url', 'http://localhost:11434'),
                    model=llm_config.get('model', 'qwen3:4b'),
                    timeout=llm_config.get('timeout', 60)
                )

                if self.llm_client.check_connection():
                    if not self.llm_client.check_model_available():
                        model = llm_config.get('model')
                        logger.warning(f"Model {model} not found. Run: ollama pull {model}")
                    else:
                        logger.info(f"LLM ready: {llm_config.get('model')}")
                else:
                    logger.warning("Ollama not running. Start with: ollama serve")

                self.router = SmartRouter(self.llm_client, self.parser, self.config)
                logger.info("Smart router initialized (hybrid mode)")

            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                logger.info("Falling back to rule-based mode")
        else:
            logger.info("LLM disabled in config")

    def _register_tools(self):
        """Register all built-in tools."""
        from tools.builtin import (
            GenerateAndRunScriptTool,
            MediaControlTool, GetNowPlayingTool,
            AnswerQuestionTool, ExplainConceptTool, HaveConversationTool,
            SetUserPreferenceTool, RememberUserInfoTool, SetWorkContextTool,
            BrightnessControlTool, PowerManagementTool, SystemVolumeTool,
            OpenWebsiteTool, WebSearchTool
        )

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
            # AI Script Generation
            GenerateAndRunScriptTool(),
            # Media Control
            MediaControlTool(),
            GetNowPlayingTool(),
            # Conversation & Knowledge
            AnswerQuestionTool(),
            ExplainConceptTool(),
            HaveConversationTool(),
            # User Context
            SetUserPreferenceTool(),
            RememberUserInfoTool(),
            SetWorkContextTool(),
            # System Control
            BrightnessControlTool(),
            PowerManagementTool(),
            SystemVolumeTool(),
            # Web Navigation
            OpenWebsiteTool(),
            WebSearchTool(),
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

        print(f'📝 You said: "{text}"')

        # Filter garbage transcriptions
        clean_text = text.strip().replace('.', '').replace(',', '')
        if len(clean_text) < 2 or (clean_text.replace(' ', '').isdigit() and len(clean_text) < 5):
            logger.warning(f"Ignored garbage transcription: '{text}'")
            print("🚫 Ignored (noise/hallucination)")
            return

        # 3. Process command
        response_text = self._process_command(text)

        if response_text:
            print(f"💬 Response: {response_text}")
            # 4. Speak response
            self._speak(response_text)

        # Return to idle
        self.ui.set_idle()

        # Cleanup
        self.recorder.cleanup_old_recordings(keep_last=5)

    def _process_command(self, text: str) -> str:
        """Process a command and return response text."""

        # Route command
        if self.router:
            processor_type, data = self.router.route(text)
            print(f"🧠 Using: {processor_type.upper()}")
        else:
            processor_type = 'rules'
            data = self.parser.parse(text)

        # Process based on route
        if processor_type == 'llm':
            return self._process_with_llm(data['text'], data.get('context'))
        else:
            return self._process_with_rules(data)

    def _process_with_rules(self, intent) -> str:
        """Process with rule-based parser."""
        if not intent or intent['intent'] == 'unknown':
            logger.warning("Unknown command")
            return get_error_response('unknown_command', self.parser)

        print(f"⚙️  Executing: {intent['intent']} - {intent['target']}")
        result = self._execute_action(intent)
        return generate_response(result, self.parser)

    def _process_with_llm(self, text: str, context=None) -> str:
        """Process command using LLM with improved tool calling."""
        try:
            # Check for simple greetings first (handle locally for speed)
            greeting_response = self._check_greeting(text)
            if greeting_response:
                return greeting_response

            # Use chat API for better qwen3 compatibility
            logger.info("Generating LLM response via chat API...")

            # Build messages for chat API
            messages = [
                {
                    'role': 'system',
                    'content': self._get_tool_calling_prompt()
                },
                {
                    'role': 'user',
                    'content': text
                }
            ]

            result = self.llm_client.chat(
                messages=messages,
                temperature=0.1  # Low for reliable tool calls
            )

            if not result.get('success'):
                logger.error(f"LLM error: {result.get('error')}")
                return "I encountered an error. Please try again."

            response = result.get('response', '').strip()

            # Check for invalid template responses
            if response in ['TOOL: name(param="value")', 'TOOL:', '']:
                logger.warning(f"LLM returned invalid response: {repr(response)}")
                # Try to infer the action from the text
                return self._infer_action(text)

            # Parse tool calls with improved parser
            tool_calls = self.tool_parser.parse(response)

            if tool_calls and self.tool_executor:
                return self._execute_tools(text, tool_calls)

            # Check for direct response
            direct_response = self.tool_parser.extract_direct_response(response)
            if direct_response:
                return direct_response

            # Fallback
            return response

        except Exception as e:
            logger.error(f"LLM processing failed: {e}", exc_info=True)
            return "I encountered an error. Please try again."

    def _execute_tools(self, user_text: str, tool_calls: list) -> str:
        """Execute tool calls and generate response."""
        results = []
        is_conversation = False

        conversation_tools = {'answer_question', 'explain_concept', 'have_conversation'}

        for call in tool_calls:
            tool_name = call.name
            tool_params = call.params

            logger.info(f"Executing tool: {tool_name} with params: {tool_params}")

            # Check if this is a conversation tool
            if tool_name in conversation_tools:
                is_conversation = True

            # Execute the tool
            tool_result = self.tool_executor.execute(tool_name, tool_params)
            results.append(tool_result)

            # Format result
            result_str = self.tool_executor.format_result_for_llm(tool_result)
            logger.debug(f"Tool result: {result_str}")

        # Generate summary response
        return self._generate_summary(user_text, results, is_conversation)

    def _generate_summary(self, user_text: str, results: list, is_conversation: bool) -> str:
        """Generate natural language summary of tool results."""

        # Build prompt for summary
        summary_prompt = self.prompt_builder.build_result_prompt(
            user_text, results, is_conversation
        )

        # Determine settings based on type
        if is_conversation:
            temperature = 0.7
            max_tokens = 300
        else:
            temperature = 0.3
            max_tokens = 100

        # Get LLM summary
        final_result = self.llm_client.generate(
            prompt=summary_prompt,
            system="Provide a brief, natural response.",
            temperature=temperature,
            max_tokens=max_tokens
        )

        if final_result.get('success'):
            response = final_result.get('response', '')

            # Clean thinking tags
            import re
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()

            if response:
                return response

        # Fallback to generic summary
        return self._generate_fallback_summary(results)

    def _generate_fallback_summary(self, results: list) -> str:
        """Generate fallback summary when LLM fails."""
        if not results:
            return "I completed the task."

        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]

        if not successful:
            return "I encountered an error completing that task."

        tool_names = [r.get('tool', 'task') for r in successful]

        if len(tool_names) == 1:
            return f"I've completed the {tool_names[0].replace('_', ' ')} task."
        else:
            return f"I've completed {len(tool_names)} tasks."

    def _check_greeting(self, text: str) -> str:
        """Handle greetings locally for speed."""
        text_lower = text.lower().strip()

        greetings = {
            'hello': "Hello! How can I help you today?",
            'hi': "Hi there! What can I do for you?",
            'hey': "Hey! How can I assist you?",
            'hey jarvis': "Yes? How can I help?",
            'good morning': "Good morning! How can I help you today?",
            'good afternoon': "Good afternoon! What can I do for you?",
            'good evening': "Good evening! How may I assist you?",
            'how are you': "I'm doing great, thank you for asking! How can I help you?",
            'thank you': "You're welcome! Is there anything else I can help with?",
            'thanks': "You're welcome! Anything else?",
        }

        for greeting, response in greetings.items():
            if text_lower == greeting or text_lower.startswith(greeting + ' '):
                return response

        return None

    def _get_tool_calling_prompt(self) -> str:
        """Get compact prompt for tool calling."""
        return """You are JARVIS, a Linux voice assistant. Respond with TOOL calls.

FORMAT: TOOL: tool_name(param="value", number=50)

TOOLS:
- open_app(app_name="firefox") - Open applications
- close_app(app_name="chrome") - Close applications
- get_system_info(info_type="cpu") - CPU/memory/disk info (types: cpu, memory, disk)
- control_brightness(action="set", value=80) - Screen brightness (0-100)
- control_system_volume(action="set", value=50) - Volume (0-100, actions: set/increase/decrease/mute)
- control_media(action="play") - Media control (actions: play/pause/next/previous)
- open_website(website="youtube") - Open websites (google/gmail/youtube/github)
- search_web(query="python tutorial") - Web search
- run_script(script="ls -la") - Run shell commands
- list_files(path=".", pattern="*.py") - List files

EXAMPLES:
"open firefox" → TOOL: open_app(app_name="firefox")
"open brave" → TOOL: open_app(app_name="brave-browser")
"CPU usage" → TOOL: get_system_info(info_type="cpu")
"brightness 80" → TOOL: control_brightness(action="set", value=80)
"volume 50" → TOOL: control_system_volume(action="set", value=50)
"reduce volume to 20" → TOOL: control_system_volume(action="set", value=20)
"open google" → TOOL: open_website(website="google")
"open terminal" → TOOL: open_app(app_name="gnome-terminal")
"play music" → TOOL: control_media(action="play")
"pause" → TOOL: control_media(action="pause")

OUTPUT ONLY THE TOOL CALL. No explanations."""

    def _infer_action(self, text: str) -> str:
        """Infer action from text when LLM fails."""
        text_lower = text.lower()

        # Try to match common patterns
        if 'open' in text_lower:
            # Extract app name
            words = text_lower.replace('open', '').strip().split()
            if words:
                app = words[0]
                # Map common names
                app_map = {
                    'google': 'google-chrome',
                    'chrome': 'google-chrome',
                    'brave': 'brave-browser',
                    'terminal': 'gnome-terminal',
                    'files': 'nautilus',
                    'code': 'code',
                    'vscode': 'code',
                }
                app_name = app_map.get(app, app)
                # Execute directly
                result = self.tool_executor.execute('open_app', {'app_name': app_name})
                if result.get('success'):
                    return f"Opening {app}."
                return f"I couldn't open {app}."

        if 'cpu' in text_lower or 'memory' in text_lower or 'ram' in text_lower:
            info_type = 'memory' if ('memory' in text_lower or 'ram' in text_lower) else 'cpu'
            result = self.tool_executor.execute('get_system_info', {'info_type': info_type})
            if result.get('success'):
                return self._format_system_info(result.get('result', {}))

        if 'volume' in text_lower:
            # Extract number
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                value = int(numbers[0])
                result = self.tool_executor.execute('control_system_volume', {'action': 'set', 'value': value})
                if result.get('success'):
                    return f"Volume set to {value}%."

        if 'brightness' in text_lower:
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                value = int(numbers[0])
                result = self.tool_executor.execute('control_brightness', {'action': 'set', 'value': value})
                if result.get('success'):
                    return f"Brightness set to {value}%."

        return "I couldn't understand that command. Could you rephrase?"

    def _format_system_info(self, data: dict) -> str:
        """Format system info for speech."""
        parts = []
        if 'cpu' in data:
            cpu = data['cpu']
            parts.append(f"CPU usage is at {cpu.get('usage_percent', 0):.0f}%")
        if 'memory' in data:
            mem = data['memory']
            parts.append(f"Memory is {mem.get('percent', 0):.0f}% used")
        if 'disk' in data:
            disk = data['disk']
            parts.append(f"Disk has {disk.get('free_gb', 0):.1f} GB free")
        return ". ".join(parts) if parts else "System information retrieved."

    def _execute_action(self, intent):
        """Execute action based on intent."""
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

    def _speak(self, text: str):
        """Speak text using TTS with fallback support."""
        if not text:
            return

        print("🔊 Speaking...")

        # Use unified TTS engine
        audio_file = self.tts.speak(text)

        if audio_file:
            # Pause wake word during playback
            if self.wake_word_manager:
                self.wake_word_manager.pause()

            try:
                self.player.play_file(audio_file)
            finally:
                # Resume wake word
                if self.wake_word_manager:
                    import time
                    time.sleep(0.3)
                    self.wake_word_manager.resume()
        else:
            logger.error("TTS synthesis failed (all backends)")

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
        print("🎙️  JARVIS Voice AI Assistant v2.0")
        print("=" * 60)

        # Show platform info
        print(f"📍 Platform: {self.platform.distribution.value} / {self.platform.display_server.value}")

        # Show LLM status
        if self.llm_client and self.llm_client.check_connection():
            model = self.config.get('llm', {}).get('model', 'unknown')
            print(f"🧠 LLM: {model} (Hybrid Mode)")
        else:
            print("⚙️  Mode: Rule-based only (LLM unavailable)")

        # Show capabilities
        print(f"🔧 Capabilities: {self.capability_manifest.count_available()} available")

        # Activation methods
        print(f"\nPress {self.config['hotkey']['combination'].upper()} to speak")

        # Start wake word if available
        if self.wake_word_manager and self.wake_word_manager.is_available():
            if self.wake_word_manager.start():
                self.wake_word_active = True
                print("🗣️  Or say 'Hey JARVIS' for hands-free activation")

        print("Press Ctrl+C to exit\n")

        # Check hotkey support
        if not self.platform_adapter.can_use_global_hotkeys():
            print("⚠️  Warning: Global hotkeys may not work on pure Wayland.")
            print("   Consider using XWayland or wake word activation.")

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

        # Stop wake word
        if self.wake_word_manager:
            self.wake_word_manager.stop()
            self.wake_word_active = False

        # Stop UI
        if self.ui:
            self.ui.stop()

        # Cleanup sandbox
        if self.sandbox:
            self.sandbox.cleanup()

        # Cleanup TTS cache
        if self.tts:
            self.tts.cleanup_old_files(max_age_hours=1)

        print("\n👋 Goodbye!")
        sys.exit(0)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n👋 Shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    signal.signal(signal.SIGINT, signal_handler)

    try:
        assistant = JarvisAssistant()
        assistant.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

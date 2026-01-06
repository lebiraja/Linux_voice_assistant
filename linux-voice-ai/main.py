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
            # System Control (New)
            BrightnessControlTool(),
            PowerManagementTool(),
            SystemVolumeTool(),
            # Web Navigation (New)
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
        
        print(f"📝 You said: \"{text}\"")
        
        # Filter garbage transcriptions (short text or just numbers)
        clean_text = text.strip().replace('.', '').replace(',', '')
        if len(clean_text) < 2 or (clean_text.replace(' ', '').isdigit() and len(clean_text) < 5):
            logger.warning(f"Ignored garbage transcription: '{text}'")
            print("🚫 Ignored (noise/hallucination)")
            return
        
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
        """
        try:
            # Build system prompt with tool calling instructions
            tool_schemas = self.tool_registry.get_all_schemas() if self.tool_executor else []
            system_prompt = f"""{SystemPrompts.ASSISTANT_SYSTEM_PROMPT}

{SystemPrompts.TOOL_CALLING_PROMPT}"""
            
            # Generate LLM response
            logger.info("LLM requested tool usage (text-based)")
            result = self.llm_client.generate(
                prompt=text,
                system=system_prompt,
                temperature=0.3,
                max_tokens=256  # Reduced for faster tool calls
            )
            
            # Handle errors
            if not result.get('success'):
                error_type = result.get('error', 'unknown')
                logger.error(f"LLM error: {result.get('message', 'Unknown error')}")
                
                if error_type == 'timeout':
                    return "I'm thinking too slowly. Let me try the quick route."
                else:
                    return "I encountered an error. Please try again."
            
            response = result.get('response', '').strip()
            
            # Handle empty response
            if not response:
                logger.warning("LLM returned empty response")
                return "I didn't quite catch that. Could you rephrase?"
            
            # Check if LLM wants to use tools (text-based format)
            if 'TOOL:' in response and self.tool_executor:
                logger.info("LLM requested tool usage (text-based)")
                
                # Parse tool calls from response (returns list)
                tool_calls = self._parse_tool_calls(response)
                
                if tool_calls:
                    full_result_text = []
                    
                    # Execute all parsed tools sequentially
                    for call in tool_calls:
                        tool_name = call['name']
                        tool_params = call['params']
                        
                        logger.info(f"Executing tool: {tool_name} with params: {tool_params}")
                        
                        # Execute the tool
                        tool_result = self.tool_executor.execute(tool_name, tool_params)
                        
                        # Format result clearly
                        result_str = self.tool_executor.format_result_for_llm(tool_result)
                        full_result_text.append(f"Tool '{tool_name}' output:\n{result_str}")
                    
                    combined_results = "\n\n".join(full_result_text)
                    logger.debug(f"Combined tool results: {combined_results}")
                    
                    # Determine response style based on tool types
                    conversation_tools = {'answer_question', 'explain_concept', 'have_conversation'}
                    is_conversation = any(call['name'] in conversation_tools for call in tool_calls)
                    
                    # Get final response from LLM with tool results
                    if is_conversation:
                        # Detailed response for questions/conversation
                        final_prompt = f"""User asked: "{text}"

Tool results:
{combined_results}

Provide a natural, informative response using the above information. Be conversational and helpful."""
                        temperature = 0.7
                        max_tokens = 300
                        system_msg = "You are JARVIS, a helpful AI assistant. Provide informative, natural responses."
                    else:
                        # Concise response for commands/actions
                        final_prompt = f"""I asked: "{text}"

Results:
{combined_results}

Confirm what was done in 1-2 sentences (will be spoken aloud)."""
                        temperature = 0.3
                        max_tokens = 100
                        system_msg = "You are JARVIS. Confirm actions briefly using the provided data."
                    
                    final_result = self.llm_client.generate(
                        prompt=final_prompt,
                        system=system_msg,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    if final_result.get('success'):
                        final_response = final_result.get('response', '')
                        
                        # Clean final response of any <think> blocks
                        import re
                        final_response = re.sub(r'<think>.*?</think>', '', final_response, flags=re.DOTALL).strip()
                        
                        # If empty after cleaning, use fallback
                        if not final_response:
                            # Generate dynamic summary of actions
                            action_summary = self._generate_action_summary(tool_calls)
                            return action_summary
                            
                        # If LLM still refuses, provide direct answer from data
                        if any(word in final_response.lower() for word in ['cannot', 'unable', 'sorry', "don't have"]):
                            # Fallback: just return the last tool's success message roughly
                            return "I completed the requested actions."
                            
                        return final_response
                    else:
                        # LLM failed, return generic success
                        return "Actions completed successfully."
            
            # No tools needed or tool execution failed, return direct response
            return response
                
        except Exception as e:
            logger.error(f"LLM processing failed: {e}", exc_info=True)
            return "I encountered an error. Please try again."
            
    def _generate_action_summary(self, tool_calls: list) -> str:
        """Generate a natural language summary of executed actions."""
        if not tool_calls:
            return "I completed the task."
            
        actions = []
        for call in tool_calls:
            name = call['name']
            params = call['params']
            
            if name == 'open_app':
                app = params.get('app_name', 'application')
                actions.append(f"opened {app}")
            elif name == 'close_app':
                app = params.get('app_name', 'application')
                actions.append(f"closed {app}")
            elif name == 'run_script':
                actions.append("ran a script")
            elif name == 'list_files':
                actions.append("listed files")
            elif name == 'get_system_info':
                actions.append("checked system info")
            else:
                actions.append(f"used {name}")
        
        if len(actions) == 1:
            return f"I have {actions[0]}."
        elif len(actions) == 2:
            return f"I have {actions[0]} and {actions[1]}."
        else:
            # Join with commas and 'and'
            return f"I have {', '.join(actions[:-1])}, and {actions[-1]}."
    
    def _parse_tool_calls(self, response: str) -> list:
        """Parse multiple tool calls from LLM text response."""
        import re
        
        VALID_TOOLS = {
            # App control
            'open_app', 'close_app', 'run_script',
            # System
            'get_system_info', 'get_processes', 'execute_command',
            # Filesystem
            'list_files', 'read_file', 'search_files',
            # Web
            'search_web', 'fetch_url',
            # Script generation
            'generate_and_run_script',
            # Media control
            'control_media', 'get_now_playing',
            # Conversation
            'answer_question', 'explain_concept', 'have_conversation',
            # User context
            'set_user_preference', 'remember_user_info', 'set_work_context',
            # System Control
            'control_brightness', 'power_management', 'control_system_volume',
            # Web Navigation
            'open_website', 'web_search',
        }
        
        tool_calls = []
        
        try:
            # Clean response: remove <think>...</think> blocks from reasoning models
            cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            
            # Find all TOOL: patterns
            # Regex captures: 1=tool_name, 2=params_str
            for match in re.finditer(r'TOOL:\s*([\w_]+)\(([^)]*)\)', cleaned_response):
                tool_name = match.group(1)
                params_str = match.group(2)
                
                # Validate tool name
                if tool_name not in VALID_TOOLS:
                    logger.warning(f"Invalid tool skipped: {tool_name}")
                    continue
                
                # Parse parameters - handle quoted strings, numbers, booleans
                params = {}
                if params_str.strip():
                    # Try quoted strings first (double quotes)
                    for m in re.findall(r'(\w+)\s*=\s*"([^"]*)"', params_str):
                        params[m[0]] = m[1]
                    # Single quotes
                    for m in re.findall(r"(\w+)\s*=\s*'([^']*)'", params_str):
                        if m[0] not in params:  # Don't override
                            params[m[0]] = m[1]
                    # Unquoted values (numbers, booleans, etc.)
                    for m in re.findall(r'(\w+)\s*=\s*([^,\s)]+)', params_str):
                        if m[0] not in params:  # Don't override quoted values
                            value = m[1].strip()
                            # Convert types
                            if value.lower() == 'true':
                                params[m[0]] = True
                            elif value.lower() == 'false':
                                params[m[0]] = False
                            elif value.isdigit():
                                params[m[0]] = int(value)
                            else:
                                params[m[0]] = value
                
                logger.info(f"Parsed: {tool_name} params: {params}")
                tool_calls.append({'name': tool_name, 'params': params})
                
            return tool_calls
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return []
    
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
            # Pause wake word detection during playback to avoid self-triggering
            if self.wake_word_manager:
                self.wake_word_manager.pause()
            
            try:
                self.player.play_file(audio_file)
            finally:
                # Resume wake word detection after a short grace period
                if self.wake_word_manager:
                    # Small delay to let echoes die down
                    import time
                    time.sleep(0.3)
                    self.wake_word_manager.resume()
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

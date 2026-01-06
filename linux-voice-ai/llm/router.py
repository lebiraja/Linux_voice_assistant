"""
Smart Router
Routes commands to either rule-based parser or LLM based on complexity
Supports both tool-calling commands and general conversation
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional, List
from .conversation_memory import ConversationMemory
from .user_context import UserContext

logger = logging.getLogger(__name__)


class SmartRouter:
    """
    Intelligent router that decides whether to use rule-based parsing or LLM.
    
    Strategy:
    1. Try rule-based parser first for speed
    2. If rule parser succeeds with high confidence, use it
    3. Otherwise, route to LLM for complex understanding
    4. Support conversational mode for general Q&A
    5. Fallback to rules if LLM fails
    """
    
    def __init__(self, llm_client, rule_parser, config: Dict):
        """
        Initialize smart router.
        
        Args:
            llm_client: OllamaClient instance
            rule_parser: CommandParser instance
            config: Configuration dict
        """
        self.llm = llm_client
        self.rules = rule_parser
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize conversation memory
        self.conversation = ConversationMemory(
            max_history=config.get('conversation', {}).get('max_history', 10)
        )
        
        # Initialize user context
        context_file = config.get('conversation', {}).get('context_file', 'user_context.json')
        self.user_context = UserContext(context_file)
        
        # Simple command patterns (regex)
        self.simple_patterns = [
            r"^(open|launch|start|run)\s+\w+$",
            r"^(close|quit|stop|kill|exit)\s+\w+$",
            r"^(what'?s?|show|tell|get)\s+(my\s+)?(cpu|processor|ram|memory|disk|storage|space)\s*(usage|info)?$",
        ]
        
        # LLM is enabled by default, can be disabled in config
        self.llm_enabled = config.get('llm', {}).get('enabled', True)
        self.fallback_to_rules = config.get('llm', {}).get('fallback_to_rules', True)
        self.conversation_mode = config.get('conversation', {}).get('enabled', True)
    
    def route(self, text: str, context: Optional[str] = None) -> Tuple[str, Any]:
        """
        Route command to appropriate processor.
        
        Args:
            text: User command text
            context: Optional conversation context (if None, uses memory)
            
        Returns:
            Tuple of (processor_type, result)
            - processor_type: 'rules' or 'llm'
            - result: Parsed intent dict or LLM response
        """
        if not text:
            return ('rules', None)
        
        text = text.strip()
        self.logger.info(f"Routing command: '{text}'")
        
        # Step 1: Check if it's a simple command
        if self._is_simple_command(text):
            self.logger.debug("Detected simple command pattern")
            result = self.rules.parse(text)
            
            # If rule parser succeeded, use it
            if result and result.get('intent') != 'unknown':
                # CHECK: If intent is found but target is missing for app commands, fallback to LLM
                # This handles "Open Brave" where "Brave" isn't in commands.yaml
                if result.get('intent') in ['open_app', 'close_app'] and not result.get('target'):
                    self.logger.info(f"Rule parser found intent {result['intent']} but no target. Fallback to LLM.")
                else:
                    self.logger.info(f"Using rule-based parser: {result['intent']}")
                    return ('rules', result)
        
        # Step 2: Try LLM if enabled
        if self.llm_enabled:
            # Check if LLM is available
            if not self.llm.check_connection():
                self.logger.warning("LLM not available, falling back to rules")
                return ('rules', self.rules.parse(text))
            
            self.logger.info("Routing to LLM for complex understanding")
            return ('llm', {'text': text, 'context': context})
        
        # Step 3: Fallback to rules
        self.logger.info("LLM disabled, using rule-based parser")
        return ('rules', self.rules.parse(text))
    
    def _is_simple_command(self, text: str) -> bool:
        """
        Check if command matches simple patterns.
        
        Args:
            text: Command text
            
        Returns:
            bool: True if simple command
        """
        text_lower = text.lower().strip()
        
        # Check against regex patterns
        for pattern in self.simple_patterns:
            if re.match(pattern, text_lower):
                return True
        
        # Check word count (simple commands are usually short)
        word_count = len(text_lower.split())
        if word_count <= 3:
            # Additional check: contains action keyword
            action_keywords = ['open', 'close', 'launch', 'quit', 'stop', 'kill', 
                             'start', 'run', 'exit', 'cpu', 'ram', 'disk', 'memory']
            if any(keyword in text_lower for keyword in action_keywords):
                return True
        
        return False
    
    def should_use_llm(self, text: str, rule_result: Optional[Dict] = None) -> bool:
        """
        Determine if LLM should be used for this command.
        
        Args:
            text: Command text
            rule_result: Result from rule parser (if already tried)
            
        Returns:
            bool: True if LLM should be used
        """
        # Don't use LLM if disabled
        if not self.llm_enabled:
            return False
        
        # Don't use LLM if not available
        if not self.llm.check_connection():
            return False
        
        # Use LLM if rule parser failed
        if rule_result and rule_result.get('intent') == 'unknown':
            return True
        
        # Use LLM for complex commands
        if not self._is_simple_command(text):
            return True
        
        # Use LLM for questions
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'can', 'could', 'would']
        if any(text.lower().startswith(word) for word in question_words):
            return True
        
        return False    
    def is_conversational(self, text: str) -> bool:
        """
        Check if input is conversational (not a command).
        
        Args:
            text: User input
            
        Returns:
            bool: True if conversational
        """
        text_lower = text.lower().strip()
        
        # Greetings
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 
                     'good evening', "what's up", 'how are you']
        if any(greeting in text_lower for greeting in greetings):
            return True
        
        # Questions (general knowledge, not system commands)
        question_starters = [
            'what is', 'what are', 'what does', "what's",
            'how does', 'how do', 'how can',
            'why is', 'why are', 'why does',
            'when was', 'when is', 'when did',
            'who is', 'who was', 'who are',
            'tell me about', 'explain',
            'can you tell', 'do you know'
        ]
        if any(text_lower.startswith(q) for q in question_starters):
            # Exclude system commands like "what's my CPU usage"
            system_keywords = ['cpu', 'memory', 'ram', 'disk', 'storage', 'process']
            if not any(kw in text_lower for kw in system_keywords):
                return True
        
        # Thank you / feedback
        feedback = ['thank', 'thanks', 'appreciate', 'good job', 'well done',
                   'nice', 'great', 'awesome', 'perfect']
        if any(fb in text_lower for fb in feedback):
            return True
        
        return False
    
    def add_to_memory(self, user_input: str, response: str, metadata: Optional[Dict] = None):
        """Add exchange to conversation memory"""
        if self.conversation_mode:
            self.conversation.add_exchange(user_input, response, metadata)
    
    def get_conversation_context(self, num_exchanges: int = 5) -> str:
        """Get recent conversation context"""
        return self.conversation.get_context(num_exchanges)
    
    def clear_conversation(self):
        """Clear conversation memory"""
        self.conversation.clear()
    
    def get_user_context_summary(self) -> str:
        """Get formatted user context for prompts"""
        return self.user_context.get_context_summary()
    
    def update_user_context(self, user_input: str, metadata: Optional[Dict] = None):
        """Update user context based on interaction"""
        self.user_context.learn_from_interaction(user_input, metadata)
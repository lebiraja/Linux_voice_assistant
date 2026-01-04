"""
Smart Router
Routes commands to either rule-based parser or LLM based on complexity
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class SmartRouter:
    """
    Intelligent router that decides whether to use rule-based parsing or LLM.
    
    Strategy:
    1. Try rule-based parser first for speed
    2. If rule parser succeeds with high confidence, use it
    3. Otherwise, route to LLM for complex understanding
    4. Fallback to rules if LLM fails
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
        
        # Simple command patterns (regex)
        self.simple_patterns = [
            r"^(open|launch|start|run)\s+\w+$",
            r"^(close|quit|stop|kill|exit)\s+\w+$",
            r"^(what'?s?|show|tell|get)\s+(my\s+)?(cpu|processor|ram|memory|disk|storage|space)\s*(usage|info)?$",
        ]
        
        # LLM is enabled by default, can be disabled in config
        self.llm_enabled = config.get('llm', {}).get('enabled', True)
        self.fallback_to_rules = config.get('llm', {}).get('fallback_to_rules', True)
    
    def route(self, text: str, context: Optional[str] = None) -> Tuple[str, Any]:
        """
        Route command to appropriate processor.
        
        Args:
            text: User command text
            context: Optional conversation context
            
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

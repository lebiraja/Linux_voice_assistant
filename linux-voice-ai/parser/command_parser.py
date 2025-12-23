"""Command parser for understanding user intent."""

import yaml
import logging
from pathlib import Path
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class CommandParser:
    """Parse natural language commands into structured intents."""
    
    def __init__(self, commands_file="config/commands.yaml"):
        """
        Initialize command parser.
        
        Args:
            commands_file: Path to commands configuration file
        """
        self.commands_file = Path(commands_file)
        self.config = None
        self.intents = {}
        self.applications = {}
        self.responses = {}
        
        self._load_config()
    
    def _load_config(self):
        """Load command configuration from YAML file."""
        try:
            with open(self.commands_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.intents = self.config.get('intents', {})
            self.applications = self.config.get('applications', {})
            self.responses = self.config.get('responses', {})
            
            logger.info(f"Loaded command config from {self.commands_file}")
            logger.debug(f"Intents: {list(self.intents.keys())}")
            logger.debug(f"Applications: {list(self.applications.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading command config: {e}")
            raise
    
    def parse(self, text):
        """
        Parse text into structured intent.
        
        Args:
            text: Input text from STT
            
        Returns:
            dict: Parsed intent with 'intent', 'target', and 'confidence'
        """
        if not text:
            return None
        
        text = text.lower().strip()
        logger.info(f"Parsing command: '{text}'")
        
        # Detect intent
        intent = self._detect_intent(text)
        
        if not intent:
            logger.warning("No intent detected")
            return {
                'intent': 'unknown',
                'target': None,
                'confidence': 0.0,
                'original_text': text
            }
        
        # Extract target based on intent
        target = None
        if intent in ['open_app', 'close_app']:
            target = self._extract_app_name(text)
        elif intent == 'system_info':
            target = self._extract_system_query(text)
        
        result = {
            'intent': intent,
            'target': target,
            'confidence': 0.8,  # Simple confidence for now
            'original_text': text
        }
        
        logger.info(f"Parsed intent: {result}")
        return result
    
    def _detect_intent(self, text):
        """
        Detect the intent from text.
        
        Args:
            text: Input text
            
        Returns:
            str: Intent name or None
        """
        for intent_name, intent_config in self.intents.items():
            keywords = intent_config.get('keywords', [])
            for keyword in keywords:
                if keyword in text:
                    return intent_name
        
        return None
    
    def _extract_app_name(self, text):
        """
        Extract application name from text using fuzzy matching.
        
        Args:
            text: Input text
            
        Returns:
            str: Application name or None
        """
        best_match = None
        best_score = 0.0
        
        # Build list of all possible app names and synonyms
        app_choices = {}
        for app_name, app_config in self.applications.items():
            # Add app name itself
            app_choices[app_name] = app_name
            
            # Add all synonyms
            synonyms = app_config.get('synonyms', [])
            for synonym in synonyms:
                app_choices[synonym] = app_name
        
        # Try exact substring match first
        for choice, app_name in app_choices.items():
            if choice in text:
                logger.debug(f"Exact match found: {choice} → {app_name}")
                return app_name
        
        # Extract potential app name from text (word after "open"/"launch"/"close")
        words = text.split()
        potential_app = None
        for i, word in enumerate(words):
            if word in ['open', 'launch', 'start', 'run', 'close', 'quit', 'stop', 'kill']:
                if i + 1 < len(words):
                    potential_app = words[i + 1]
                    break
        
        if not potential_app:
            # Try last word as fallback
            potential_app = words[-1] if words else text
        
        # Fuzzy match the potential app name
        if potential_app:
            match = process.extractOne(
                potential_app,
                app_choices.keys(),
                scorer=fuzz.ratio,
                score_cutoff=75  # 75% similarity threshold
            )
            
            if match:
                matched_choice, score, _ = match
                app_name = app_choices[matched_choice]
                logger.info(f"Fuzzy match: '{potential_app}' → '{matched_choice}' ({score}%) → {app_name}")
                return app_name
        
        logger.debug(f"No app match found for: {text}")
        return None
    
    def _extract_system_query(self, text):
        """
        Extract system query type from text.
        
        Args:
            text: Input text
            
        Returns:
            str: Query type (cpu, ram, disk)
        """
        if any(word in text for word in ['cpu', 'processor']):
            return 'cpu'
        elif any(word in text for word in ['ram', 'memory']):
            return 'ram'
        elif any(word in text for word in ['disk', 'storage', 'space']):
            return 'disk'
        
        return 'cpu'  # Default
    
    def get_response_template(self, category, key):
        """
        Get response template.
        
        Args:
            category: Response category (success, error, system_info)
            key: Response key
            
        Returns:
            str: Response template
        """
        try:
            return self.responses[category][key]
        except KeyError:
            return "Operation completed."
    
    def get_app_executables(self, app_name):
        """
        Get list of possible executables for an application.
        
        Args:
            app_name: Application name
            
        Returns:
            list: List of executable names
        """
        if app_name in self.applications:
            return self.applications[app_name].get('executables', [])
        return []

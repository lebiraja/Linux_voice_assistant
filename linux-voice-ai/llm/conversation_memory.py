"""
Conversation memory manager for maintaining context across interactions
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history and context.
    Stores recent exchanges to provide context-aware responses.
    """
    
    def __init__(self, max_history: int = 10, max_tokens: int = 1000):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of exchanges to keep
            max_tokens: Approximate max tokens for context (rough estimate)
        """
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
    
    def add_exchange(self, user_input: str, assistant_response: str, 
                     metadata: Optional[Dict] = None):
        """
        Add a conversation exchange to memory.
        
        Args:
            user_input: What the user said
            assistant_response: JARVIS's response
            metadata: Optional metadata (intent, tools used, etc.)
        """
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "metadata": metadata or {}
        }
        
        self.history.append(exchange)
        
        # Trim if exceeds max history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        self.logger.debug(f"Added exchange to memory (total: {len(self.history)})")
    
    def get_context(self, num_exchanges: int = 5) -> str:
        """
        Get formatted conversation context.
        
        Args:
            num_exchanges: Number of recent exchanges to include
            
        Returns:
            str: Formatted context string
        """
        if not self.history:
            return ""
        
        recent = self.history[-num_exchanges:]
        
        context_parts = []
        for exchange in recent:
            context_parts.append(f"User: {exchange['user']}")
            context_parts.append(f"Assistant: {exchange['assistant']}")
        
        return "\n".join(context_parts)
    
    def get_recent_topics(self, num: int = 3) -> List[str]:
        """
        Get recent conversation topics.
        
        Args:
            num: Number of recent topics
            
        Returns:
            List of topics/intents
        """
        topics = []
        for exchange in reversed(self.history[-num:]):
            metadata = exchange.get("metadata", {})
            if "intent" in metadata:
                topics.append(metadata["intent"])
            elif "action" in metadata:
                topics.append(metadata["action"])
        
        return topics
    
    def clear(self):
        """Clear conversation history"""
        self.history.clear()
        self.logger.info("Conversation memory cleared")
    
    def get_last_exchange(self) -> Optional[Dict[str, Any]]:
        """Get the most recent exchange"""
        return self.history[-1] if self.history else None
    
    def find_reference(self, text: str) -> Optional[str]:
        """
        Try to resolve references like "it", "that", "this" from context.
        
        Args:
            text: User's current input
            
        Returns:
            str: Resolved reference or None
        """
        if not self.history:
            return None
        
        # Simple reference detection
        references = ["it", "that", "this", "them", "those", "the same"]
        text_lower = text.lower()
        
        if any(ref in text_lower for ref in references):
            # Look in last exchange for nouns/entities
            last = self.history[-1]
            
            # Extract target from metadata if available
            metadata = last.get("metadata", {})
            if "target" in metadata:
                return metadata["target"]
            
            # Extract from user input (simple noun extraction)
            words = last["user"].split()
            for i, word in enumerate(words):
                if word.lower() in ["open", "close", "play", "pause", "about", "for"]:
                    if i + 1 < len(words):
                        return words[i + 1]
        
        return None
    
    def __len__(self) -> int:
        """Get number of exchanges in memory"""
        return len(self.history)
    
    def __str__(self) -> str:
        """String representation"""
        return f"ConversationMemory({len(self.history)} exchanges)"

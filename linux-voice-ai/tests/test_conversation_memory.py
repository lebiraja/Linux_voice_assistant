#!/usr/bin/env python3
"""
Tests for conversation memory
"""

import pytest
from llm.conversation_memory import ConversationMemory


class TestConversationMemory:
    """Test ConversationMemory"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.memory = ConversationMemory(max_history=5)
    
    def test_initialization(self):
        """Test memory initialization"""
        assert len(self.memory) == 0
        assert self.memory.max_history == 5
    
    def test_add_single_exchange(self):
        """Test adding a single exchange"""
        self.memory.add_exchange(
            user_input="What is Docker?",
            assistant_response="Docker is a containerization platform..."
        )
        
        assert len(self.memory) == 1
    
    def test_add_multiple_exchanges(self):
        """Test adding multiple exchanges"""
        exchanges = [
            ("Hello", "Hi there!"),
            ("What is Python?", "Python is a programming language..."),
            ("How do I install it?", "You can install Python...")
        ]
        
        for user, assistant in exchanges:
            self.memory.add_exchange(user, assistant)
        
        assert len(self.memory) == 3
    
    def test_max_history_limit(self):
        """Test that history is limited to max_history"""
        # Add 10 exchanges to memory with max_history=5
        for i in range(10):
            self.memory.add_exchange(
                f"Question {i}",
                f"Answer {i}"
            )
        
        # Should only keep last 5
        assert len(self.memory) == 5
        
        # Check that oldest exchanges were removed
        last_exchange = self.memory.get_last_exchange()
        assert "Question 9" in last_exchange["user"]
    
    def test_get_context(self):
        """Test getting formatted context"""
        self.memory.add_exchange("Hello", "Hi!")
        self.memory.add_exchange("What is Docker?", "Docker is...")
        
        context = self.memory.get_context(num_exchanges=2)
        
        assert "User: Hello" in context
        assert "Assistant: Hi!" in context
        assert "User: What is Docker?" in context
        assert "Assistant: Docker is..." in context
    
    def test_get_context_limited(self):
        """Test getting limited context"""
        # Add 5 exchanges
        for i in range(5):
            self.memory.add_exchange(f"Q{i}", f"A{i}")
        
        # Get only last 2
        context = self.memory.get_context(num_exchanges=2)
        
        assert "Q4" in context
        assert "Q3" in context
        assert "Q0" not in context  # Older exchanges not included
    
    def test_get_recent_topics(self):
        """Test getting recent topics from metadata"""
        self.memory.add_exchange(
            "Open Firefox",
            "Opening Firefox",
            metadata={"intent": "open_app", "action": "open"}
        )
        self.memory.add_exchange(
            "What is Docker?",
            "Docker is...",
            metadata={"intent": "question", "action": "answer_question"}
        )
        
        topics = self.memory.get_recent_topics(num=2)
        
        assert "question" in topics
        assert "open_app" in topics
    
    def test_clear_memory(self):
        """Test clearing memory"""
        self.memory.add_exchange("Hello", "Hi!")
        self.memory.add_exchange("How are you?", "I'm good!")
        
        assert len(self.memory) == 2
        
        self.memory.clear()
        
        assert len(self.memory) == 0
    
    def test_get_last_exchange(self):
        """Test getting last exchange"""
        self.memory.add_exchange("First question", "First answer")
        self.memory.add_exchange("Second question", "Second answer")
        
        last = self.memory.get_last_exchange()
        
        assert last["user"] == "Second question"
        assert last["assistant"] == "Second answer"
    
    def test_get_last_exchange_empty(self):
        """Test getting last exchange when empty"""
        last = self.memory.get_last_exchange()
        assert last is None
    
    def test_find_reference_it(self):
        """Test finding reference to 'it'"""
        self.memory.add_exchange(
            "Open Firefox",
            "Opening Firefox",
            metadata={"target": "firefox"}
        )
        
        reference = self.memory.find_reference("Close it")
        
        assert reference == "firefox"
    
    def test_find_reference_that(self):
        """Test finding reference to 'that'"""
        self.memory.add_exchange(
            "Play music",
            "Playing music",
            metadata={"target": "spotify"}
        )
        
        reference = self.memory.find_reference("Pause that")
        
        assert reference == "spotify"
    
    def test_find_reference_no_context(self):
        """Test finding reference with no context"""
        reference = self.memory.find_reference("Close it")
        assert reference is None
    
    def test_exchange_with_metadata(self):
        """Test adding exchange with metadata"""
        self.memory.add_exchange(
            "What is Python?",
            "Python is a programming language...",
            metadata={
                "intent": "question",
                "topic": "programming",
                "tool_used": "answer_question"
            }
        )
        
        last = self.memory.get_last_exchange()
        
        assert last["metadata"]["intent"] == "question"
        assert last["metadata"]["topic"] == "programming"
        assert last["metadata"]["tool_used"] == "answer_question"
    
    def test_timestamp_present(self):
        """Test that timestamps are added"""
        self.memory.add_exchange("Hello", "Hi!")
        
        last = self.memory.get_last_exchange()
        
        assert "timestamp" in last
        assert last["timestamp"]  # Not empty
    
    def test_string_representation(self):
        """Test string representation"""
        self.memory.add_exchange("Q1", "A1")
        self.memory.add_exchange("Q2", "A2")
        
        str_repr = str(self.memory)
        
        assert "ConversationMemory" in str_repr
        assert "2 exchanges" in str_repr


class TestConversationMemoryEdgeCases:
    """Test edge cases for conversation memory"""
    
    def test_zero_max_history(self):
        """Test with max_history=0"""
        memory = ConversationMemory(max_history=0)
        
        memory.add_exchange("Hello", "Hi!")
        
        # Should store even with max_history=0
        # (max_history is enforced on overflow)
        assert len(memory) == 1
    
    def test_very_large_max_history(self):
        """Test with very large max_history"""
        memory = ConversationMemory(max_history=1000)
        
        for i in range(100):
            memory.add_exchange(f"Q{i}", f"A{i}")
        
        assert len(memory) == 100
    
    def test_empty_strings(self):
        """Test with empty strings"""
        memory = ConversationMemory()
        
        memory.add_exchange("", "Empty user input")
        memory.add_exchange("Empty response", "")
        
        assert len(memory) == 2
    
    def test_unicode_content(self):
        """Test with unicode characters"""
        memory = ConversationMemory()
        
        memory.add_exchange(
            "What is 你好?",
            "你好 means 'hello' in Chinese! 🎉"
        )
        
        last = memory.get_last_exchange()
        assert "你好" in last["user"]
        assert "🎉" in last["assistant"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

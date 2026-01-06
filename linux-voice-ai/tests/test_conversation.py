#!/usr/bin/env python3
"""
Tests for conversation and knowledge sharing tools
"""

import pytest
from tools.builtin.conversation import (
    AnswerQuestionTool, 
    ExplainConceptTool, 
    HaveConversationTool
)


class TestAnswerQuestionTool:
    """Test AnswerQuestionTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = AnswerQuestionTool()
    
    def test_tool_properties(self):
        """Test tool metadata"""
        assert self.tool.name == "answer_question"
        assert "answer general questions" in self.tool.description.lower()
        assert len(self.tool.parameters) >= 1
    
    def test_basic_question(self):
        """Test answering a basic question"""
        result = self.tool.execute(
            question="What is Docker?",
            topic="technology"
        )
        
        assert result["success"] is True
        assert result["question"] == "What is Docker?"
        assert result["topic"] == "technology"
        assert result["requires_llm_response"] is True
        assert result["action"] == "answer_question"
    
    def test_detailed_response_style(self):
        """Test detailed response style"""
        result = self.tool.execute(
            question="How does machine learning work?",
            response_style="detailed"
        )
        
        assert result["success"] is True
        assert result["response_style"] == "detailed"
    
    def test_concise_response_style(self):
        """Test concise response style (default)"""
        result = self.tool.execute(
            question="What is Python?"
        )
        
        assert result["success"] is True
        assert result["response_style"] == "concise"  # default
    
    def test_casual_response_style(self):
        """Test casual response style"""
        result = self.tool.execute(
            question="Tell me about Linux",
            response_style="casual"
        )
        
        assert result["success"] is True
        assert result["response_style"] == "casual"


class TestExplainConceptTool:
    """Test ExplainConceptTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = ExplainConceptTool()
    
    def test_tool_properties(self):
        """Test tool metadata"""
        assert self.tool.name == "explain_concept"
        assert "explain" in self.tool.description.lower()
        assert len(self.tool.parameters) >= 1
    
    def test_basic_explanation(self):
        """Test basic concept explanation"""
        result = self.tool.execute(
            concept="containerization"
        )
        
        assert result["success"] is True
        assert result["concept"] == "containerization"
        assert result["complexity"] == "intermediate"  # default
        assert result["requires_llm_response"] is True
        assert result["action"] == "explain_concept"
    
    def test_simple_complexity(self):
        """Test simple/beginner explanation"""
        result = self.tool.execute(
            concept="REST API",
            complexity="simple"
        )
        
        assert result["success"] is True
        assert result["complexity"] == "simple"
    
    def test_advanced_complexity(self):
        """Test advanced explanation"""
        result = self.tool.execute(
            concept="Kubernetes architecture",
            complexity="advanced"
        )
        
        assert result["success"] is True
        assert result["complexity"] == "advanced"
    
    def test_intermediate_complexity(self):
        """Test intermediate explanation (default)"""
        result = self.tool.execute(
            concept="Git branching"
        )
        
        assert result["success"] is True
        assert result["complexity"] == "intermediate"


class TestHaveConversationTool:
    """Test HaveConversationTool"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.tool = HaveConversationTool()
    
    def test_tool_properties(self):
        """Test tool metadata"""
        assert self.tool.name == "have_conversation"
        assert "conversation" in self.tool.description.lower()
        assert len(self.tool.parameters) >= 1
    
    def test_greeting_hello(self):
        """Test greeting: hello"""
        result = self.tool.execute(
            message="Hello"
        )
        
        assert result["success"] is True
        assert "direct_response" in result
        assert "Hello" in result["direct_response"]
        assert result["requires_llm_response"] is False
    
    def test_greeting_hi(self):
        """Test greeting: hi"""
        result = self.tool.execute(
            message="Hi there"
        )
        
        assert result["success"] is True
        assert "direct_response" in result
        assert result["requires_llm_response"] is False
    
    def test_greeting_good_morning(self):
        """Test greeting: good morning"""
        result = self.tool.execute(
            message="Good morning JARVIS"
        )
        
        assert result["success"] is True
        assert "direct_response" in result
        assert "morning" in result["direct_response"].lower()
    
    def test_how_are_you(self):
        """Test: how are you"""
        result = self.tool.execute(
            message="How are you?"
        )
        
        assert result["success"] is True
        assert "direct_response" in result
        assert result["conversation_type"] == "greeting"
    
    def test_general_conversation(self):
        """Test general conversation (not a greeting)"""
        result = self.tool.execute(
            message="That's really interesting",
            conversation_type="small_talk"
        )
        
        assert result["success"] is True
        assert result["conversation_type"] == "small_talk"
        # Not a simple greeting, should use LLM
        assert result["requires_llm_response"] is True
    
    def test_chat_conversation(self):
        """Test general chat"""
        result = self.tool.execute(
            message="Tell me more about that",
            conversation_type="chat"
        )
        
        assert result["success"] is True
        assert result["conversation_type"] == "chat"
        assert result["requires_llm_response"] is True
    
    def test_opinion_conversation(self):
        """Test opinion-based conversation"""
        result = self.tool.execute(
            message="What do you think about that?",
            conversation_type="opinion"
        )
        
        assert result["success"] is True
        assert result["conversation_type"] == "opinion"


class TestConversationIntegration:
    """Integration tests for conversation tools"""
    
    def test_question_answer_flow(self):
        """Test Q&A flow"""
        question_tool = AnswerQuestionTool()
        
        result = question_tool.execute(
            question="What is the Linux kernel?"
        )
        
        assert result["success"] is True
        assert result["requires_llm_response"] is True
        # In real usage, LLM would generate the actual answer
    
    def test_explanation_flow(self):
        """Test explanation flow"""
        explain_tool = ExplainConceptTool()
        
        result = explain_tool.execute(
            concept="Docker containers",
            complexity="simple"
        )
        
        assert result["success"] is True
        assert result["requires_llm_response"] is True
        # In real usage, LLM would generate explanation
    
    def test_conversation_types(self):
        """Test different conversation types"""
        conv_tool = HaveConversationTool()
        
        types = ["greeting", "small_talk", "opinion", "chat", "joke"]
        
        for conv_type in types:
            result = conv_tool.execute(
                message=f"Test {conv_type} message",
                conversation_type=conv_type
            )
            assert result["success"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

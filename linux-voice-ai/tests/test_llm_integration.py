"""
Test suite for Phase 1: LLM Integration
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import OllamaClient, SmartRouter, SystemPrompts
from parser import CommandParser


class TestOllamaClient:
    """Test Ollama client functionality"""
    
    def test_client_initialization(self):
        """Test client can be initialized"""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "functiongemma:270m"
    
    def test_connection_check(self):
        """Test connection checking"""
        client = OllamaClient()
        # This will fail if Ollama is not running, which is expected
        result = client.check_connection()
        assert isinstance(result, bool)
    
    def test_model_check(self):
        """Test model availability check"""
        client = OllamaClient()
        result = client.check_model_available()
        assert isinstance(result, bool)


class TestSmartRouter:
    """Test smart routing logic"""
    
    @pytest.fixture
    def router(self):
        """Create router instance"""
        client = OllamaClient()
        parser = CommandParser()
        config = {'llm': {'enabled': True, 'fallback_to_rules': True}}
        return SmartRouter(client, parser, config)
    
    def test_simple_command_detection(self, router):
        """Test simple command pattern matching"""
        assert router._is_simple_command("open firefox") == True
        assert router._is_simple_command("close chrome") == True
        assert router._is_simple_command("cpu usage") == True
    
    def test_complex_command_detection(self, router):
        """Test complex command detection"""
        assert router._is_simple_command("tell me about my system") == False
        assert router._is_simple_command("how many files are in my home directory") == False
    
    def test_routing_simple_command(self, router):
        """Test routing of simple commands"""
        processor, data = router.route("open firefox")
        assert processor == 'rules'
        assert data is not None
    
    def test_routing_with_llm_disabled(self):
        """Test routing when LLM is disabled"""
        client = OllamaClient()
        parser = CommandParser()
        config = {'llm': {'enabled': False}}
        router = SmartRouter(client, parser, config)
        
        processor, data = router.route("tell me about my system")
        assert processor == 'rules'


class TestSystemPrompts:
    """Test system prompts"""
    
    def test_get_system_prompt(self):
        """Test system prompt generation"""
        prompt = SystemPrompts.get_system_prompt()
        assert "JARVIS" in prompt
        assert "Linux" in prompt
    
    def test_get_system_prompt_with_tools(self):
        """Test system prompt with tools"""
        tools = [
            {"name": "test_tool", "description": "A test tool"}
        ]
        prompt = SystemPrompts.get_system_prompt(include_tools=True, tools=tools)
        assert "test_tool" in prompt
    
    def test_format_command_prompt(self):
        """Test command prompt formatting"""
        prompt = SystemPrompts.format_command_prompt("open firefox")
        assert "open firefox" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

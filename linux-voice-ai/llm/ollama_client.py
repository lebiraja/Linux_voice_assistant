"""
Ollama LLM Client
Handles communication with Ollama API for LLM inference
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama LLM API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 model: str = "functiongemma:270m",
                 timeout: int = 30):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Verify connection on init
        if not self.check_connection():
            self.logger.warning(f"Cannot connect to Ollama at {self.base_url}")
    
    def check_connection(self) -> bool:
        """
        Verify Ollama is running and accessible.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"Connection check failed: {e}")
            return False
    
    def check_model_available(self) -> bool:
        """
        Check if the configured model is available.
        
        Returns:
            bool: True if model exists, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(m.get('name', '').startswith(self.model) for m in models)
            return False
        except requests.exceptions.RequestException:
            return False
    
    def generate(self,
                 prompt: str,
                 system: Optional[str] = None,
                 tools: Optional[List[Dict]] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 512,
                 disable_thinking: bool = True) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system: System prompt (optional)
            tools: List of available tools for function calling (optional)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            disable_thinking: Disable thinking mode for qwen3 models (default True)

        Returns:
            dict: Response containing 'response' text and optional 'tool_calls'
        """
        try:
            # Build the full prompt
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\nUser: {prompt}\nAssistant:"

            # For qwen3 models, add /no_think to disable thinking mode
            # This makes the model respond directly without internal reasoning
            if disable_thinking and 'qwen3' in self.model.lower():
                full_prompt = full_prompt + " /no_think"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            # Add tools if provided (for function calling)
            if tools:
                payload["tools"] = tools

            self.logger.debug(f"Sending request to Ollama: {self.model}")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            self.logger.debug(f"Received response from Ollama")

            # Get response - also check 'thinking' field for qwen3 models
            response_text = result.get('response', '')

            # If response is empty but thinking exists, the model used thinking mode
            # In this case, we need to extract from thinking or retry
            if not response_text and result.get('thinking'):
                self.logger.debug("Model used thinking mode, response in thinking field")
                # For tool calls, we might find them in the thinking
                thinking = result.get('thinking', '')
                # Try to extract tool calls from thinking
                import re
                tool_match = re.search(r'TOOL:\s*\w+\([^)]*\)', thinking)
                if tool_match:
                    response_text = tool_match.group(0)

            return {
                'success': True,
                'response': response_text,
                'tool_calls': result.get('tool_calls', []),
                'model': result.get('model', self.model),
                'done': result.get('done', True),
                'thinking': result.get('thinking', '')
            }
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Ollama request timed out after {self.timeout}s")
            return {
                'success': False,
                'error': 'timeout',
                'message': 'LLM request timed out'
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama request failed: {e}")
            return {
                'success': False,
                'error': 'connection',
                'message': str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error in LLM generation: {e}", exc_info=True)
            return {
                'success': False,
                'error': 'unknown',
                'message': str(e)
            }
    
    def chat(self,
             messages: List[Dict[str, str]],
             tools: Optional[List[Dict]] = None,
             temperature: float = 0.7) -> Dict[str, Any]:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Available tools for function calling
            temperature: Sampling temperature
            
        Returns:
            dict: Response with 'response' and optional 'tool_calls'
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if tools:
                payload["tools"] = tools
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'response': result.get('message', {}).get('content', ''),
                'tool_calls': result.get('message', {}).get('tool_calls', []),
                'done': result.get('done', True)
            }
            
        except Exception as e:
            self.logger.error(f"Chat request failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def pull_model(self) -> bool:
        """
        Pull/download the model if not available.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info(f"Pulling model {self.model}...")
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=300  # 5 minutes for download
            )
            
            # Stream the download progress
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    if status:
                        self.logger.info(f"Pull status: {status}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull model: {e}")
            return False

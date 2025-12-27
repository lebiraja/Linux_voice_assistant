"""
Web access tools
"""

import requests
import logging
from typing import Dict, Any, List
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class SearchWebTool(Tool):
    """Search the web using DuckDuckGo"""
    
    @property
    def name(self) -> str:
        return "search_web"
    
    @property
    def description(self) -> str:
        return "Search the web for information using DuckDuckGo. Returns search results with titles and snippets."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            ),
            ToolParameter(
                name="max_results",
                type="integer",
                description="Maximum number of results to return",
                required=False,
                default=5
            )
        ]
    
    def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """Search the web"""
        try:
            # Use DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Extract results
            results = []
            
            # Abstract (main answer)
            if data.get('Abstract'):
                results.append({
                    "title": data.get('Heading', 'Answer'),
                    "snippet": data['Abstract'],
                    "url": data.get('AbstractURL', '')
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:max_results-1]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        "title": topic.get('Text', '').split(' - ')[0],
                        "snippet": topic.get('Text', ''),
                        "url": topic.get('FirstURL', '')
                    })
            
            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class FetchURLTool(Tool):
    """Fetch content from a URL"""
    
    @property
    def name(self) -> str:
        return "fetch_url"
    
    @property
    def description(self) -> str:
        return "Fetch content from a URL. Returns the text content of the page."
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="URL to fetch",
                required=True
            ),
            ToolParameter(
                name="max_length",
                type="integer",
                description="Maximum length of content to return (in characters)",
                required=False,
                default=2000
            )
        ]
    
    def execute(self, url: str, max_length: int = 2000, **kwargs) -> Dict[str, Any]:
        """Fetch URL content"""
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()
            
            # Get text content
            content = response.text[:max_length]
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.text),
                "content": content,
                "truncated": len(response.text) > max_length
            }
            
        except Exception as e:
            logger.error(f"Error fetching URL: {e}")
            return {
                "success": False,
                "error": str(e)
            }

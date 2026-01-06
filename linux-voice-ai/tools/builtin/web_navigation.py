"""
Web Navigation Tools - Smart URL opening and search
"""

import subprocess
import logging
import os
import yaml
import urllib.parse
from typing import Dict, Any, List, Optional
from ..base import Tool, ToolParameter

logger = logging.getLogger(__name__)


class OpenWebsiteTool(Tool):
    """Open websites by name (e.g., 'google' → google.com)"""
    
    def __init__(self):
        super().__init__()
        self.url_mappings = self._load_url_mappings()
    
    @property
    def name(self) -> str:
        return "open_website"
    
    @property
    def description(self) -> str:
        return (
            "Open websites by name. Examples: 'google', 'gmail', 'youtube', 'github'. "
            "Also supports action phrases like 'check email' or 'watch videos'."
        )
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="website",
                type="string",
                description="Website name or action phrase (e.g., 'google', 'gmail', 'check email')",
                required=True
            )
        ]
    
    def _load_url_mappings(self) -> Dict:
        """Load URL mappings from config file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "../../config/url_mappings.yaml"
            )
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load URL mappings: {e}")
            return {"websites": {}, "actions": {}, "search_engines": {}}
    
    def _open_url(self, url: str) -> Dict[str, Any]:
        """Open URL in default browser"""
        try:
            # Use xdg-open (works on most Linux desktops)
            subprocess.run(
                ["xdg-open", url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {"success": True, "url": url}
        except subprocess.CalledProcessError:
            # Fallback to firefox if xdg-open fails
            try:
                subprocess.run(
                    ["firefox", url],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return {"success": True, "url": url}
            except:
                return {"success": False, "error": "Could not open browser"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute(self, website: str, **kwargs) -> Dict[str, Any]:
        """Open website by name"""
        website_lower = website.lower().strip()
        
        # Check if it's an action phrase
        actions = self.url_mappings.get("actions", {})
        if website_lower in actions:
            website_lower = actions[website_lower]
        
        # Get URL from mappings
        websites = self.url_mappings.get("websites", {})
        if website_lower in websites:
            url = websites[website_lower]
            result = self._open_url(url)
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Opened {website}",
                    "url": url,
                    "website": website
                }
            else:
                return result
        else:
            # Try as direct URL if it looks like one
            if website.startswith("http://") or website.startswith("https://"):
                result = self._open_url(website)
                if result["success"]:
                    return {
                        "success": True,
                        "message": f"Opened {website}",
                        "url": website
                    }
                return result
            else:
                return {
                    "success": False,
                    "error": f"Unknown website: {website}. Try: google, gmail, youtube, github, etc."
                }


class WebSearchTool(Tool):
    """Search on specific websites (Google, YouTube, Wikipedia, etc.)"""
    
    def __init__(self):
        super().__init__()
        self.url_mappings = self._load_url_mappings()
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return (
            "Search on websites. Supports: google, youtube, wikipedia, github, stackoverflow, etc. "
            "Example: search 'python tutorial' on google"
        )
    
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
                name="engine",
                type="string",
                description="Search engine (google, youtube, wikipedia, github, etc.)",
                required=False,
                default="google"
            )
        ]
    
    def _load_url_mappings(self) -> Dict:
        """Load URL mappings from config file"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__),
                "../../config/url_mappings.yaml"
            )
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load URL mappings: {e}")
            return {"search_engines": {}}
    
    def _open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        try:
            subprocess.run(
                ["xdg-open", url],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            try:
                subprocess.run(
                    ["firefox", url],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            except:
                return False
    
    def execute(self, query: str, engine: str = "google", **kwargs) -> Dict[str, Any]:
        """Search on specified engine"""
        engine_lower = engine.lower().strip()
        
        # Get search URL template
        search_engines = self.url_mappings.get("search_engines", {})
        if engine_lower not in search_engines:
            engine_lower = "google"  # Default to Google
        
        url_template = search_engines.get(engine_lower)
        if not url_template:
            return {
                "success": False,
                "error": f"Unknown search engine: {engine}"
            }
        
        # Format URL with query
        encoded_query = urllib.parse.quote_plus(query)
        search_url = url_template.format(query=encoded_query)
        
        # Open in browser
        if self._open_url(search_url):
            return {
                "success": True,
                "message": f"Searching '{query}' on {engine}",
                "query": query,
                "engine": engine,
                "url": search_url
            }
        else:
            return {
                "success": False,
                "error": "Could not open browser"
            }

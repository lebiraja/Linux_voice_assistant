"""
User context and preferences manager
Stores important user information and preferences across sessions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UserContext:
    """
    Manages user profile, preferences, and important context information.
    This information persists across sessions and influences JARVIS's behavior.
    """
    
    def __init__(self, context_file: str = "user_context.json"):
        """
        Initialize user context.
        
        Args:
            context_file: Path to JSON file for storing context
        """
        self.context_file = Path(context_file)
        self.context: Dict[str, Any] = {
            "user_info": {},
            "preferences": {},
            "important_facts": [],
            "work_context": {},
            "app_preferences": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        self.logger = logging.getLogger(__name__)
        self._load_context()
    
    def _load_context(self):
        """Load context from file if it exists"""
        if self.context_file.exists():
            try:
                with open(self.context_file, 'r') as f:
                    loaded = json.load(f)
                    self.context.update(loaded)
                self.logger.info(f"Loaded user context from {self.context_file}")
            except Exception as e:
                self.logger.error(f"Error loading context: {e}")
    
    def _save_context(self):
        """Save context to file"""
        try:
            self.context["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            self.context_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2)
            
            self.logger.debug(f"Saved user context to {self.context_file}")
        except Exception as e:
            self.logger.error(f"Error saving context: {e}")
    
    def set_user_info(self, key: str, value: Any):
        """
        Set user information.
        
        Args:
            key: Information key (name, location, occupation, etc.)
            value: Information value
        
        Examples:
            set_user_info("name", "John")
            set_user_info("timezone", "EST")
            set_user_info("workspace", "/home/john/projects")
        """
        self.context["user_info"][key] = value
        self._save_context()
        self.logger.info(f"Set user info: {key} = {value}")
    
    def get_user_info(self, key: str) -> Optional[Any]:
        """Get user information by key"""
        return self.context["user_info"].get(key)
    
    def set_preference(self, category: str, key: str, value: Any):
        """
        Set user preference.
        
        Args:
            category: Preference category (response, ui, voice, etc.)
            key: Preference key
            value: Preference value
        
        Examples:
            set_preference("response", "style", "concise")
            set_preference("response", "detail_level", "intermediate")
            set_preference("voice", "speed", "normal")
        """
        if category not in self.context["preferences"]:
            self.context["preferences"][category] = {}
        
        self.context["preferences"][category][key] = value
        self._save_context()
        self.logger.info(f"Set preference: {category}.{key} = {value}")
    
    def get_preference(self, category: str, key: str, default: Any = None) -> Any:
        """Get user preference with optional default"""
        return self.context["preferences"].get(category, {}).get(key, default)
    
    def add_important_fact(self, fact: str, category: str = "general"):
        """
        Add an important fact about the user.
        
        Args:
            fact: The fact to remember
            category: Category/tag for the fact
        
        Examples:
            add_important_fact("User prefers Python over JavaScript", "programming")
            add_important_fact("User works on machine learning projects", "work")
        """
        fact_entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        
        # Limit to 50 facts
        if len(self.context["important_facts"]) >= 50:
            self.context["important_facts"].pop(0)
        
        self.context["important_facts"].append(fact_entry)
        self._save_context()
        self.logger.info(f"Added important fact: {fact}")
    
    def get_important_facts(self, category: Optional[str] = None, limit: int = 10) -> List[str]:
        """
        Get important facts, optionally filtered by category.
        
        Args:
            category: Filter by category (None for all)
            limit: Maximum number of facts to return
        
        Returns:
            List of fact strings
        """
        facts = self.context["important_facts"]
        
        if category:
            facts = [f for f in facts if f["category"] == category]
        
        # Return most recent facts
        recent_facts = facts[-limit:] if len(facts) > limit else facts
        return [f["fact"] for f in reversed(recent_facts)]
    
    def set_work_context(self, key: str, value: Any):
        """
        Set work-related context.
        
        Args:
            key: Context key (project, directory, language, etc.)
            value: Context value
        
        Examples:
            set_work_context("current_project", "web-scraper")
            set_work_context("project_directory", "/home/user/projects/scraper")
            set_work_context("primary_language", "Python")
        """
        self.context["work_context"][key] = value
        self._save_context()
        self.logger.info(f"Set work context: {key} = {value}")
    
    def get_work_context(self, key: str) -> Optional[Any]:
        """Get work context by key"""
        return self.context["work_context"].get(key)
    
    def set_app_preference(self, app_type: str, app_name: str):
        """
        Set preferred application for a type.
        
        Args:
            app_type: Application type (browser, editor, terminal, etc.)
            app_name: Preferred application name
        
        Examples:
            set_app_preference("browser", "firefox")
            set_app_preference("editor", "vscode")
            set_app_preference("terminal", "gnome-terminal")
        """
        self.context["app_preferences"][app_type] = app_name
        self._save_context()
        self.logger.info(f"Set app preference: {app_type} = {app_name}")
    
    def get_app_preference(self, app_type: str) -> Optional[str]:
        """Get preferred app for a type"""
        return self.context["app_preferences"].get(app_type)
    
    def get_context_summary(self) -> str:
        """
        Get a formatted summary of user context for LLM prompts.
        
        Returns:
            Formatted string with relevant user context
        """
        summary_parts = []
        
        # User info
        if self.context["user_info"]:
            info_parts = []
            for key, value in self.context["user_info"].items():
                info_parts.append(f"{key}: {value}")
            if info_parts:
                summary_parts.append("User Info: " + ", ".join(info_parts))
        
        # Response preferences
        if "response" in self.context["preferences"]:
            prefs = self.context["preferences"]["response"]
            pref_parts = []
            for key, value in prefs.items():
                pref_parts.append(f"{key}: {value}")
            if pref_parts:
                summary_parts.append("Response Preferences: " + ", ".join(pref_parts))
        
        # App preferences
        if self.context["app_preferences"]:
            app_parts = []
            for app_type, app_name in self.context["app_preferences"].items():
                app_parts.append(f"{app_type}: {app_name}")
            if app_parts:
                summary_parts.append("App Preferences: " + ", ".join(app_parts))
        
        # Work context
        if self.context["work_context"]:
            work_parts = []
            for key, value in self.context["work_context"].items():
                work_parts.append(f"{key}: {value}")
            if work_parts:
                summary_parts.append("Work Context: " + ", ".join(work_parts))
        
        # Important facts (last 5)
        recent_facts = self.get_important_facts(limit=5)
        if recent_facts:
            summary_parts.append("Important Facts: " + "; ".join(recent_facts))
        
        return "\n".join(summary_parts) if summary_parts else ""
    
    def learn_from_interaction(self, user_input: str, context: Optional[Dict] = None):
        """
        Automatically learn preferences from user interactions.
        
        Args:
            user_input: What the user said
            context: Optional context from the interaction
        
        This method detects patterns like:
        - "I prefer X"
        - "My name is X"
        - "I work on X"
        - "I like X"
        """
        input_lower = user_input.lower().strip()
        
        # Detect name
        if "my name is" in input_lower or "i'm " in input_lower or "i am " in input_lower:
            # Simple name extraction (this could be enhanced)
            for phrase in ["my name is ", "i'm ", "i am ", "call me "]:
                if phrase in input_lower:
                    parts = input_lower.split(phrase, 1)
                    if len(parts) > 1:
                        name_part = parts[1].split()[0] if parts[1].split() else ""
                        if name_part and len(name_part) > 1:
                            self.set_user_info("name", name_part.capitalize())
                            break
        
        # Detect preferences
        if "i prefer" in input_lower or "i like" in input_lower:
            self.add_important_fact(user_input, "preference")
        
        # Detect work context
        if "i work on" in input_lower or "i'm working on" in input_lower:
            self.add_important_fact(user_input, "work")
        
        # Detect app preferences from successful actions
        if context and context.get("action") == "open_app" and context.get("success"):
            app_type = context.get("app_type")
            app_name = context.get("target")
            if app_type and app_name:
                # Track app usage (could build preference over time)
                pass
    
    def clear_context(self):
        """Clear all user context (reset)"""
        self.context = {
            "user_info": {},
            "preferences": {},
            "important_facts": [],
            "work_context": {},
            "app_preferences": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        }
        self._save_context()
        self.logger.info("User context cleared")
    
    def export_context(self) -> Dict[str, Any]:
        """Export entire context as dictionary"""
        return self.context.copy()
    
    def __str__(self) -> str:
        """String representation"""
        num_facts = len(self.context["important_facts"])
        num_prefs = sum(len(v) for v in self.context["preferences"].values())
        return f"UserContext({num_facts} facts, {num_prefs} preferences)"

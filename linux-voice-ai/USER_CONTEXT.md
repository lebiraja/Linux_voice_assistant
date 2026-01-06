# JARVIS User Context & Personalization

JARVIS now remembers important information about you and your preferences to provide personalized assistance!

## 🎯 Overview

The User Context system allows JARVIS to:
- **Remember your preferences** (response style, favorite apps, etc.)
- **Learn about you** (name, occupation, interests)
- **Track work context** (current projects, programming languages)
- **Personalize responses** based on what it knows about you
- **Persist across sessions** - remembers even after restart

## ✨ Features

### 1. **User Information**
JARVIS remembers personal details you share:
- Name
- Location/Timezone
- Occupation
- Interests
- Workspace directory

### 2. **Preferences**
JARVIS adapts to your preferences:
- **Response style**: concise, detailed, casual
- **Detail level**: simple, intermediate, advanced
- **Favorite apps**: browser, editor, terminal
- **Programming preferences**: languages, frameworks

### 3. **Work Context**
JARVIS tracks what you're working on:
- Current project
- Project directory
- Primary programming language
- Current tasks

### 4. **Important Facts**
JARVIS remembers key things you mention:
- "I prefer Python over JavaScript"
- "I work on machine learning projects"
- "I use Firefox for web development"

## 🛠️ How It Works

### Automatic Learning

JARVIS automatically learns from your interactions:

```
You: "My name is Alex"
JARVIS: [Automatically remembers]
       "Got it, I'll remember your name, Alex!"

You: "I prefer concise responses"
JARVIS: [Saves preference]
       "I'll keep my responses brief from now on."

You: "I'm working on a web scraper project"
JARVIS: [Saves work context]
       "Noted, I'll remember that you're working on a web scraper."
```

### Manual Context Setting

You can explicitly tell JARVIS to remember things:

```
You: "Remember that I use VS Code as my editor"
JARVIS: [Saves app preference]
       "I'll remember that you prefer VS Code."

You: "My primary language is Python"
JARVIS: [Saves work context]
       "Noted, I'll keep in mind that Python is your primary language."
```

### Context-Aware Responses

JARVIS uses what it knows to personalize interactions:

```
You: "Open my editor"
JARVIS: [Uses remembered preference: vscode]
       "Opening VS Code." 

You: "Create a script for my project"
JARVIS: [Uses remembered project context and language]
       "I'll create a Python script for your web-scraper project."

You: "Explain async programming"
JARVIS: [Uses remembered detail level preference]
       "Here's an intermediate-level explanation..."
```

## 📋 Usage Examples

### Example 1: Introducing Yourself

```
You: "Hey JARVIS, my name is Sarah"

JARVIS: "Nice to meet you, Sarah! I'll remember that."

You: "I'm a software developer working primarily in Python"

JARVIS: "Got it! I'll remember that you're a developer who works with Python."

You: "I prefer detailed explanations when I ask questions"

JARVIS: "Understood. I'll provide thorough explanations when you ask questions."
```

### Example 2: Setting App Preferences

```
You: "I want you to use Firefox when I say 'open browser'"

JARVIS: [Remembers: browser preference = firefox]
       "I'll remember to use Firefox as your browser."

You: "Open browser"

JARVIS: [Uses preference]
       "Opening Firefox."

You: "My preferred terminal is Alacritty"

JARVIS: "Got it, I'll use Alacritty as your terminal."

You: "Open terminal"

JARVIS: "Opening Alacritty."
```

### Example 3: Work Context

```
You: "I'm starting work on a Django project called 'blog-platform'"

JARVIS: [Saves: current_project = blog-platform, framework = Django]
       "Noted! I'll remember you're working on the blog-platform Django project."

You: "The project directory is ~/projects/blog"

JARVIS: [Saves: project_directory]
       "I'll remember your project is in ~/projects/blog."

You: "Create a script to run the Django dev server"

JARVIS: [Uses project context]
       "I'll create a script to run the Django dev server for your blog-platform project."
       [Generates: python manage.py runserver in ~/projects/blog]
```

### Example 4: Learning Preferences Over Time

```
You: "Explain Docker"

JARVIS: "Docker is a containerization platform..."

You: "That's good, but I prefer simpler explanations"

JARVIS: [Saves: response preference = simple]
       "Got it! I'll explain things more simply from now on."

You: "Explain Kubernetes"

JARVIS: [Uses simple explanation preference]
       "Kubernetes is like a manager for containers. It helps you run lots of 
        containers across many computers and keeps them healthy..."

You: "Perfect! That's the level of detail I like"

JARVIS: "Great! I'll continue with that style."
```

## 🔧 Context Categories

### User Information
```
remember_user_info(info_type="name", value="Alex")
remember_user_info(info_type="occupation", value="developer")
remember_user_info(info_type="location", value="San Francisco")
remember_user_info(info_type="timezone", value="PST")
```

### Response Preferences
```
set_user_preference(category="response", preference="style", value="concise")
set_user_preference(category="response", preference="detail_level", value="intermediate")
set_user_preference(category="response", preference="tone", value="friendly")
```

### App Preferences
```
set_user_preference(category="app", preference="browser", value="firefox")
set_user_preference(category="app", preference="editor", value="vscode")
set_user_preference(category="app", preference="terminal", value="gnome-terminal")
```

### Work Context
```
set_work_context(context_type="current_project", value="web-scraper")
set_work_context(context_type="project_directory", value="/home/user/projects/scraper")
set_work_context(context_type="primary_language", value="Python")
set_work_context(context_type="framework", value="Django")
```

## ⚙️ Configuration

Context is stored in `user_context.json` (configurable):

```yaml
# config/config.yaml
conversation:
  enabled: true
  max_history: 10
  context_window: 5
  context_file: "user_context.json"  # Where to store user context
```

## 📊 Context File Structure

`user_context.json`:
```json
{
  "user_info": {
    "name": "Alex",
    "occupation": "developer",
    "timezone": "EST"
  },
  "preferences": {
    "response": {
      "style": "concise",
      "detail_level": "intermediate"
    },
    "app": {
      "browser": "firefox",
      "editor": "vscode"
    }
  },
  "work_context": {
    "current_project": "blog-platform",
    "project_directory": "/home/alex/projects/blog",
    "primary_language": "Python"
  },
  "important_facts": [
    {
      "fact": "User prefers Python over JavaScript",
      "category": "programming",
      "timestamp": "2026-01-06T10:30:00"
    }
  ],
  "metadata": {
    "created": "2026-01-06T09:00:00",
    "last_updated": "2026-01-06T10:30:00"
  }
}
```

## 🎓 Advanced Features

### Context Summary in Prompts

JARVIS includes relevant context when processing requests:

```
User Context:
User Info: name: Alex, occupation: developer
Response Preferences: style: concise, detail_level: intermediate
App Preferences: browser: firefox, editor: vscode
Work Context: current_project: blog-platform, primary_language: Python
```

### Automatic Pattern Detection

JARVIS detects and learns from patterns:

```
"My name is..." → Saves name
"I prefer..." → Saves preference
"I work on..." → Saves work context
"I like..." → Saves as important fact
```

### Context-Aware Tool Selection

JARVIS uses context to make better decisions:

```
You: "Open my editor"
JARVIS: [Checks app_preferences.editor → "vscode"]
       Uses: open_app(app_name="vscode")

You: "Create a backup script"
JARVIS: [Checks primary_language → "Python"]
       Uses: generate_and_run_script(language="python")
```

## 🔍 Viewing Your Context

Ask JARVIS about stored context:

```
You: "What do you know about me?"

JARVIS: "Here's what I remember:
         - Your name is Alex
         - You're a developer
         - You prefer concise, intermediate-level responses
         - Your favorite editor is VS Code
         - You're working on the blog-platform project in Python"

You: "What's my current project?"

JARVIS: "You're working on blog-platform, a Django project."
```

## 🔄 Managing Context

### Updating Preferences

```
You: "Actually, I prefer detailed responses now"

JARVIS: [Updates preference]
       "I'll provide more detailed responses from now on."
```

### Adding New Context

```
You: "I've started learning Rust"

JARVIS: [Adds to work context]
       "Noted! I'll remember you're learning Rust."
```

### Context Persistence

- Context is saved automatically after each update
- Survives restarts
- Shared across all JARVIS sessions
- Stored in JSON for easy backup/portability

## 💡 Tips for Best Results

### 1. **Be Explicit**
Tell JARVIS clearly when you want it to remember something:
```
✅ "Remember that I use Firefox"
✅ "My preferred response style is concise"
❌ "I opened Firefox" (won't be saved as preference)
```

### 2. **Share Context Early**
Introduce yourself and set preferences when you first use JARVIS:
```
"My name is Alex, I'm a Python developer, and I prefer concise responses"
```

### 3. **Update as Needed**
Tell JARVIS when your preferences change:
```
"I've switched to VS Code from Sublime"
"I'm now working on a React project"
```

### 4. **Use Natural Language**
No special syntax needed:
```
"I prefer detailed explanations"
"My workspace is in ~/dev/projects"
"I work primarily in Python"
```

## 🚀 Example Workflows

### First-Time Setup

```
You: "Hey JARVIS"
JARVIS: "Hello! How can I help?"

You: "My name is Alex, I'm a software developer"
JARVIS: "Nice to meet you, Alex! I'll remember that you're a developer."

You: "I use Firefox and VS Code"
JARVIS: "Got it, I'll remember Firefox and VS Code as your preferred apps."

You: "I prefer intermediate-level, concise responses"
JARVIS: "Understood. I'll keep my responses concise and at an intermediate level."

You: "I'm currently working on a Python project called blog-platform"
JARVIS: "Noted! I'll remember you're working on the blog-platform Python project."
```

### Daily Usage with Context

```
You: "Good morning JARVIS"
JARVIS: "Good morning, Alex! Ready to work on blog-platform?"

You: "Yes, open my editor and terminal"
JARVIS: [Uses preferences: vscode, gnome-terminal]
       "Opening VS Code and GNOME Terminal."

You: "Create a test script for my project"
JARVIS: [Uses: Python, blog-platform context]
       "I'll create a Python test script for blog-platform."

You: "Explain pytest"
JARVIS: [Uses: concise, intermediate preferences]
       "Pytest is a Python testing framework..."
```

## 📚 Related Documentation

- [CONVERSATION.md](CONVERSATION.md) - Conversation features
- [README.md](README.md) - Main documentation
- [USAGE.md](USAGE.md) - Usage guide

---

**Made with 🧠 by the JARVIS team**

*"JARVIS Remembers. JARVIS Personalizes."*

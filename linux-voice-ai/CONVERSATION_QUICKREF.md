# 💬 JARVIS Conversation - Quick Reference

## Basic Usage

### Ask Questions
```
"What is Docker?"
"How does Linux work?"
"Tell me about Python"
"What's the difference between Git and GitHub?"
```

### Get Explanations
```
"Explain containerization"
"Explain machine learning in simple terms"
"How does DNS work?"
"What is a REST API?"
```

### Casual Chat
```
"Hello JARVIS"
"How are you?"
"Thanks for the help"
"Good job"
```

## Conversation Modes

### 1. Question & Answer
- Use: General knowledge, technical questions
- Examples:
  - "What is Kubernetes?"
  - "How do I install Node.js?"
  - "What are Linux permissions?"

### 2. Concept Explanation
- Use: Understanding how things work
- Examples:
  - "Explain Docker"
  - "Explain async/await in simple terms"
  - "How does SSH work?"

### 3. Casual Conversation
- Use: Greetings, thank you's, small talk
- Examples:
  - "Hello"
  - "Thanks!"
  - "That's interesting"

## Detail Levels

### Concise (Default)
```
You: "What is Python?"
JARVIS: "Python is a high-level programming language 
         known for readability and versatility."
```

### Detailed
```
You: "Tell me about Python in detail"
JARVIS: [Provides thorough explanation with examples]
```

### Simple/Beginner
```
You: "Explain Docker in simple terms"
JARVIS: [ELI5-style explanation]
```

## Context Memory

JARVIS remembers recent conversations:

```
You: "What is Kubernetes?"
JARVIS: "Kubernetes is a container orchestration platform..."

You: "How do I install it?"
JARVIS: [Knows "it" = Kubernetes]
```

## Mixing Commands & Conversation

```
"Open terminal"              # Command
"What is the pwd command?"   # Question
"List files"                 # Command
"Thanks!"                    # Conversation
```

## Configuration

`config/config.yaml`:
```yaml
conversation:
  enabled: true      # Enable conversation mode
  max_history: 10    # Remember last 10 exchanges
  context_window: 5  # Use 5 recent exchanges for context
```

## Tips

✅ **DO:**
- Ask naturally: "What is Docker?"
- Use follow-ups: "How do I install it?"
- Mix commands and questions freely
- Specify detail level when needed

❌ **DON'T:**
- Over-formalize: "Please provide information regarding..."
- Repeat context: "What is Kubernetes? Also tell me about Kubernetes."
- Force commands: Every question doesn't need an action

## Common Patterns

### Learning Flow
```
1. "What is X?"           # Get definition
2. "How does it work?"    # Understand mechanism
3. "How do I use it?"     # Learn application
4. "Show me an example"   # See practice
```

### Problem Solving
```
1. "How do I do X?"       # Get approach
2. "What's the command?"  # Get specific tool
3. "Can you help?"        # Request assistance
4. "Create a script"      # Automate solution
```

## See Also

- [CONVERSATION.md](CONVERSATION.md) - Full documentation
- [USAGE.md](USAGE.md) - General usage guide
- [README.md](README.md) - Main documentation

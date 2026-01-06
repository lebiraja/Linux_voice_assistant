# 🚀 JARVIS Script Generation - Quick Reference

## Installation

```bash
# 1. Quick setup (recommended)
./setup-script-generation.sh

# 2. Or manual setup
./install-aichat.sh
cp config/aichat-config.yaml ~/.config/aichat/config.yaml
```

## Voice Commands

### Generate and Run Scripts
- "Write a script to [task]"
- "Create a [language] script that [does X]"
- "Generate a script to [accomplish Y]"

### Examples
```
✓ "Write a script to back up my Documents folder"
✓ "Create a Python script to organize Downloads by file type"
✓ "Generate a script to monitor CPU usage for 1 minute"
✓ "Make a script that finds all large files over 100MB"
✓ "Write a script to convert all PNG images to JPG"
```

### Execute Commands Directly
- "Run command [shell command]"
- "Execute [command]"

```
✓ "Run git status"
✓ "Execute docker ps"
✓ "Run df -h"
```

## Supported Languages

- **Bash** (default) - System scripts, automation
- **Python** - Data processing, complex logic
- **JavaScript** - Node.js scripts
- **Perl, Ruby, PHP** - Also supported

## Common Use Cases

### 📁 File Management
```
"Create a script to organize files by extension"
"Write a script to find duplicate files"
"Generate a script to rename files in batch"
```

### 🔧 System Administration
```
"Write a script to clean up old log files"
"Create a backup script with rotation"
"Generate a system health check script"
```

### 💾 Data Processing
```
"Write a Python script to parse this CSV file"
"Create a script to merge multiple text files"
"Generate a script to extract data from JSON"
```

### 🌐 Network & Web
```
"Write a script to check website availability"
"Create a script to download files from URLs"
"Generate a script to monitor network bandwidth"
```

### 🐳 DevOps
```
"Write a script to clean up Docker resources"
"Create a deployment automation script"
"Generate a script to run tests and report results"
```

## Configuration

Edit `config/config.yaml`:

```yaml
aichat:
  enabled: true
  model: "ollama:deepseek-r1:1.5b"  # Fast, local
  timeout: 60
  max_script_execution_time: 300
  auto_execute: true  # Set false for manual review
```

## Safety Tips

1. ✅ Start with simple scripts
2. ✅ Use specific, clear descriptions
3. ✅ Review complex scripts before execution
4. ✅ Set `auto_execute: false` for critical operations
5. ✅ Scripts timeout after 5 minutes by default

## Troubleshooting

### aichat not found
```bash
./install-aichat.sh
```

### Script generation fails
```bash
# Test aichat directly
aichat "write hello world script"

# Check Ollama is running
curl http://localhost:11434/api/tags

# Check logs
tail -f logs/lva.log
```

### Permission errors
Scripts may need sudo for system operations. Include in task:
```
"Write a script that uses sudo to install packages"
```

## Testing

Run the test suite:
```bash
python3 tests/test_script_generation.py
```

## Full Documentation

See [SCRIPT_GENERATION.md](SCRIPT_GENERATION.md) for complete guide.

## Model Options

### Local (Free, Private)
- `ollama:deepseek-r1:1.5b` - ⚡ Fast, good for most scripts
- `ollama:llama3.2` - 🎯 More capable
- `ollama:codellama` - 💻 Specialized for code

### Cloud (Requires API Key)
- `openai:gpt-4` - 🚀 Most capable
- `claude:claude-3-sonnet` - ⚖️ Great balance

Configure in `~/.config/aichat/config.yaml`

## Tips & Tricks

1. **Be specific**: "Create a script to..." works better than "Make something that..."
2. **Mention requirements**: Include error handling, logging needs, etc.
3. **Specify language**: Default is Bash, but Python often better for complex tasks
4. **Use working directory**: Scripts run where you want them to
5. **Chain operations**: "Pull code, run tests, deploy if passing"

## Examples by Task Type

### Backup Scripts
```
"Write a script to tar.gz my home folder with timestamp"
"Create an incremental backup script with rotation"
```

### Monitoring
```
"Generate a script to log memory usage every 10 seconds"
"Write a script to alert if disk is over 90% full"
```

### File Processing
```
"Create a script to resize all images to 800x600"
"Write a script to extract zip files recursively"
```

### Git Operations
```
"Generate a script to commit and push all changes"
"Write a script to clean up merged branches"
```

---

**Need help?** Check the full docs or ask JARVIS: "How do I use script generation?"

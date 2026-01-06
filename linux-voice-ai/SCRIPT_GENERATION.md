# AI Script Generation Feature

## 🤖 Overview

JARVIS can now **generate and execute scripts automatically** based on natural language requirements using [aichat](https://github.com/sigoden/aichat). This powerful feature allows you to describe complex tasks in plain English, and JARVIS will write and run the appropriate script for you.

## ✨ Features

- **AI-Powered Script Generation**: Describe what you want in natural language
- **Multi-Language Support**: Generate Bash, Python, JavaScript, and more
- **Automatic Execution**: Scripts are automatically run after generation
- **Safety**: Review mode available for manual approval
- **Error Handling**: Built-in timeout and error reporting
- **Flexible Working Directory**: Run scripts anywhere on your system

## 📦 Installation

### 1. Install aichat CLI

Run the installation script:

```bash
cd linux-voice-ai
./install-aichat.sh
```

Or install manually:

```bash
curl -fsSL https://raw.githubusercontent.com/sigoden/aichat/main/scripts/install.sh | bash
```

### 2. Configure aichat

For **local AI** (recommended - works with your existing Ollama):

```bash
aichat --model ollama:deepseek-r1:1.5b
```

This will use your existing Ollama installation without requiring additional setup!

For other AI providers, run the setup:

```bash
aichat --setup
```

Choose from:
- **Ollama** (local, free, recommended)
- OpenAI (requires API key)
- Anthropic Claude (requires API key)
- Google Gemini (requires API key)
- And many more!

### 3. Verify Installation

```bash
aichat --version
```

## 🎯 Usage Examples

### Example 1: System Administration

**Say:** "JARVIS, write a script to back up my Documents folder to /backup with timestamp"

**What happens:**
1. JARVIS generates a Bash script with proper error handling
2. Creates timestamped backup directory
3. Copies files with progress
4. Reports success/failure

### Example 2: File Organization

**Say:** "JARVIS, create a Python script to organize my Downloads folder by file type"

**What happens:**
1. Generates Python script
2. Scans Downloads folder
3. Creates subdirectories (Images, Documents, Videos, etc.)
4. Moves files to appropriate folders
5. Shows summary

### Example 3: System Monitoring

**Say:** "JARVIS, write a script to monitor CPU and save to a log file every 5 seconds for 1 minute"

**What happens:**
1. Creates monitoring script
2. Logs CPU usage with timestamps
3. Saves to file
4. Stops after 1 minute

### Example 4: Batch Processing

**Say:** "JARVIS, generate a script to convert all PNG images in current folder to JPG with 80% quality"

**What happens:**
1. Generates image conversion script
2. Finds all PNG files
3. Converts each to JPG
4. Reports results

### Example 5: Git Operations

**Say:** "JARVIS, write a script to commit all changes with message 'Update docs' and push to main"

**What happens:**
1. Generates Git script
2. Stages all changes
3. Commits with message
4. Pushes to remote

## 🎮 Voice Commands

### Generate and Run Script (Auto-Execute)
- "Write a script to [task description]"
- "Create a [language] script that [does something]"
- "Generate a script to [accomplish task]"
- "Make a script that [task]"

### Generate Only (Manual Review)
- "Generate a script to [task] but don't run it"
- "Write a script for [task] without executing"

### Execute Command Directly
- "Run command [shell command]"
- "Execute [command]"

## 🔧 Tool Parameters

### `generate_and_run_script`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_description` | string | required | What the script should accomplish |
| `language` | string | "bash" | Programming language (bash, python, js, etc.) |
| `auto_execute` | boolean | true | Whether to run the script automatically |
| `working_directory` | string | null | Where to run the script |

### `execute_command`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | string | required | Shell command to execute |
| `working_directory` | string | null | Where to run the command |
| `timeout` | integer | 30 | Command timeout in seconds |

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
# AI Script Generation (aichat)
aichat:
  enabled: true
  model: "ollama:deepseek-r1:1.5b"  # Use local Ollama
  timeout: 60  # Script generation timeout
  max_script_execution_time: 300  # 5 minutes max
  auto_execute: true  # Auto-run generated scripts
  working_directory: null  # Default working directory
```

### Configuration Options

- **model**: AI model to use for script generation
  - `ollama:deepseek-r1:1.5b` - Fast, local (recommended)
  - `ollama:llama3.2` - More capable
  - `openai:gpt-4` - Most capable (requires API key)
  - `claude:claude-3-sonnet` - Great balance (requires API key)

- **timeout**: How long to wait for script generation (seconds)

- **max_script_execution_time**: Maximum time scripts can run (seconds)

- **auto_execute**: Set to `false` for manual approval of scripts

- **working_directory**: Default directory for script execution

## 🛡️ Safety Features

### Automatic Safety Measures

1. **Execution Timeout**: Scripts are killed after 5 minutes by default
2. **Error Handling**: All errors are caught and reported
3. **Temporary Files**: Scripts are created in temp locations and cleaned up
4. **Working Directory Isolation**: Scripts run in specified directories

### Manual Review Mode

To review scripts before execution, set in config:

```yaml
aichat:
  auto_execute: false
```

Or use voice command: "Generate a script but don't run it"

### Best Practices

1. **Start Small**: Test with simple scripts first
2. **Review Complex Tasks**: For system-critical operations, review scripts manually
3. **Use Specific Descriptions**: More detail = better scripts
4. **Check Permissions**: Ensure you have rights for the operation
5. **Monitor Output**: Watch script execution for errors

## 🎨 Examples by Use Case

### File Management

```
"Create a script to find all files larger than 100MB in my home directory"
"Write a script to delete all .tmp files older than 7 days"
"Generate a script to rename all .txt files to .md in current folder"
```

### System Maintenance

```
"Write a script to check disk space and alert if less than 10% free"
"Create a script to update all packages and log the output"
"Generate a script to clean up Docker images and containers"
```

### Development

```
"Write a script to create a new Python project with virtual environment"
"Generate a script to run tests and generate coverage report"
"Create a script to build and deploy my Docker container"
```

### Data Processing

```
"Write a Python script to parse CSV file and calculate averages"
"Generate a script to download files from a list of URLs"
"Create a script to compress all videos in a folder to save space"
```

### Network & Web

```
"Write a script to check if websites in urls.txt are online"
"Generate a script to download and archive a website"
"Create a script to monitor network bandwidth usage"
```

## 🔍 Troubleshooting

### aichat not found

```bash
# Reinstall aichat
./install-aichat.sh

# Or manually
curl -fsSL https://raw.githubusercontent.com/sigoden/aichat/main/scripts/install.sh | bash
```

### Script generation fails

1. Check aichat is configured: `aichat --version`
2. Test aichat directly: `aichat "write hello world script"`
3. Check model is available: `ollama list`
4. Review logs: `tail -f logs/lva.log`

### Script execution timeout

Increase timeout in config:

```yaml
aichat:
  max_script_execution_time: 600  # 10 minutes
```

### Permission denied errors

Scripts may need sudo for system operations:

```yaml
# Generate script that uses sudo
"Write a script to install package using sudo"
```

## 🚀 Advanced Usage

### Custom AI Models

Use different models for different tasks:

```bash
# In your aichat config (~/.config/aichat/config.yaml)
model: ollama:codellama  # For code generation
# or
model: openai:gpt-4      # For complex tasks
```

### Script Templates

Create reusable script templates by describing patterns:

```
"Generate a script template for daily backups with rotation"
"Create a monitoring script that emails on failure"
```

### Chaining Operations

Combine multiple operations:

```
"Write a script to pull latest code, run tests, and deploy if tests pass"
```

## 📊 Performance Tips

1. **Use Faster Models**: `deepseek-r1:1.5b` is fast for simple scripts
2. **Be Specific**: Clear descriptions = faster generation
3. **Local Models**: Ollama is faster than API calls
4. **Caching**: aichat caches conversations for speed

## 🎯 What's Next?

Planned improvements:

- [ ] Script history and reuse
- [ ] Interactive script debugging
- [ ] Script library/templates
- [ ] Multi-step script workflows
- [ ] Script scheduling
- [ ] Visual script editor

## 📚 Resources

- [aichat GitHub](https://github.com/sigoden/aichat)
- [aichat Documentation](https://github.com/sigoden/aichat/blob/main/README.md)
- [Ollama Models](https://ollama.ai/library)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)
- [Python Documentation](https://docs.python.org/3/)

## 🤝 Contributing

Have ideas for better script generation? Open an issue or PR!

## 📄 License

Same as parent project (MIT)

# Quick Start - Docker

## One-Command Setup

```bash
cd /home/lebi/projects/VFL/linux-voice-ai
./docker-setup.sh
```

This will:
- Start Ollama and Voice Assistant containers
- Pull functiongemma:270m model
- Configure everything automatically

## Manual Setup

```bash
# 1. Allow X11
xhost +local:docker

# 2. Start services
docker-compose up -d

# 3. Pull model
docker exec ollama ollama pull functiongemma:270m

# 4. Check status
docker-compose ps
```

## Usage

```bash
# View logs
docker-compose logs -f voice-assistant

# Stop
docker-compose down

# Restart
docker-compose restart
```

## Testing

Press `Ctrl+Space` and say:
- "open firefox" (should use RULES)
- "tell me about my system" (should use LLM)

See full documentation in `DOCKER_SETUP.md`

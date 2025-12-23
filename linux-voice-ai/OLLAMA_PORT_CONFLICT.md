# Quick Fix: Stop Host Ollama and Start Docker Version

## The Issue
Port 11434 is already in use by Ollama running on your host machine.

## Solution: Stop Host Ollama

```bash
# Stop host Ollama
sudo pkill ollama

# Verify it's stopped
lsof -i :11434
# (should show nothing)

# Now run the Docker setup
./docker-setup.sh
```

## Alternative: Use Host Ollama (Simpler)

If you prefer to use your existing host Ollama instead of Docker:

1. **Keep host Ollama running**
2. **Remove Ollama from docker-compose.yml**:
   ```bash
   # Edit docker-compose.yml and remove the entire ollama service section
   ```
3. **Start only the voice assistant**:
   ```bash
   docker-compose up -d voice-assistant
   ```

The voice assistant will automatically connect to your host Ollama at `localhost:11434`.

## Recommended: Use Host Ollama

Since you already have Ollama installed and running, it's simpler to use it:

```bash
# 1. Make sure host Ollama is running
ollama serve &

# 2. Pull the model (if not already done)
ollama pull functiongemma:270m

# 3. Start only voice assistant container
docker-compose up -d voice-assistant

# 4. Check logs
docker-compose logs -f voice-assistant
```

This avoids port conflicts and uses your existing Ollama setup!

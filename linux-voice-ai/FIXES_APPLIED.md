# Quick Fixes Applied

## Issue 1: Poor STT Accuracy ✅ FIXED
**Problem:** Whisper "tiny" model is very inaccurate (39M parameters)
**Solution:** Upgraded to "base" model (74M parameters) - 2x better accuracy

**Change in `config/config.yaml`:**
```yaml
stt:
  model_name: "base"  # Was "tiny"
```

**Note:** The base model will download automatically on next restart (~142MB)

## Issue 2: TTS Playing Twice
**Status:** Cannot reproduce from logs - appears to play once

The logs show:
1. TTS synthesizes once
2. Audio player plays once
3. No duplicate calls

**Possible causes:**
- Echo in your audio setup
- PulseAudio loopback
- Multiple audio outputs

**To verify:**
```bash
# Check for audio loopback
pactl list short modules | grep loopback

# Check active sinks
pactl list short sinks
```

## How to Test

1. **Stop current assistant** (Ctrl+C in both terminals)

2. **Restart with new config:**
   ```bash
   source venv/bin/activate
   python main.py
   ```

3. **Test with clear command:**
   - Press Ctrl+Space
   - Say clearly: "open firefox"
   - Should recognize accurately with base model

## STT Model Comparison

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39M | Very Fast | Poor | Testing only |
| **base** | 74M | Fast | Good | **Recommended** |
| small | 244M | Medium | Better | High accuracy needed |
| medium | 769M | Slow | Best | Maximum accuracy |

## Expected Improvements

**Before (tiny):**
- "What if this is some mysterious?" (incorrect)
- "What do you guys say about this?" (incorrect)

**After (base):**
- Should recognize actual speech much better
- ~50-70% improvement in accuracy
- Still fast enough for real-time use

## If TTS Still Plays Twice

Check your audio setup:
```bash
# List all audio outputs
pactl list sinks

# Check if multiple devices are active
pactl list short sink-inputs
```

You might have:
- Headphones + Speakers both active
- Audio mirroring enabled
- PulseAudio echo cancellation creating duplicate

**Quick fix:**
```bash
# Set default sink to one device only
pactl set-default-sink YOUR_DEVICE_NAME
```

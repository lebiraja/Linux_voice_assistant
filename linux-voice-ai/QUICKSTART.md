# Linux Voice AI Assistant - Quick Start

## First Time Setup

Run this **once** after booting your system (or after logging in):

```bash
cd /home/lebi/projects/VFL/linux-voice-ai
./setup-x11.sh
```

This sets up X11 permissions for Docker. You only need to run this once per session (until you reboot).

---

## Running the Assistant

After running the setup script above, start the assistant with:

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

---

## Using the Assistant

Once running, you'll see:

```
🎙️  Linux Voice AI Assistant v0
============================================================

Press <CTRL>+<SPACE> to speak
Press Ctrl+C to exit
```

**Press Ctrl+Space** and speak your command!

---

## Example Commands

- "Open Firefox"
- "Close Firefox"  
- "What's my CPU usage?"
- "How much RAM do I have?"
- "What's my disk space?"

---

## Stopping the Assistant

**If running in foreground** (`docker compose up`):
- Press `Ctrl+C`

**If running in background** (`docker compose up -d`):
```bash
docker compose down
```

---

## After Reboot

If you reboot your system, you need to run the setup script again:

```bash
./setup-x11.sh
```

Then you can use `docker compose up` as normal.

---

## Alternative: Use start.sh

If you don't want to remember the setup step, you can use:

```bash
./start.sh
```

This script automatically handles X11 permissions and cleanup for you.

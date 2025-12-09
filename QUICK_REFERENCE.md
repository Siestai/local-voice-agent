# Quick Reference Guide 📝

One-page reference for running your local voice agent.

## 🚀 Start Everything (Fresh Start)

```bash
# 1. Start LiveKit Server (in first terminal)
cd ~/Desktop/livekit-voice-agent
make livekit-start

# 2. Wait for server to be ready (check status)
make livekit-status

# 3. Start Voice Agent (in second terminal)
cd ~/Desktop/livekit-voice-agent
source venv/bin/activate
python agent.py dev
```

## ⚡ Common Commands

### LiveKit Server Management
```bash
make livekit-start      # Start server
make livekit-stop       # Stop server
make livekit-restart    # Restart server
make livekit-status     # Check if running
make livekit-logs       # View live logs
```

### Agent Management
```bash
make dev                # Run agent in dev mode
make console            # Run in terminal mode (no LiveKit room)
make test-components    # Test STT/LLM/TTS individually
make check-env          # Verify .env configuration
make logs               # View agent logs
```

### Development
```bash
make install            # Install dependencies
make setup              # Create project directories
make clean              # Clean cache files
make format             # Format code
make doctor             # Run all health checks
```

## 🔍 Troubleshooting Quick Fixes

### Server Won't Start
```bash
# Check Docker is running
docker info

# Start Docker Desktop
open -a Docker

# Clean and restart
docker-compose down -v
docker-compose up -d
```

### Agent Can't Connect
```bash
# Check server is running
curl http://localhost:7880

# Verify environment variables
make check-env

# Check .env has these values:
# LIVEKIT_URL=ws://localhost:7880
# LIVEKIT_API_KEY=devkey
# LIVEKIT_API_SECRET=secret
```

### Port Already in Use
```bash
# Find what's using port 7880
lsof -i :7880

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Out of Memory
```bash
# Use smaller models in .env:
# LLM_MODEL=mlx-community/Mistral-7B-Instruct-v0.3-4bit
# STT_MODEL=mlx-community/distil-whisper-large-v3
```

### Models Taking Long to Download
```bash
# Models cache to ~/.cache/huggingface/
# First run downloads ~15GB
# Be patient, subsequent runs are fast
```

## 📋 Required Configuration

### .env File Must Have:
```bash
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

### Voice Cloning (Optional):
```bash
# 1. Prepare audio file (3-15 seconds, .wav)
# 2. Create transcript text file
# 3. Run encoder
python setup_voice_clone.py voice_clones/my_voice.wav voice_clones/my_voice.txt

# 4. Update .env
VOICE_CLONE_CODES=./voice_clones/my_voice.pt
VOICE_CLONE_TEXT=./voice_clones/my_voice.txt
```

## 🔗 Important URLs

- **WebSocket**: `ws://localhost:7880`
- **HTTP API**: `http://localhost:7881`
- **Health Check**: `http://localhost:7880`

## 📊 System Requirements

- **Mac M4** (or Apple Silicon)
- **16GB+ RAM** recommended
- **50GB+ free space** (for models)
- **Docker Desktop** running
- **Python 3.11+**
- **espeak** installed (`brew install espeak`)

## 🎯 Testing Flow

```bash
# 1. Test LiveKit server
curl http://localhost:7880

# 2. Test environment
make check-env

# 3. Test components individually
make test-components

# 4. Run in console mode (no LiveKit needed)
python agent.py console

# 5. Run full agent (requires LiveKit)
python agent.py dev
```

## 📁 Important Files

```
livekit-voice-agent/
├── agent.py                    # Main agent code
├── .env                        # YOUR configuration (private)
├── docker-compose.yml          # LiveKit server setup
├── livekit.yaml               # Server configuration
├── requirements.txt           # Python dependencies
├── Makefile                   # All commands
├── DOCKER_SETUP.md            # Docker guide
├── QUICKSTART.md              # Getting started
└── README.md                  # Full documentation
```

## 🛠️ First-Time Setup

```bash
# 1. Install system dependencies
brew install espeak

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Install NeuTTS
make install-neutts

# 5. Create .env file (if not exists)
# Copy values from .env.example

# 6. Setup voice cloning (optional)
make setup-voice

# 7. Start LiveKit server
make livekit-start

# 8. Run the agent
make dev
```

## 🔄 Daily Workflow

```bash
# Morning startup
make livekit-start              # Start server
source venv/bin/activate        # Activate Python env
make dev                        # Run agent

# During development
make livekit-logs              # Monitor server
make logs                      # Monitor agent

# End of day
make livekit-stop              # Stop server
deactivate                     # Deactivate Python env
```

## 💡 Pro Tips

1. **Keep two terminals open**: One for LiveKit server logs, one for agent
2. **Test in console mode first**: Faster iteration without LiveKit room
3. **Use `make doctor`**: Checks everything before running
4. **Monitor logs**: Use `make livekit-logs` and `make logs`
5. **Backup configs**: Use `make backup` before major changes

## 🚨 Emergency Reset

```bash
# Nuclear option - reset everything
make livekit-stop              # Stop server
docker-compose down -v         # Remove containers
make clean                     # Clean Python cache
# Then restart from scratch
make livekit-start
make dev
```

## 📞 Getting Help

1. Check relevant docs:
   - Docker issues → `DOCKER_SETUP.md`
   - First-time setup → `QUICKSTART.md`
   - Full details → `README.md`

2. Check logs:
   ```bash
   make livekit-logs     # Server logs
   make logs             # Agent logs
   ```

3. Run diagnostics:
   ```bash
   make doctor           # Full system check
   make check-env        # Environment check
   make info             # System info
   ```

## 🎉 Success Indicators

You know everything is working when:
- ✅ `make livekit-status` shows "Server is running and healthy"
- ✅ Agent logs show "Voice agent started and ready!"
- ✅ No errors in either terminal
- ✅ You can hear the agent's greeting when connecting

---

**Quick Start**: `make livekit-start` → `make dev` → Start talking! 🎤


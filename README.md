# Local Voice Agent for LiveKit 🎙️

A fully local voice agent running STT-LLM-TTS pipeline optimized for Mac M4 with Apple Silicon. Features voice cloning capabilities using NeuTTS Air.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Voice Agent Pipeline                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Audio Input → VAD → STT → LLM → TTS → Audio Output   │
│                ↓      ↓     ↓     ↓                    │
│              Silero  MLX   MLX  NeuTTS                 │
│                    Whisper Llama  Air                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          ↕
                   LiveKit Server
                  (ws://localhost:7880)
```

### Components

- **VAD**: Silero Voice Activity Detection
- **STT**: Whisper Large V3 Turbo (MLX optimized)
- **LLM**: Llama 3.1 8B Instruct (MLX 4-bit quantized)
- **TTS**: NeuTTS Air (GGUF Q4 with voice cloning)

## 📋 Prerequisites

### System Requirements
- **Mac M4** (or other Apple Silicon Mac)
- **macOS** 13.0 or later
- **Python** 3.11 or later
- **16GB+ RAM** recommended (8GB minimum)
- **50GB+ free disk space** (for models)

### Software Requirements
- Docker Desktop (for LiveKit server)
- Homebrew (for espeak)

## 🐳 LiveKit Server Setup (Docker)

**NEW**: We now include a Docker Compose setup for easy local LiveKit server management!

### Quick Start
```bash
# Start LiveKit server
make livekit-start

# Check status
make livekit-status

# View logs
make livekit-logs

# Stop server
make livekit-stop
```

The server will be available at:
- **WebSocket**: `ws://localhost:7880` (default in .env)
- **HTTP API**: `http://localhost:7881`

**📖 Full Docker documentation**: See [`DOCKER_SETUP.md`](DOCKER_SETUP.md)

## 🚀 Installation

### 1. Clone or Copy This Project

```bash
# Navigate to your projects directory
cd ~/Desktop
# The project should already be here as 'livekit-voice-agent'
cd livekit-voice-agent
```

### 2. Install System Dependencies

```bash
# Install espeak (required for NeuTTS)
brew install espeak

# Verify installation
espeak --version
```

### 3. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4. Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# This will install:
# - LiveKit SDK and agents framework
# - MLX framework and models
# - Whisper MLX
# - Audio processing libraries
# - And more...
```

**Note**: Installation may take 10-20 minutes as it downloads several packages.

### 5. Install NeuTTS Air

```bash
# Clone and install NeuTTS Air
git clone https://github.com/neuphonic/neutts-air.git /tmp/neutts-air
cd /tmp/neutts-air
pip install -e .
cd -
```

### 6. Setup Environment Variables

```bash
# Copy the example .env (already created)
# Edit .env file with your preferences
nano .env

# Key variables to check:
# - LIVEKIT_URL=ws://localhost:7880
# - LIVEKIT_API_KEY=devkey
# - LIVEKIT_API_SECRET=secret
```

## 🎤 Voice Cloning Setup

### Prepare Reference Audio

You need a reference audio sample for voice cloning:

1. **Record or find a clean audio sample** (3-15 seconds)
   - Mono channel
   - 16-44 kHz sample rate
   - Minimal background noise
   - Natural, continuous speech

2. **Create a text transcript**
   ```bash
   echo "This is the exact text spoken in the audio file." > voice_clones/reference.txt
   ```

3. **Run the setup script**
   ```bash
   # Encode the voice
   python setup_voice_clone.py \
     voice_clones/reference.wav \
     voice_clones/reference.txt

   # This will create:
   # - voice_clones/reference.pt (encoded voice)
   # - voice_clones/reference.txt (transcript)
   ```

4. **Update .env**
   ```bash
   VOICE_CLONE_CODES=./voice_clones/reference.pt
   VOICE_CLONE_TEXT=./voice_clones/reference.txt
   ```

### Using Sample Voices

The project includes sample reference files:
```bash
# Use the included samples (if available)
python setup_voice_clone.py \
  voice_clones/sample.wav \
  voice_clones/sample.txt
```

## 🏃 Running the Agent

### 1. Start LiveKit Server

First, start the LiveKit server using Docker Compose:

```bash
# Start the server (runs in background)
make livekit-start

# Verify it's running
make livekit-status
# Should show: "Server is running and healthy"
```

### 2. Start the Voice Agent

```bash
# Make sure you're in the agent directory
cd ~/Desktop/livekit-voice-agent

# Activate virtual environment
source venv/bin/activate

# Run the agent in development mode
python agent.py dev

# Or run in console mode (terminal only, no LiveKit room)
python agent.py console
```

### 3. Connect a Client

You can connect via:
- **Web browser**: Using LiveKit Meet or custom React app
- **Mobile app**: Using LiveKit iOS/Android SDK
- **Console mode**: Direct terminal interaction (for testing)

## 🧪 Testing

### Test Individual Components

```bash
# Test STT (Whisper MLX)
python -c "from stt import WhisperMLXSTT; stt = WhisperMLXSTT(); print('STT OK')"

# Test LLM (MLX)
python -c "from llm import MLXLLM; llm = MLXLLM(); print('LLM OK')"

# Test TTS (NeuTTS Air)
python -c "from tts import NeuTTSAirTTS; tts = NeuTTSAirTTS(); print('TTS OK')"
```

### Test Full Pipeline

```bash
# Run in console mode for testing
python agent.py console

# Speak into your microphone
# The agent should respond with cloned voice
```

## 📁 Project Structure

```
livekit-voice-agent/
├── agent.py                 # Main agent implementation
├── setup_voice_clone.py     # Voice cloning setup utility
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
├── README.md               # This file
├── stt/                    # Speech-to-Text module
│   ├── __init__.py
│   └── whisper_mlx.py      # Whisper MLX implementation
├── llm/                    # Language Model module
│   ├── __init__.py
│   └── mlx_llm.py          # MLX LLM implementation
├── tts/                    # Text-to-Speech module
│   ├── __init__.py
│   └── neutts_air.py       # NeuTTS Air implementation
├── voice_clones/           # Voice reference files
│   ├── reference.wav
│   ├── reference.txt
│   └── reference.pt        # (generated)
├── logs/                   # Log files (generated)
├── backups/                # Configuration backups
└── examples/               # Example scripts
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` to customize:

```bash
# LiveKit Connection
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# Models (can be changed to different MLX models)
STT_MODEL=mlx-community/whisper-large-v3-turbo
LLM_MODEL=mlx-community/Meta-Llama-3.1-8B-Instruct-4bit
TTS_BACKBONE=neuphonic/neutts-air-q4-gguf

# Voice Cloning
VOICE_CLONE_CODES=./voice_clones/reference.pt
VOICE_CLONE_TEXT=./voice_clones/reference.txt

# Pipeline Behavior
ALLOW_INTERRUPTIONS=true
INTERRUPT_SPEECH_DURATION=0.5

# System Prompt
SYSTEM_PROMPT="You are a helpful voice assistant..."
```

### Model Selection

You can use different models from HuggingFace:

**STT Models (Whisper MLX)**:
- `mlx-community/whisper-large-v3-turbo` (recommended, fast)
- `mlx-community/whisper-large-v3`
- `mlx-community/distil-whisper-large-v3`

**LLM Models (MLX)**:
- `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit` (recommended)
- `mlx-community/Mistral-7B-Instruct-v0.3-4bit`
- `mlx-community/gemma-2-9b-it-4bit`

**TTS Models (NeuTTS Air)**:
- `neuphonic/neutts-air-q4-gguf` (recommended, faster)
- `neuphonic/neutts-air-q8-gguf` (better quality)
- `neuphonic/neutts-air` (full precision)

## 📊 Performance

Expected performance on **Mac M4 Max (128GB RAM)**:

| Component | Latency | Memory |
|-----------|---------|--------|
| VAD | ~10ms | ~100MB |
| STT (Whisper) | ~300-500ms | ~2GB |
| LLM (Llama 8B) | ~50-100ms/token | ~5GB |
| TTS (NeuTTS) | ~400-800ms | ~3GB |
| **Total RTT** | **~2-3s** | **~10GB** |

### Optimization Tips

1. **Use quantized models**: 4-bit models are 4x smaller and faster
2. **Pre-encode voices**: Use `.pt` files instead of encoding on-the-fly
3. **Adjust chunk sizes**: Tune STT buffer duration for your needs
4. **Reduce max_tokens**: Lower for faster responses
5. **Use turbo models**: Like `whisper-large-v3-turbo`

## 🔧 Troubleshooting

### Common Issues

#### 1. Models not downloading
```bash
# Manually download models
python -c "import mlx_whisper; mlx_whisper.transcribe('test.wav', path_or_hf_repo='mlx-community/whisper-large-v3-turbo')"
```

#### 2. espeak not found
```bash
# Install espeak
brew install espeak

# Set library path (if needed)
export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak.dylib
```

#### 3. Out of memory
- Use smaller models (4-bit quantized)
- Close other applications
- Restart Python process

#### 4. Connection refused to LiveKit
```bash
# Check if LiveKit server is running
make livekit-status

# Or check manually
curl http://localhost:7880

# Start server if needed
make livekit-start

# View server logs for errors
make livekit-logs
```

#### 5. Audio device issues
```bash
# List audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Grant microphone permissions in System Settings
```

### Debug Mode

Enable debug logging:
```bash
# In .env
LOG_LEVEL=DEBUG

# Or run with debug flag
LOG_LEVEL=DEBUG python agent.py dev
```

## 🔐 Security Notes

This is configured for **local development only**:

- ✅ All processing happens on your Mac
- ✅ No data sent to external servers
- ✅ Complete privacy
- ⚠️ Default API keys (change for production!)
- ⚠️ No TLS encryption (local only)

## 🚢 Deployment

### For Production Use

1. **Change API keys** in LiveKit server config
2. **Enable TLS** for secure connections
3. **Add authentication** to prevent unauthorized access
4. **Monitor resources** (CPU, RAM, GPU)
5. **Set up logging** for debugging
6. **Add rate limiting** to prevent abuse

## 📚 Additional Resources

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents Guide](https://docs.livekit.io/agents/)
- [MLX Framework](https://github.com/ml-explore/mlx)
- [NeuTTS Air](https://github.com/neuphonic/neutts-air)
- [Whisper MLX](https://github.com/ml-explore/mlx-examples/tree/main/whisper)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more voice samples
- [ ] Implement streaming TTS
- [ ] Add function calling support
- [ ] Create web UI
- [ ] Add conversation history
- [ ] Implement RAG capabilities

## 📝 License

This project structure and custom code: MIT License

Dependencies have their own licenses:
- LiveKit: Apache 2.0
- NeuTTS Air: Apache 2.0
- MLX: MIT
- Whisper: MIT

## 🐛 Issues & Support

For issues:
1. Check the troubleshooting section
2. Review logs in `logs/` directory
3. Verify environment configuration
4. Test components individually

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Setup voice cloning
3. ✅ Start LiveKit server
4. ✅ Run the agent
5. 🎉 Build amazing voice AI apps!

---

**Built with ❤️ for SiestAi**

*Helping humans get their siesta while AI works locally on their Mac M4* 🌙

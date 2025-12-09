# Quick Start Guide 🚀

Get your local voice agent running in 5 minutes!

## Step 1: Install Dependencies (5 minutes)

```bash
# Navigate to project
cd ~/Desktop/livekit-voice-agent

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install espeak (required for TTS)
brew install espeak

# Install Python packages
pip install -r requirements.txt

# Install NeuTTS Air
make install-neutts
```

## Step 2: Setup Voice Cloning (2 minutes)

```bash
# Prepare your reference audio (3-15 seconds, .wav)
# Example: Record yourself saying something natural

# Create transcript
echo "Hello, this is my voice. I'm testing the voice cloning system." > voice_clones/my_voice.txt

# Encode the voice
python setup_voice_clone.py \
  voice_clones/my_voice.wav \
  voice_clones/my_voice.txt

# Update .env
# Change these lines:
VOICE_CLONE_CODES=./voice_clones/my_voice.pt
VOICE_CLONE_TEXT=./voice_clones/my_voice.txt
```

## Step 3: Start LiveKit Server (30 seconds)

```bash
# In a new terminal window
cd ~/Desktop/livekit-local-setup
make start

# Wait for server to start
# Check status: make status
```

## Step 4: Run the Agent! (30 seconds)

```bash
# Back in agent directory
cd ~/Desktop/livekit-voice-agent
source venv/bin/activate

# Test components first
python examples/test_components.py

# If all tests pass, run the agent
python agent.py dev
```

## Step 5: Connect & Talk

### Option A: Console Mode (Fastest)
```bash
python agent.py console
# Speak into your microphone when prompted
```

### Option B: Web Browser
1. Open the LiveKit Meet demo or custom frontend
2. Enter room: `test-room`
3. Use token from LiveKit server
4. Start talking!

### Option C: Custom App
Use LiveKit React components or mobile SDK

## Troubleshooting

### Models taking too long to download?
Models are cached in `~/.cache/huggingface/`. First run downloads ~15GB of models.

### espeak not found?
```bash
brew install espeak
```

### Out of memory?
Use smaller models in `.env`:
```bash
LLM_MODEL=mlx-community/Mistral-7B-Instruct-v0.3-4bit
STT_MODEL=mlx-community/distil-whisper-large-v3
```

### LiveKit connection refused?
```bash
# Check if server is running
curl http://localhost:7880

# Start server if needed
cd ../livekit-local-setup && make start
```

## Next Steps

- Customize system prompt in `.env`
- Try different voices
- Adjust pipeline parameters
- Build a custom UI
- Add function calling

## Resources

- Full README: `README.md`
- Test components: `python examples/test_components.py`
- Check system: `make doctor`
- View logs: `make logs`

---

**Need help?** Check the troubleshooting section in README.md

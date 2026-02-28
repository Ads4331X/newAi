# Miku AI Assistant for Ubuntu

An AI-powered desktop assistant with Live2D Miku avatar, voice interaction, and full system control.

![Miku Assistant](screenshot.png)

## Features

- 🎤 **Voice Input (STT)** - Offline speech recognition via Whisper (faster-whisper)
- 🔊 **Voice Output (TTS)** - Anime-style voice via Kokoro TTS (offline, no API needed)
- 🤖 **AI Chat** - Powered by Ollama (qwen2.5:1.5b or gemma3:4b)
- 💻 **System Control** - Open any app, manage files, run commands, control WiFi/Bluetooth/night light
- 🎭 **Live2D Avatar** - Interactive Miku character
- 🖥️ **Always-on-top** - Transparent, draggable window

---

## System Requirements

- **OS**: Ubuntu 24.04 (or similar Debian-based)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: ~5GB free space
- **Python**: 3.11
- **Node.js**: 18+
- **GPU**: Optional (CPU works fine)

---

## Prerequisites

### 1. Install Python 3.11

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. Install Node.js & npm

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Pull the AI model:**

```bash
ollama pull qwen2.5:1.5b
# or for better quality:
ollama pull gemma3:4b
```

### 4. Install System Dependencies

```bash
sudo apt install -y xdotool alsa-utils ffmpeg portaudio19-dev
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/Ads4331X/newAi.git
cd newAi
```

### 2. Backend Setup (Python)

```bash
# Create Python 3.11 virtual environment
python3.11 -m venv .venv_tts

# Activate venv
source .venv_tts/bin/activate

# Install Python dependencies
pip install ollama faster-whisper sounddevice numpy kokoro-onnx soundfile
```

### 3. Download Voice Models

The TTS model files are too large for GitHub. Download them manually:

```bash
mkdir -p backend/voices
cd backend/voices

# Download Kokoro TTS models
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

cd ../..
```

### 4. Frontend Setup (Electron)

```bash
cd frontend
npm install
cd ..
```

---

## Configuration

### 1. Set Python Path in Electron

Edit `frontend/electron/main.js` and update the python path:

```javascript
pythonPath: "/home/YOUR_USERNAME/git_projects/newAi/.venv_tts/bin/python",
```

Replace `YOUR_USERNAME` with your actual username.

### 2. Check Display Variable

```bash
echo $DISPLAY
```

If it's NOT `:0`, edit `backend/system_commands.py` and update:

```python
env={**os.environ, 'DISPLAY': ':0'}
```

---

## Running the App

### Method 1: Manual Start

**Terminal 1 - Start Ollama (if not running):**

```bash
ollama serve
```

**Terminal 2 - Start the App:**

```bash
cd ~/git_projects/newAi
source .venv_tts/bin/activate
cd frontend
npm start
```

### Method 2: Auto-activate venv (Recommended)

Install direnv:

```bash
sudo apt install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
```

Create `.envrc` in project root:

```bash
cd ~/git_projects/newAi
echo "source .venv_tts/bin/activate" > .envrc
direnv allow
```

Now just:

```bash
cd ~/git_projects/newAi/frontend
npm start
```

---

## Usage

### Voice Input

Click the mic button and speak. Whisper will transcribe your voice offline and send it to the AI.

### Text Input

Type in the input box and press Enter.

### Example Commands

| You say                | What happens                  |
| ---------------------- | ----------------------------- |
| "hi"                   | Miku greets you               |
| "open chrome"          | Opens Google Chrome           |
| "open files"           | Opens file manager (Nautilus) |
| "open calculator"      | Opens GNOME Calculator        |
| "open filezilla"       | Opens FileZilla               |
| "install vlc"          | Installs VLC via apt          |
| "update system"        | Runs apt update & upgrade     |
| "what time is it"      | Shows time notification       |
| "disk space"           | Shows disk usage              |
| "battery"              | Shows battery percentage      |
| "volume up / down"     | Adjusts system volume         |
| "mute"                 | Toggles mute                  |
| "wifi on / off"        | Toggles WiFi                  |
| "bluetooth on / off"   | Toggles Bluetooth             |
| "night light on / off" | Toggles night light           |
| "screenshot"           | Takes a screenshot            |
| "empty trash"          | Empties the trash             |

### Power Commands (type directly)

- `SHUTDOWN` - Shuts down system
- `RESTART` - Restarts system
- `SUSPEND` - Suspends system
- `LOCK` - Locks screen
- `LOGOUT` - Logs out

---

## Troubleshooting

### No Voice Output

1. Test TTS standalone:

```bash
cd backend
/home/YOUR_USERNAME/git_projects/newAi/.venv_tts/bin/python -c "import tts_speak; tts_speak.tts_speak('Hello I am Miku')"
```

2. Check audio device:

```bash
aplay -l
```

3. Verify model files exist:

```bash
ls backend/voices/
# Should show: kokoro-v1.0.onnx  voices-v1.0.bin
```

### No Voice Input (Mic not working)

1. Test microphone:

```bash
arecord -d 3 test.wav && aplay test.wav
```

2. Check mic permissions in system settings.

### Apps Not Opening

1. Verify display:

```bash
echo $DISPLAY
```

2. Update `system_commands.py` with correct display value (`:0` or `:1`)

3. Test manually:

```bash
DISPLAY=:0 nautilus &
```

### Import Errors

Ensure correct venv is activated:

```bash
which python
# Should show: /home/username/git_projects/newAi/.venv_tts/bin/python
```

### Out of Storage

```bash
pip cache purge
sudo apt clean
sudo apt autoremove
```

---

## Project Structure

```
newAi/
├── backend/
│   ├── main.py                      # Main AI logic & tag processing
│   ├── system_commands.py           # System command executor (with app finder)
│   ├── power_commands.py            # Power management
│   ├── tts_speak.py                 # Kokoro TTS with parallel playback
│   ├── stt_listen.py                # Whisper STT with silence detection
│   └── data/
│       └── conversation_history.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # Main UI + mic button
│   │   └── components/
│   │       └── Model.jsx            # Live2D renderer
│   ├── electron/
│   │   ├── main.js                  # Electron main process
│   │   └── preload.js               # IPC bridge
│   └── public/
│       └── models/                  # Live2D Miku model
└── .venv_tts/                       # Python virtual environment (not in git)
```

> **Note:** `backend/voices/` directory (TTS model files) is excluded from git due to file size. Download them manually as described in Installation.

---

## Technologies Used

- **AI**: Ollama (qwen2.5:1.5b / gemma3:4b)
- **STT**: faster-whisper (offline Whisper)
- **TTS**: Kokoro ONNX (offline anime-style voice)
- **Frontend**: React + Electron
- **Live2D**: pixi-live2d-display-advanced
- **Backend**: Python 3.11

---

## Performance Notes

- **First TTS call**: ~2-3 seconds (model loading)
- **Subsequent calls**: ~0.3-1 second per sentence
- **STT**: ~1-2 seconds per transcription
- **RAM usage**: ~2-4GB (with models loaded)

---

## Credits

- **Live2D Model**: Miku Sample T04
- **AI Model**: Ollama / Google Gemma / Alibaba Qwen
- **TTS**: Kokoro ONNX by thewh1teagle
- **STT**: faster-whisper by SYSTRAN

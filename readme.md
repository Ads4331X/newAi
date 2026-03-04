# Miku AI Assistant for Ubuntu

An AI-powered desktop assistant with Live2D Miku avatar, voice interaction, full system control, and persistent memory.

![Miku Assistant](screenshot.png)

## Features

- 🎤 **Voice Input (STT)** - Offline speech recognition via Whisper (faster-whisper)
- 🔊 **Voice Output (TTS)** - Anime-style voice via Kokoro TTS (fully offline)
- 🤖 **AI Chat** - Powered by Ollama (gemma3:4b)
- 💻 **Full System Control** - Open any app, run any command, control WiFi/Bluetooth/volume/night light
- 🧠 **Persistent Memory** - Remembers your name, preferences, and habits across sessions
- 🎭 **Live2D Avatar** - Interactive Miku character with idle/tap/flick animations
- 🖥️ **Always-on-top** - Transparent, draggable window
- 🔕 **Interrupt TTS** - New prompt cancels current speech instantly

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

Pull the AI model:

```bash
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
python3.11 -m venv .venv_tts
source .venv_tts/bin/activate
pip install ollama faster-whisper sounddevice numpy kokoro-onnx soundfile
```

### 3. Download Voice Models

Model files are too large for GitHub. Download manually:

```bash
mkdir -p backend/voices
cd backend/voices
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ../..
```

### 4. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 5. Initialize Data Files

```bash
echo '[]' > backend/data/conversation_history.json
echo '{}' > backend/data/memory.json
```

---

## Configuration

### 1. Set Python Path in Electron

Edit `frontend/electron/main.js` and update:

```javascript
pythonPath: "/home/YOUR_USERNAME/git_projects/newAi/.venv_tts/bin/python",
```

### 2. Check Display Variable

```bash
echo $DISPLAY
```

Update `frontend/electron/main.js` env section with your display value (`:0` or `:1`).

---

## Running the App

### Start Ollama (if not running)

```bash
ollama serve &
```

### Start Miku

```bash
cd ~/git_projects/newAi/frontend
source ../.venv_tts/bin/activate
npm start
```

### Run in background (no terminal needed)

```bash
bash /home/YOUR_USERNAME/git_projects/newAi/start.sh
```

### Auto-start on boot

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/miku.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Miku AI
Exec=/home/YOUR_USERNAME/git_projects/newAi/start.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

---

## Usage

### Voice Input

Click the mic button (turns red while recording) and speak. Whisper transcribes offline.

### Text Input

Type in the input box and press Enter.

### Memory

Miku automatically remembers important things you tell her:

- "my name is Zenith" → remembers your name forever
- "I prefer dark mode" → remembers your preferences
- "my work folder is ~/projects" → remembers your paths

### Example Commands

| You say                | What happens                    |
| ---------------------- | ------------------------------- |
| "hi"                   | Miku greets you by name         |
| "open chrome"          | Opens Google Chrome             |
| "open files"           | Opens Nautilus file manager     |
| "open calculator"      | Opens GNOME Calculator          |
| "install vlc"          | Installs VLC via apt            |
| "update system"        | Runs apt update & upgrade       |
| "what time is it"      | Shows desktop notification      |
| "disk space"           | Shows disk usage                |
| "battery"              | Shows battery percentage        |
| "volume up / down"     | Adjusts system volume           |
| "mute"                 | Toggles mute                    |
| "wifi on / off"        | Toggles WiFi                    |
| "bluetooth on / off"   | Toggles Bluetooth               |
| "night light on / off" | Toggles night light             |
| "screenshot"           | Takes a screenshot              |
| "empty trash"          | Empties the trash               |
| "my name is X"         | Remembers your name permanently |

### Power Commands (type directly)

- `SHUTDOWN` - Shuts down system
- `RESTART` - Restarts system
- `SUSPEND` - Suspends system
- `LOCK` - Locks screen
- `LOGOUT` - Logs out

---

## Troubleshooting

### No Voice Output

```bash
cd backend
/home/YOUR_USERNAME/git_projects/newAi/.venv_tts/bin/python -c "import tts_speak; tts_speak.tts_speak('Hello I am Miku')"
```

Verify model files:

```bash
ls backend/voices/
# Should show: kokoro-v1.0.onnx  voices-v1.0.bin
```

### No Voice Input

```bash
arecord -d 3 test.wav && aplay test.wav
```

If mic is too quiet, adjust `SILENCE_THRESHOLD` in `backend/stt_listen.py`.

### Apps Not Opening

Check your display:

```bash
echo $DISPLAY
```

Update the `DISPLAY` value in `frontend/electron/main.js` env config.

### Memory Not Saving

```bash
cat backend/data/memory.json
```

If empty, initialize it:

```bash
echo '{}' > backend/data/memory.json
```

### Reset Everything

```bash
echo '[]' > backend/data/conversation_history.json
echo '{}' > backend/data/memory.json
```

---

## Project Structure

```
newAi/
├── backend/
│   ├── main.py                  # Main AI logic & tag processing
│   ├── system_commands.py       # System command executor
│   ├── power_commands.py        # Power management
│   ├── tts_speak.py             # Kokoro TTS with parallel playback
│   ├── stt_listen.py            # Whisper STT with silence detection
│   ├── memory.py                # Persistent memory manager
│   └── data/
│       ├── conversation_history.json
│       └── memory.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main UI + mic button
│   │   └── components/
│   │       ├── Model.jsx        # Live2D renderer with animations
│   │       └── ResponseBox.jsx  # Response display
│   ├── electron/
│   │   ├── main.js              # Electron main process
│   │   └── preload.js           # IPC bridge
│   └── public/
│       └── models/              # Live2D Miku model files
└── .venv_tts/                   # Python venv (not in git)
```

> **Note:** `backend/voices/` and `.venv_tts/` are excluded from git. Download voice models manually as described above.

---

## Technologies Used

- **AI**: Ollama (gemma3:4b)
- **STT**: faster-whisper (offline Whisper)
- **TTS**: Kokoro ONNX (offline anime-style voice)
- **Frontend**: React + Electron
- **Live2D**: pixi-live2d-display-lipsyncpatch
- **Backend**: Python 3.11

---

## Performance Notes

- **First TTS call**: ~2-3 seconds (model loading)
- **Subsequent TTS**: ~0.3-1 second per sentence
- **STT transcription**: ~1-2 seconds
- **AI response**: ~2-5 seconds (gemma3:4b on CPU)
- **RAM usage**: ~3-5GB with all models loaded

---

## Credits

- **Live2D Model**: Miku Sample T04
- **AI**: Ollama / Google Gemma
- **TTS**: Kokoro ONNX by thewh1teagle
- **STT**: faster-whisper by SYSTRAN

# Miku AI Assistant for Ubuntu

An AI-powered desktop assistant with Live2D Miku avatar, voice interaction, and full system control.

![Miku Assistant](screenshot.png)

## Features

- 🎤 **Voice TTS** - Coqui TTS with natural female voice
- 🤖 **AI Chat** - Powered by Ollama (Gemma 3:4b)
- 💻 **System Control** - Open apps, manage files, run commands
- 🎭 **Live2D Avatar** - Interactive Miku character
- 🖥️ **Always-on-top** - Transparent, draggable window

---

## System Requirements

- **OS**: Ubuntu 24.04 (or similar Debian-based)
- **RAM**: 16GB recommended
- **Storage**: ~15GB free space
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
ollama pull gemma3:4b
```

### 4. Install System Dependencies

```bash
sudo apt install -y xdotool aplay mpg123
```

---

## Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd newAi
```

### 2. Backend Setup (Python)

```bash
# Create Python 3.11 virtual environment
python3.11 -m venv .venv_tts

# Activate venv
source .venv_tts/bin/activate

# Install Python dependencies
pip install ollama requests TTS torch==2.3.0 torchaudio==2.3.0

# Install Japanese TTS support
pip install TTS[ja]
```

### 3. Frontend Setup (Electron)

```bash
cd frontend

# Install dependencies
npm install

# Return to project root
cd ..
```

---

## Configuration

### 1. Set Python Path in Electron

Edit `frontend/electron/main.js` and update line 22:

```javascript
pythonPath: "/home/YOUR_USERNAME/git_projects/newAi/.venv_tts/bin/python",
```

Replace `YOUR_USERNAME` with your actual username.

### 2. Check Display Variable

```bash
echo $DISPLAY
```

If it's NOT `:1`, edit `backend/system_commands.py` line 13:

```python
bash_file.write("export DISPLAY=:YOUR_DISPLAY\n")
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

### Voice Commands

- **"open chrome"** - Opens Google Chrome
- **"open files"** - Opens file manager
- **"open terminal"** - Opens terminal
- **"calculate 2+2"** - Performs calculation
- **"what is my ip"** - Shows IP address
- **"make folder test in downloads"** - Creates folder
- **"minimize window"** - Minimizes current window

### Chat

- **"hello"** - Greet Miku
- **"how to install vlc"** - Get instructions

### System Commands

Type directly:

- `SHUTDOWN` - Shuts down system
- `RESTART` - Restarts system
- `LOCK` - Locks screen

---

## Troubleshooting

### No Voice Output

1. Check audio device:

```bash
aplay -l
```

2. Test audio:

```bash
speaker-test -t wav -c 2
```

3. Check TTS installation:

```bash
python -c "from TTS.api import TTS; print('TTS OK')"
```

### Apps Not Opening

1. Verify display:

```bash
echo $DISPLAY
```

2. Update `system_commands.py` with correct display

3. Test manually:

```bash
DISPLAY=:1 nautilus &
```

### Import Errors

Ensure correct venv is activated:

```bash
which python
# Should show: /home/username/git_projects/newAi/.venv_tts/bin/python
```

### Out of Storage

Free up space:

```bash
# Clean caches
rm -rf ~/.cache/google-chrome
rm -rf ~/.cache/vscode-cpptools
pip cache purge
sudo apt clean
sudo apt autoremove
```

---

## Project Structure

```
newAi/
├── backend/
│   ├── main.py              # Main AI logic
│   ├── system_commands.py   # System command executor
│   ├── power_commands.py    # Power management
│   ├── tts_speak.py         # Text-to-speech
│   └── data/
│       └── conversation_history.json
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main UI
│   │   └── components/
│   │       └── Model.jsx    # Live2D renderer
│   ├── electron/
│   │   ├── main.js          # Electron main process
│   │   └── preload.js       # IPC bridge
│   └── public/
│       └── models/          # Live2D Miku model
└── .venv_tts/               # Python virtual environment
```

---

## Technologies Used

- **AI**: Ollama (Gemma 3:4b)
- **TTS**: Coqui TTS (Tacotron2 + HiFiGAN)
- **Frontend**: React + Electron + Material-UI
- **Live2D**: pixi-live2d-display-advanced
- **Backend**: Python 3.11

---

## Performance Notes

- **First TTS call**: ~5-10 seconds (model loading)
- **Subsequent calls**: ~0.5-2 seconds per sentence
- **RAM usage**: ~2-3GB (with models loaded)
- **Storage**: ~15GB total

---

## Credits

- **Live2D Model**: Miku Sample T04
- **AI Model**: Google Gemma 3
- **TTS**: Coqui TTS (Apache 2.0 license)

---

<!--
## License

MIT License

---

## Support

For issues, please open a GitHub issue with:

- Your Ubuntu version
- Error messages
- Steps to reproduce -->

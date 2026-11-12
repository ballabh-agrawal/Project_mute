# Project Mute - Real-Time Multi-Speaker Transcription

Real-time captioning system for deaf/hard-of-hearing users. Transcribes audio from multiple devices using OpenAI Whisper and displays captions in real-time with speaker identification.

## ✨ Features

- **Real-time transcription**: ~2-3 second latency (Whisper Small model)
- **Multi-device support**: Up to 4 simultaneous speakers
- **Speaker identification**: Shows which device/speaker is talking
- **Web-based**: Browser clients, works on any device with WiFi
- **Offline capable**: Local Whisper model (no API calls required)
- **Session recording**: Automatically saves transcripts to SQLite + JSONL backup
- **Professional UI**: Clean, responsive design for monitors and phones

## 🚀 Quick Start (macOS)

### Prerequisites

- Python 3.9+
- pip
- macOS or Windows

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/project-mute.git
cd project-mute

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR on Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Whisper model (one-time, ~1.4 GB)
python -c "import whisper; whisper.load_model('small')"
```

### Running the Server

```bash
# Activate venv if not already
source venv/bin/activate

# Start server
python -m flask --app src.backend.app run --host=0.0.0.0 --port=5000

# Or directly:
python src/backend/app.py
```

Server will start on `http://localhost:5000`

### Opening Clients (Browser)

**For local testing (on same laptop):**
- Monitor/Dashboard: http://localhost:5000/
- Device A: http://localhost:5000/recorder.html (in Tab 1)
- Device B: http://localhost:5000/recorder.html (in Tab 2)

**For network testing (multiple devices):**

1. Find your laptop's IP:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example output: inet 192.168.1.100
```

2. On phone/second device:
   - Device: `http://192.168.1.100:5000/recorder.html`
   - Monitor: `http://192.168.1.100:5000/`

### Using Pre-recorded Audio

1. Record speaker audio files:
```bash
# Record 60+ seconds of natural speech for each speaker
# Save as: data/recordings/speaker_a.wav
#          data/recordings/speaker_b.wav
# Format: WAV, PCM16, 16kHz, Mono
```

2. In device UI, select "📁 Pre-recorded File" instead of microphone

### Demo Flow

1. **Device A (Speaker 1)**:
   - Open `http://localhost:5000/recorder.html`
   - Enter name: "Alice"
   - Select "🎤 Live Microphone" or "📁 Pre-recorded File"
   - Click "▶ Start Capture"
   - Speak naturally or file plays automatically
   - Captions appear in 2-3 seconds

2. **Device B (Speaker 2)**:
   - Open another tab/device with same URL
   - Enter name: "Bob"
   - Click "▶ Start Capture"
   - Speak or play file
   - Both speakers' captions appear on monitor

3. **Monitor (Deaf User's View)**:
   - Open `http://localhost:5000/`
   - See captions from both speakers in real-time
   - Late entries marked with "earlier" tag
   - Session duration displayed at bottom

4. **End Session**:
   - Click "⏹ Stop" on any device
   - Transcript automatically saved to `data/sessions/sess_*.sqlite`
   - JSONL backup in `data/sessions/sess_*.jsonl`

## 📁 Project Structure

```
project-mute/
├── src/
│   ├── backend/
│   │   ├── app.py              # Flask + SocketIO main server
│   │   ├── models.py           # Entry, SessionCoordinator classes
│   │   ├── storage.py          # SQLite interface
│   │   ├── network.py          # WebSocket message builders
│   │   ├── constants.py        # Config values
│   │   └── workers/
│   │       └── asr_worker.py   # Whisper transcription
│   └── frontend/
│       ├── templates/
│       │   ├── index.html      # Monitor dashboard
│       │   └── recorder.html   # Device recorder UI
│       └── static/
│           ├── js/
│           │   ├── socket-client.js   # WebSocket connection
│           │   ├── audio-capture.js   # Audio input handling
│           │   └── ui.js              # Caption display
│           └── css/
│               └── style.css         # Styling
├── data/
│   ├── recordings/             # Pre-recorded speaker audio (WAV files)
│   └── sessions/               # Saved transcripts (SQLite + JSONL)
├── tests/                      # Unit tests
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

## 🔧 Configuration

Edit `src/backend/constants.py` to customize:

- **ASR_WORKERS**: Number of concurrent transcription jobs (default: 2)
- **LATENCY_CEILING**: Max acceptable delay for captions (default: 5 seconds)
- **OVERLAP_SLACK**: Clock tolerance between devices (default: 0.15 seconds)
- **WHISPER_MODEL**: Model size - "tiny", "base", "small", "medium" (default: "small")
- **HOST/PORT**: Server address (default: 0.0.0.0:5000)

## 🐛 Troubleshooting

### Whisper model not loading
```bash
# Download model manually
python -c "import whisper; whisper.load_model('small')"
```

### Port 5000 already in use
```bash
# Kill the process
lsof -i :5000
kill -9 <PID>

# Or use different port in constants.py
```

### Microphone permission denied
- macOS: System Preferences → Security & Privacy → Microphone
- Browser: Settings → Privacy → Microphone

### Audio quality is poor
- Ensure microphone is close to speaker
- Reduce background noise
- Check browser audio settings (echoCancellation, noiseSuppression enabled)

### Transcription is inaccurate
- Try with cleaner audio (no background noise)
- Ensure 16kHz mono WAV format for pre-recorded files
- Larger Whisper model if time permits: change "small" → "medium" in constants.py

## 🪟 Running on Windows

1. Clone and setup (same as macOS)
2. Activate venv:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download Whisper model:
```bash
python -c "import whisper; whisper.load_model('small')"
```

5. Start server:
```bash
python src/backend/app.py
```

6. Find your Windows laptop IP:
```bash
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)
```

7. On phones: Open `http://192.168.1.100:5000/recorder.html`

## 📊 Architecture

```
                        SERVER (Python/Flask)
┌─────────────────────────────────────────────────────┐
│  WebSocket Hub                                      │
│  ↓                                                  │
│  SessionCoordinator (state management, sync)       │
│  ↓                                                  │
│  ASR Worker Pool (Whisper transcription)           │
│  ↓                                                  │
│  SQLite Storage (transcripts)                      │
└─────────────────────────────────────────────────────┘
          ↑                    ↑                    ↑
    ┌─────┴────┐         ┌────┴────┐         ┌────┴────┐
    │ Device A │         │ Device B │        │ Monitor  │
    │ Browser  │         │ Browser  │        │ Browser  │
    │ Mic/File │         │ Mic/File │        │ Display  │
    └──────────┘         └──────────┘        └──────────┘
```

## 📝 Data Model

### Entry (Single event in system)
- **entry_id**: UUID (unique identifier)
- **session_id**: Session reference
- **source**: "asr" (audio for transcription)
- **device_id**: Which device sent this (device_a, device_b)
- **start_ts / end_ts**: Unix seconds (e.g., 1699603200.123)
- **text**: Transcribed text (after ASR)
- **speaker**: Speaker name (Alice, Bob, or device_id)
- **speaker_confidence**: Confidence score (0.0-1.0)
- **is_final**: True when transcription complete
- **is_late**: True if arrived after 5-second latency ceiling
- **audio_bytes**: Raw PCM16 audio (16kHz mono)
- **quality**: "ok" or "low_quality"
- **created_at**: ISO datetime when entry created

### WebSocket Messages

**Client → Server:**
- `welcome`: Device initialization
- `chunk`: Audio data (400ms)
- `end_session`: User stops recording

**Server → Client:**
- `welcome`: Session established + history
- `caption`: Transcribed text for display
- `text_message`: Status updates
- `session_ended`: Session complete
- `error`: Error notification

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run specific test
pytest tests/test_models.py -v
```

## 📦 Deployment

### Local Network (Hackathon)
```bash
# Run on laptop
python src/backend/app.py

# Clients access via laptop IP
http://192.168.1.100:5000/recorder.html
```

### Production (Future)
- Use Gunicorn: `gunicorn -w 4 src.backend.app:app`
- Add HTTPS (SSL certificate)
- Run behind reverse proxy (nginx)
- Use PostgreSQL instead of SQLite

## 📜 License

MIT License - See LICENSE file

## 👥 Contributors

Built for hackathon. Questions? Check FEASIBILITY_AND_ARCHITECTURE.md

## 🎯 Next Steps

- [ ] Record speaker_a.wav and speaker_b.wav
- [ ] Test locally on macOS
- [ ] Push to GitHub
- [ ] Clone on Windows
- [ ] Run hackathon demo
- [ ] Celebrate! 🎉

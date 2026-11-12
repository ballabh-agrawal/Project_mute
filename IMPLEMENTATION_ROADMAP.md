# IMPLEMENTATION ROADMAP - PROJECT MUTE
**Date**: 2026-11-10  
**Configuration**: Whisper Small + Recorded Demo Files + WiFi Deployment  
**Status**: Ready for Coding

---

## YOUR SPECIFIC SETUP CONFIRMED

✅ **ASR Engine**: OpenAI Whisper Small (English)  
✅ **Audio Input**: Pre-recorded speaker files (will record yourself)  
✅ **Deployment**: One server laptop + 2 phones on same WiFi network  
✅ **Platform**: Browser (HTML/CSS/JS frontend)  
✅ **Scope**: 2 speakers + 1 deaf user monitor  
✅ **Latency Target**: ~2-5 seconds acceptable  

---

## SECTION 1: BEFORE YOU CODE - CHECKLIST

### 1.1 Install Whisper

```bash
# Activate venv
source venv/bin/activate

# Install OpenAI Whisper
pip install openai

# Verify installation
python -c "import openai; print(openai.__version__)"

# Set API key (get from https://platform.openai.com/account/api-keys)
export OPENAI_API_KEY="sk-proj-..."
# Or add to .env file and load with python-dotenv
```

**Cost Estimate**:
- Whisper Small model: ~$0.02 per 15 seconds of audio
- For a 15-minute demo with 2 speakers: ~$0.24 (or less if using free tier credits)
- Free tier: Often includes $5-$18 credits

**Alternative (if hitting API limits)**: Switch to local Whisper
```bash
pip install openai-whisper
# Then use whisper CLI locally (slower, no cost)
python -c "import whisper; model = whisper.load_model('small')"
```

### 1.2 Create Demo Audio Files

**Record yourself speaking**:

```bash
# Option A: Use macOS built-in QuickTime
# Open QuickTime Player → File → New Audio Recording
# Speak 60+ seconds naturally (pretend normal conversation)
# Export as: data/recordings/speaker_a.wav

# Option B: Use ffmpeg + default mic
ffmpeg -f avfoundation -i ":0" -t 60 data/recordings/speaker_a.wav
# (Press Ctrl+C to stop after 60 seconds)

# Option C: Use online text-to-speech (simpler)
# Record yourself saying:
# Speaker A: "Hello, can you hear me? I'm speaking for the first time."
# Speaker B: "Yes I can hear you. How are you today?"
# ...keep going for 60 seconds minimum
```

**Save as**:
```
data/recordings/
├── speaker_a.wav  (60+ seconds)
└── speaker_b.wav  (60+ seconds)
```

**Check files**:
```bash
# Verify files exist and have audio
file data/recordings/speaker_a.wav
# Should output: WAV audio format, 16000 Hz, mono, signed 16-bit

# Check duration
ffprobe -show_entries format=duration data/recordings/speaker_a.wav
# Should output: 60+ seconds
```

### 1.3 Get Your Server's Local IP

```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1
# Look for something like: inet 192.168.1.100

# Linux
hostname -I

# Windows
ipconfig
# Look for: IPv4 Address
```

**Note this IP**: You'll use `http://192.168.x.x:5000` on phones

### 1.4 Set Up Directory Structure

```bash
cd /Users/richa.agrawal1/Desktop/Project_mute

# Create needed directories
mkdir -p src/{backend,frontend}
mkdir -p src/backend/{models,workers,storage}
mkdir -p src/frontend/{static/{js,css},templates}
mkdir -p data/{recordings,sessions}
mkdir -p tests
mkdir -p logs

# Verify structure
tree -L 3 -I '__pycache__|*.pyc'
```

---

## SECTION 2: DEPENDENCY INSTALLATION (COMPLETE)

### 2.1 requirements.txt (Copy & Paste)

```bash
# Create file
cat > requirements.txt << 'EOF'
# Web Framework
Flask==2.3.2
Flask-SocketIO==5.3.4
python-socketio==5.9.0
python-engineio==4.7.1

# Audio Processing
librosa==0.10.0
soundfile==0.12.1
numpy==1.24.3
scipy==1.11.2

# ASR (Whisper)
openai==1.3.6
python-dotenv==1.0.0

# Storage
# (SQLite3 is built-in)

# Utilities
requests==2.31.0
python-dateutil==2.8.2

# Testing
pytest==7.4.0
pytest-asyncio==0.21.1

# Development
black==23.9.1
pylint==2.17.5
EOF

# Install all dependencies
pip install -r requirements.txt
```

### 2.2 Alternative: Minimal Install (if running low on disk)

```bash
# Core only (drop Whisper, use local whisper instead)
pip install Flask Flask-SocketIO python-socketio
pip install librosa soundfile numpy scipy
pip install openai-whisper  # Local Whisper (~3GB)
```

---

## SECTION 3: WHISPER SETUP (DETAILED)

### 3.1 Using Whisper API (Recommended for Hackathon)

```python
# src/backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """All configs in one place."""
    
    # ASR
    ASR_ENGINE = "whisper_api"  # "whisper_api" or "whisper_local"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WHISPER_MODEL = "small"  # "tiny", "base", "small", "medium", "large"
    
    # Audio
    SAMPLE_RATE = 16000
    CHANNELS = 1
    AUDIO_FORMAT = "PCM16"
    CHUNK_DURATION = 0.4  # 400ms chunks
    
    # Server
    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = True
    
    # Storage
    DATA_DIR = "./data"
    SESSIONS_DIR = "./data/sessions"
    RECORDINGS_DIR = "./data/recordings"
    
    # Network
    MAX_DEVICES = 4
    SESSION_TIMEOUT = 15 * 60  # 15 minutes
    LATENCY_CEILING = 5.0
    
    # Sync
    OVERLAP_SLACK = 0.15
    CLOCK_OFFSET_SAMPLES = 5
```

### 3.2 Create .env File

```bash
# .env (Git-ignore this!)
echo 'OPENAI_API_KEY="sk-proj-YOUR-KEY-HERE"' > .env
echo '.env' >> .gitignore

# Load in Python:
# from dotenv import load_dotenv
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
```

### 3.3 Test Whisper Connection

```python
# test_whisper.py
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test API
try:
    response = openai.Model.list()
    print("✓ OpenAI API connected successfully")
    print(f"Available models: {len(response['data'])}")
except Exception as e:
    print(f"✗ API error: {e}")
    print("Get API key: https://platform.openai.com/account/api-keys")
```

Run:
```bash
python test_whisper.py
# Should output: ✓ OpenAI API connected successfully
```

### 3.4 Alternative: Local Whisper (if API limit hit)

```bash
# Install local Whisper
pip install openai-whisper

# Download model (one-time, ~1.4 GB for "small")
python -c "import whisper; whisper.load_model('small')"

# Test
python -c "import whisper; print(whisper.available_models())"
```

```python
# src/backend/workers/asr_worker.py (LOCAL VERSION)
import whisper
import json

class ASRWorker:
    def __init__(self, model_type="whisper_local"):
        self.model = whisper.load_model("small")  # Loads from cache
    
    def process_chunk(self, audio_bytes, entry_id):
        """audio_bytes → (text, confidence)."""
        import tempfile
        import soundfile as sf
        
        # Write bytes to temp WAV
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_bytes, 16000)
            
            # Transcribe
            result = self.model.transcribe(tmp.name, language="en")
            text = result["text"]
            confidence = 0.9  # Whisper doesn't return confidence
            
            return text, confidence
```

---

## SECTION 4: COMPLETE BACKEND IMPLEMENTATION

### 4.1 src/backend/constants.py

```python
"""Shared constants and configuration."""

# Audio
SAMPLE_RATE = 16000  # Hz
AUDIO_FORMAT = "PCM16"  # 16-bit signed
CHANNELS = 1  # Mono
CHUNK_DURATION = 0.4  # seconds (6400 samples at 16kHz)

# ASR
ASR_WORKERS = 2  # Concurrent Whisper jobs
ASR_TIMEOUT = 15  # seconds (Whisper API timeout)

# Sync
OVERLAP_SLACK = 0.15  # seconds (clock tolerance)
CLOCK_OFFSET_SAMPLES = 5
CLOCK_OFFSET_REPEAT_INTERVAL = 60  # seconds
CLOCK_OFFSET_MAX_RTT = 0.5  # seconds

# Network
LATENCY_CEILING = 5.0  # seconds
SESSION_TIMEOUT = 15 * 60  # 15 minutes
HEARTBEAT_INTERVAL = 5  # seconds
MAX_DEVICES_PER_SESSION = 4

# Display
HIGH_THRESHOLD = 0.75  # Speaker confidence
LOW_THRESHOLD = 0.55
LOUDNESS_GATE = -40  # dBFS

# Paths
DATA_DIR = "./data"
SESSIONS_DIR = "./data/sessions"
RECORDINGS_DIR = "./data/recordings"
```

### 4.2 src/backend/models.py

```python
"""Core data models."""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
import uuid
import json
import base64

@dataclass
class Entry:
    """Single event in the system (audio chunk, transcription, metadata)."""
    
    entry_id: str
    session_id: str
    source: str  # "asr", "audio", "metadata", "tts"
    device_id: str
    
    start_ts: float  # Server time when speech began
    end_ts: float    # Server time when speech ended
    
    speaker: Optional[str] = None
    speaker_confidence: Optional[float] = None
    text: Optional[str] = None
    audio_bytes: Optional[bytes] = None
    quality: Optional[str] = None
    
    is_final: bool = False
    is_late: bool = False
    
    connection_epoch: int = 0
    chunk_seq: Optional[int] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    
    @staticmethod
    def create_audio(session_id, device_id, audio_bytes, start_ts, end_ts, quality="ok"):
        """Factory for audio entry."""
        return Entry(
            entry_id=uuid.uuid4().hex,
            session_id=session_id,
            source="asr",  # Audio for ASR processing
            device_id=device_id,
            start_ts=start_ts,
            end_ts=end_ts,
            audio_bytes=audio_bytes,
            quality=quality,
            connection_epoch=0,
            chunk_seq=None,
        )
    
    def to_dict(self):
        """Serialize for JSON transport."""
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        
        # Encode audio as base64 for JSON
        if self.audio_bytes:
            d["audio_bytes"] = base64.b64encode(self.audio_bytes).decode()
        else:
            d["audio_bytes"] = None
        
        return d
    
    @staticmethod
    def from_dict(d):
        """Deserialize from JSON."""
        if "audio_bytes" in d and d["audio_bytes"]:
            d["audio_bytes"] = base64.b64decode(d["audio_bytes"])
        
        d["created_at"] = datetime.fromisoformat(d["created_at"])
        return Entry(**d)


class SessionCoordinator:
    """Manages session state, syncing, buffering, deduplication."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries = {}  # entry_id → Entry
        self.released_entries = []  # Entries sent to UI
        
        # Sync/dedup
        self.seen_chunks = set()  # (device_id, epoch, chunk_seq)
        self.device_clocks = {}  # device_id → time_offset
        self.device_epochs = {}  # device_id → connection_epoch
        
        # Status
        self.active_devices = set()
        self.ended_devices = set()
        self.started_at = datetime.now()
        self.asr_pending = {}  # entry_id → Entry (waiting for ASR)
    
    def receive_audio(self, entry: Entry):
        """Add audio chunk, check for duplicates."""
        key = (entry.device_id, entry.connection_epoch, entry.chunk_seq)
        
        if key in self.seen_chunks:
            print(f"[DEDUP] Ignoring duplicate: {key}")
            return  # Duplicate, ignore
        
        self.seen_chunks.add(key)
        self.entries[entry.entry_id] = entry
        self.asr_pending[entry.entry_id] = entry
        
        return entry.entry_id  # For caller reference
    
    def receive_asr_result(self, entry_id: str, text: str, confidence: float):
        """Update entry with ASR result."""
        if entry_id not in self.entries:
            print(f"[ASR] Entry not found: {entry_id}")
            return
        
        entry = self.entries[entry_id]
        entry.text = text
        entry.speaker_confidence = confidence
        entry.is_final = True
        
        if entry_id in self.asr_pending:
            del self.asr_pending[entry_id]
        
        self.release_entry(entry_id)
    
    def release_entry(self, entry_id: str):
        """Mark entry as ready for UI display."""
        entry = self.entries[entry_id]
        
        # Check if late
        now = datetime.now().timestamp()
        if now - entry.start_ts > LATENCY_CEILING:
            entry.is_late = True
            print(f"[LATE] Entry arrived after {LATENCY_CEILING}s: {entry_id}")
        
        if entry not in self.released_entries:
            self.released_entries.append(entry)
    
    def get_released_entries(self):
        """Get entries ready for display, clear list."""
        entries = self.released_entries[:]
        self.released_entries.clear()
        return entries
    
    def handle_device_connect(self, device_id: str, epoch: int):
        """Device connected."""
        self.active_devices.add(device_id)
        self.device_epochs[device_id] = epoch
        self.device_clocks[device_id] = 0.0
        print(f"[CONNECT] {device_id} (epoch={epoch})")
    
    def handle_device_disconnect(self, device_id: str):
        """Device disconnected."""
        self.active_devices.discard(device_id)
        self.ended_devices.add(device_id)
        print(f"[DISCONNECT] {device_id}")
    
    def is_session_done(self):
        """Check if all devices ended."""
        return len(self.ended_devices) > 0 and len(self.active_devices) == 0
    
    def get_session_duration(self):
        """Time since session started."""
        return (datetime.now() - self.started_at).total_seconds()
    
    def get_all_entries(self):
        """All entries in session (for storage)."""
        return list(self.entries.values())


# Import constants
from .constants import LATENCY_CEILING
```

### 4.3 src/backend/storage.py

```python
"""SQLite storage for sessions."""

import sqlite3
import json
from datetime import datetime
from typing import List
from .models import Entry

class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        """Create tables if not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                ended_at TIMESTAMP,
                devices TEXT,
                total_duration_sec REAL,
                status TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                entry_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                source TEXT NOT NULL,
                device_id TEXT,
                start_ts REAL,
                end_ts REAL,
                speaker TEXT,
                speaker_confidence REAL,
                text TEXT,
                audio_bytes BLOB,
                quality TEXT,
                is_final BOOLEAN,
                is_late BOOLEAN,
                connection_epoch INTEGER,
                chunk_seq INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                UNIQUE(session_id, device_id, connection_epoch, chunk_seq)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_speaker ON entries(session_id, speaker)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_time ON entries(session_id, start_ts)")
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_id: str, devices: List[str], duration: float, entries: List[Entry]):
        """Save session and all entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, created_at, ended_at, devices, total_duration_sec, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now(),
            datetime.now(),
            json.dumps(devices),
            duration,
            "ended"
        ))
        
        for entry in entries:
            cursor.execute("""
                INSERT OR IGNORE INTO entries
                (entry_id, session_id, source, device_id, start_ts, end_ts,
                 speaker, speaker_confidence, text, audio_bytes, quality,
                 is_final, is_late, connection_epoch, chunk_seq, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.entry_id, entry.session_id, entry.source, entry.device_id,
                entry.start_ts, entry.end_ts, entry.speaker, entry.speaker_confidence,
                entry.text, entry.audio_bytes, entry.quality,
                entry.is_final, entry.is_late, entry.connection_epoch,
                entry.chunk_seq, entry.created_at
            ))
        
        conn.commit()
        conn.close()
    
    def save_jsonl_backup(self, session_id: str, entries: List[Entry]):
        """Write JSONL safety copy."""
        path = f"./data/sessions/{session_id}.jsonl"
        with open(path, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry.to_dict()) + "\n")
        print(f"[BACKUP] Saved JSONL: {path}")
```

### 4.4 src/backend/network.py

```python
"""WebSocket message protocol."""

from typing import Dict, Any, List
from datetime import datetime

def build_welcome_response(session_id: str, server_time: float, history: List[Dict]) -> Dict:
    """Server → Client: Session established."""
    return {
        "type": "welcome",
        "session_id": session_id,
        "server_time": server_time,
        "history": history,
    }

def build_caption_message(entry_id: str, device_id: str, speaker: str,
                         text: str, start_ts: float, end_ts: float,
                         is_final: bool, is_late: bool, confidence: float) -> Dict:
    """Server → Client: Transcribed caption."""
    return {
        "type": "caption",
        "entry_id": entry_id,
        "device_id": device_id,
        "speaker": speaker,
        "text": text,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "is_final": is_final,
        "is_late": is_late,
        "confidence": confidence,
    }

def build_text_message(source: str, text: str, timestamp: float) -> Dict:
    """Server → Client: Status/metadata message."""
    return {
        "type": "text_message",
        "source": source,  # "system", "server", etc
        "text": text,
        "timestamp": timestamp,
    }

def build_session_ended(session_id: str, total_duration: float, transcript_saved: bool) -> Dict:
    """Server → Client: Session ended."""
    return {
        "type": "session_ended",
        "session_id": session_id,
        "total_duration": total_duration,
        "transcript_saved": transcript_saved,
        "timestamp": datetime.now().isoformat(),
    }

def build_error(code: str, message: str, device_id: str = None) -> Dict:
    """Server → Client: Error."""
    return {
        "type": "error",
        "code": code,  # "asr_timeout", "connection_lost", "tts_failed"
        "message": message,
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
    }
```

### 4.5 src/backend/workers/asr_worker.py (WHISPER VERSION)

```python
"""ASR worker for transcription."""

import openai
from dotenv import load_dotenv
import os
import tempfile
import soundfile as sf
import json
from queue import Queue
from threading import Thread
import time

load_dotenv()

class ASRWorker:
    def __init__(self, model_type="whisper_api"):
        self.model_type = model_type
        
        if model_type == "whisper_api":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model_name = "small"
        else:
            import whisper
            self.model = whisper.load_model("small")
    
    def process_chunk(self, audio_bytes: bytes, entry_id: str) -> tuple[str, float]:
        """Transcribe audio chunk. Returns: (text, confidence)."""
        
        try:
            if self.model_type == "whisper_api":
                return self._transcribe_api(audio_bytes, entry_id)
            else:
                return self._transcribe_local(audio_bytes, entry_id)
        except Exception as e:
            print(f"[ASR ERROR] {entry_id}: {e}")
            return "[ASR failed]", 0.0
    
    def _transcribe_api(self, audio_bytes: bytes, entry_id: str) -> tuple[str, float]:
        """Use OpenAI Whisper API."""
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            # Write audio to temporary file
            sf.write(tmp.name, audio_bytes, 16000)
            
            # Send to Whisper API
            with open(tmp.name, "rb") as f:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=f,
                    language="en",
                )
            
            text = transcript.get("text", "")
            confidence = 0.95  # Whisper API doesn't return confidence
            
            print(f"[ASR] {entry_id}: '{text}' (conf={confidence})")
            return text, confidence
    
    def _transcribe_local(self, audio_bytes: bytes, entry_id: str) -> tuple[str, float]:
        """Use local Whisper model."""
        
        import numpy as np
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sf.write(tmp.name, audio_bytes, 16000)
            
            result = self.model.transcribe(tmp.name, language="en")
            text = result.get("text", "")
            confidence = 0.90
            
            print(f"[ASR] {entry_id}: '{text}'")
            return text, confidence


class WorkerQueue:
    """Thread pool for concurrent ASR jobs."""
    
    def __init__(self, num_workers=2, callback=None):
        self.queue = Queue()
        self.num_workers = num_workers
        self.callback = callback  # Called when ASR completes
        self.workers = []
        self.running = True
        
        # Start workers
        for i in range(num_workers):
            t = Thread(target=self._worker_loop, daemon=True, name=f"ASRWorker-{i}")
            t.start()
            self.workers.append(t)
        
        print(f"[QUEUE] Started {num_workers} ASR workers")
    
    def enqueue(self, entry):
        """Add entry to processing queue."""
        self.queue.put(entry)
    
    def _worker_loop(self):
        """Worker thread main loop."""
        asr = ASRWorker(model_type="whisper_api")
        
        while self.running:
            try:
                entry = self.queue.get(timeout=1)
                
                if entry is None:  # Poison pill to stop
                    break
                
                # Process
                text, confidence = asr.process_chunk(entry.audio_bytes, entry.entry_id)
                
                # Callback
                if self.callback:
                    self.callback(entry.entry_id, text, confidence, entry.session_id)
                
                self.queue.task_done()
            
            except:
                pass  # Timeout, continue
    
    def stop(self):
        """Stop all workers."""
        self.running = False
        for _ in range(self.num_workers):
            self.queue.put(None)
        for t in self.workers:
            t.join(timeout=5)
```

### 4.6 src/backend/app.py (MAIN FLASK APP)

```python
"""Main Flask/SocketIO application."""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, rooms
import time
import uuid
from datetime import datetime
import os

from .models import Entry, SessionCoordinator
from .storage import Storage
from .workers.asr_worker import WorkerQueue, ASRWorker
from .network import *
from .constants import *

# Initialize
app = Flask(__name__, static_folder="src/frontend/static", template_folder="src/frontend/templates")
app.config["SECRET_KEY"] = "hackathon-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Global state
sessions = {}  # session_id → SessionCoordinator
storage = None
asr_queue = None

def on_asr_result(entry_id, text, confidence, session_id):
    """Callback from ASR worker."""
    if session_id not in sessions:
        return
    
    coordinator = sessions[session_id]
    coordinator.receive_asr_result(entry_id, text, confidence)
    
    # Get updated entry
    entry = coordinator.entries[entry_id]
    
    # Broadcast caption to all clients in session
    caption_msg = build_caption_message(
        entry.entry_id,
        entry.device_id,
        entry.speaker or entry.device_id,
        entry.text,
        entry.start_ts,
        entry.end_ts,
        entry.is_final,
        entry.is_late,
        confidence
    )
    
    socketio.emit("caption", caption_msg, room=session_id)


# ============ ROUTES ============

@app.route("/")
def dashboard():
    """Monitor/UI page."""
    return render_template("index.html")

@app.route("/recorder.html")
def recorder():
    """Device capture page."""
    return render_template("recorder.html")

@app.route("/health")
def health():
    return {"status": "ok", "active_sessions": len(sessions)}


# ============ WEBSOCKET EVENTS ============

@socketio.on("connect")
def handle_connect():
    print(f"[CONNECT] New client connected")

@socketio.on("welcome")
def handle_welcome(data):
    """Device client connects."""
    
    device_id = data.get("device_id", f"device_{uuid.uuid4().hex[:8]}")
    device_name = data.get("device_name", device_id)
    connection_epoch = data.get("connection_epoch", 0)
    session_id = data.get("session_id", f"sess_{uuid.uuid4().hex[:8]}")
    
    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = SessionCoordinator(session_id)
        print(f"[NEW SESSION] {session_id}")
    
    coordinator = sessions[session_id]
    coordinator.handle_device_connect(device_id, connection_epoch)
    
    # Join SocketIO room (for broadcasting)
    socketio.server.enter_room(None, session_id)
    
    # Send welcome response with history
    history = [e.to_dict() for e in coordinator.get_all_entries()]
    
    emit("welcome", build_welcome_response(
        session_id=session_id,
        server_time=time.time(),
        history=history
    ))
    
    # Broadcast to other clients
    broadcast_msg = build_text_message("system", f"{device_name} joined", time.time())
    emit("text_message", broadcast_msg, room=session_id, skip_sid=None)

@socketio.on("chunk")
def handle_chunk(data):
    """Receive audio chunk from device."""
    
    import base64
    import numpy as np
    
    device_id = data.get("device_id")
    session_id = data.get("session_id")
    audio_b64 = data.get("audio_bytes")
    
    if not session_id or session_id not in sessions:
        emit("error", build_error("session_not_found", "Session does not exist"))
        return
    
    # Decode audio
    try:
        audio_bytes_raw = base64.b64decode(audio_b64)
        # Convert bytes to numpy array (16-bit PCM)
        audio_array = np.frombuffer(audio_bytes_raw, dtype=np.int16).astype(np.float32) / 32768.0
    except Exception as e:
        print(f"[AUDIO DECODE ERROR] {e}")
        return
    
    # Create entry
    entry = Entry(
        entry_id=uuid.uuid4().hex,
        session_id=session_id,
        source="asr",
        device_id=device_id,
        start_ts=data.get("start_ts", time.time()),
        end_ts=data.get("end_ts", time.time()),
        audio_bytes=audio_array.tobytes(),
        quality=data.get("quality", "ok"),
        connection_epoch=data.get("connection_epoch", 0),
        chunk_seq=data.get("chunk_seq", 0),
        is_final=False,
        speaker=device_id,
    )
    
    # Receive and queue
    coordinator = sessions[session_id]
    coordinator.receive_audio(entry)
    asr_queue.enqueue(entry)
    
    # Send ACK
    emit("ack", {"chunk_seq": data.get("chunk_seq")})

@socketio.on("end_session")
def handle_end_session(data):
    """Device ends session."""
    
    device_id = data.get("device_id")
    session_id = data.get("session_id")
    
    if session_id not in sessions:
        return
    
    coordinator = sessions[session_id]
    coordinator.handle_device_disconnect(device_id)
    
    msg = build_text_message("system", f"{device_id} ended session", time.time())
    emit("text_message", msg, room=session_id)
    
    # Check if all devices ended
    if coordinator.is_session_done():
        # Save to storage
        all_devices = list(coordinator.device_epochs.keys())
        duration = coordinator.get_session_duration()
        entries = coordinator.get_all_entries()
        
        storage.save_session(session_id, all_devices, duration, entries)
        storage.save_jsonl_backup(session_id, entries)
        
        print(f"[SESSION SAVED] {session_id} - {len(entries)} entries, {duration:.1f}s")
        
        # Notify clients
        ended_msg = build_session_ended(session_id, duration, True)
        emit("session_ended", ended_msg, room=session_id)
        
        # Cleanup
        del sessions[session_id]


# ============ MAIN ============

def init_app():
    """Initialize app and globals."""
    global storage, asr_queue
    
    # Create dirs
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    
    # Initialize storage
    db_path = os.path.join(SESSIONS_DIR, "main.sqlite")
    storage = Storage(db_path)
    
    # Initialize ASR worker queue
    asr_queue = WorkerQueue(num_workers=ASR_WORKERS, callback=on_asr_result)

if __name__ == "__main__":
    init_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
```

---

## SECTION 5: FRONTEND IMPLEMENTATION (Browser)

### 5.1 src/frontend/templates/index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Mute - Real-Time Transcript Monitor</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 Real-Time Transcript Monitor</h1>
            <div id="status" class="status">🔴 Not connected</div>
        </header>
        
        <main>
            <div id="captions" class="caption-box">
                <p class="placeholder">Waiting for captions...</p>
            </div>
        </main>
        
        <footer>
            <p>Session ID: <span id="sessionId">-</span></p>
            <p>Duration: <span id="duration">0:00</span></p>
        </footer>
    </div>
    
    <script src="https://cdn.socket.io/4.5.4/socket.io.js"></script>
    <script src="/static/js/ui.js"></script>
    <script>
        // Connect to server
        const socket = io();
        
        socket.on("connect", () => {
            console.log("Connected to server");
            document.getElementById("status").innerText = "🟢 Connected";
        });
        
        socket.on("caption", (data) => {
            console.log("Caption:", data);
            displayCaption(data);
        });
        
        socket.on("text_message", (data) => {
            console.log("Message:", data);
            displayMessage(data);
        });
        
        socket.on("welcome", (data) => {
            console.log("Welcome:", data);
            document.getElementById("sessionId").innerText = data.session_id;
        });
        
        socket.on("session_ended", (data) => {
            console.log("Session ended:", data);
            document.getElementById("status").innerText = "⚫ Session ended";
        });
        
        socket.on("disconnect", () => {
            document.getElementById("status").innerText = "🔴 Disconnected";
        });
    </script>
</body>
</html>
```

### 5.2 src/frontend/templates/recorder.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Mute - Audio Capture</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🎙️ Audio Capture Device</h1>
            <div id="status" class="status">🔴 Not connected</div>
        </header>
        
        <main>
            <section class="setup">
                <h2>Setup</h2>
                <div class="form-group">
                    <label for="deviceName">Device Name:</label>
                    <input type="text" id="deviceName" placeholder="e.g., Speaker A" value="Speaker A">
                </div>
                
                <div class="form-group">
                    <label for="audioSource">Audio Source:</label>
                    <select id="audioSource">
                        <option value="microphone">Live Microphone</option>
                        <option value="recorded">Pre-recorded File</option>
                    </select>
                </div>
                
                <input type="file" id="audioFile" accept=".wav,.mp3" style="display:none;">
            </section>
            
            <section class="controls">
                <button id="startBtn" class="btn btn-primary" onclick="startCapture()">🟢 Start</button>
                <button id="stopBtn" class="btn btn-danger" onclick="stopCapture()" disabled>🛑 Stop</button>
                <button id="resetBtn" class="btn btn-secondary" onclick="resetConnection()">🔄 Reset</button>
            </section>
            
            <section class="local-captions">
                <h2>Local Captions</h2>
                <div id="localCaptions" class="caption-box">
                    <p class="placeholder">No captions yet...</p>
                </div>
            </section>
        </main>
        
        <footer>
            <p>Session ID: <span id="sessionId">-</span></p>
            <p>Chunks sent: <span id="chunkCount">0</span></p>
        </footer>
    </div>
    
    <script src="https://cdn.socket.io/4.5.4/socket.io.js"></script>
    <script src="/static/js/socket-client.js"></script>
    <script src="/static/js/audio-capture.js"></script>
    <script src="/static/js/ui.js"></script>
</body>
</html>
```

### 5.3 src/frontend/static/js/socket-client.js

```javascript
/**
 * WebSocket client for communicating with server.
 */

class SocketClient {
    constructor(deviceId = null) {
        this.socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 10,
        });
        
        this.deviceId = deviceId || `device_${this.randomId()}`;
        this.sessionId = null;
        this.connectionEpoch = 0;
        this.chunkSeq = 0;
        
        this.setupListeners();
    }
    
    randomId() {
        return Math.random().toString(36).substr(2, 9);
    }
    
    setupListeners() {
        this.socket.on("connect", () => {
            console.log("[SOCKET] Connected to server");
            this.onConnected();
        });
        
        this.socket.on("welcome", (data) => {
            console.log("[SOCKET] Welcome:", data);
            this.sessionId = data.session_id;
            this.onWelcome(data);
        });
        
        this.socket.on("caption", (data) => {
            console.log("[SOCKET] Caption:", data);
            this.onCaption(data);
        });
        
        this.socket.on("ack", (data) => {
            // Chunk acknowledged
        });
        
        this.socket.on("text_message", (data) => {
            console.log("[SOCKET] Message:", data);
            this.onTextMessage(data);
        });
        
        this.socket.on("session_ended", (data) => {
            console.log("[SOCKET] Session ended:", data);
            this.onSessionEnded(data);
        });
        
        this.socket.on("error", (data) => {
            console.error("[SOCKET] Error:", data);
            this.onError(data);
        });
        
        this.socket.on("disconnect", () => {
            console.log("[SOCKET] Disconnected");
            this.onDisconnected();
        });
    }
    
    sendWelcome(deviceName) {
        this.socket.emit("welcome", {
            device_id: this.deviceId,
            device_name: deviceName,
            connection_epoch: this.connectionEpoch,
            session_id: this.sessionId,
        });
    }
    
    sendChunk(audioBytes, startTs, endTs, quality = "ok") {
        // Convert to base64
        const b64 = this.bytesToBase64(audioBytes);
        
        this.socket.emit("chunk", {
            device_id: this.deviceId,
            session_id: this.sessionId,
            connection_epoch: this.connectionEpoch,
            chunk_seq: this.chunkSeq++,
            audio_bytes: b64,
            audio_format: "PCM16",
            sample_rate: 16000,
            channels: 1,
            start_ts: startTs,
            end_ts: endTs,
            quality: quality,
        });
    }
    
    sendEndSession() {
        this.socket.emit("end_session", {
            device_id: this.deviceId,
            session_id: this.sessionId,
            reason: "manual",
        });
    }
    
    reconnect() {
        this.connectionEpoch++;
        this.chunkSeq = 0;
        this.socket.disconnect();
        this.socket.connect();
    }
    
    bytesToBase64(bytes) {
        return btoa(String.fromCharCode(...new Uint8Array(bytes)));
    }
    
    // Callbacks (override in app)
    onConnected() {}
    onWelcome(data) {}
    onCaption(data) {}
    onTextMessage(data) {}
    onSessionEnded(data) {}
    onError(data) {}
    onDisconnected() {}
}
```

### 5.4 src/frontend/static/js/audio-capture.js

```javascript
/**
 * Handles audio capture from microphone or file.
 */

const SAMPLE_RATE = 16000;
const CHUNK_DURATION = 0.4;  // 400ms
const CHUNK_SAMPLES = Math.floor(SAMPLE_RATE * CHUNK_DURATION);

class AudioCapture {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.recording = false;
        this.startTime = 0;
        this.chunkCount = 0;
        
        this.socketClient = new SocketClient();
        this.captionDisplay = new CaptionDisplay("localCaptions");
        
        // Hook up callbacks
        this.socketClient.onCaption = (data) => this.captionDisplay.addCaption(data);
        this.socketClient.onWelcome = (data) => this.onWelcome(data);
    }
    
    async startMicrophone() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: SAMPLE_RATE,
                }
            });
            
            this.setupAudioContext();
            this.recording = true;
            this.startTime = performance.now();
            document.getElementById("status").innerText = "🟢 Recording...";
            document.getElementById("startBtn").disabled = true;
            document.getElementById("stopBtn").disabled = false;
            
            console.log("[CAPTURE] Microphone started");
        } catch (error) {
            alert("Microphone access denied: " + error.message);
            document.getElementById("status").innerText = "❌ " + error.message;
        }
    }
    
    setupAudioContext() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: SAMPLE_RATE,
        });
        
        const source = this.audioContext.createMediaStreamSource(this.mediaStream);
        
        // Use ScriptProcessorNode (note: deprecated but widely supported)
        this.processor = this.audioContext.createScriptProcessor(CHUNK_SAMPLES, 1, 1);
        
        this.processor.onaudioprocess = (event) => {
            if (!this.recording) return;
            
            const inputData = event.inputBuffer.getChannelData(0);
            const int16Array = this.floatTo16BitPCM(inputData);
            
            const currentTime = (performance.now() - this.startTime) / 1000;
            this.sendChunk(int16Array, currentTime - CHUNK_DURATION, currentTime, "ok");
            
            this.chunkCount++;
            document.getElementById("chunkCount").innerText = this.chunkCount;
        };
        
        source.connect(this.processor);
        this.processor.connect(this.audioContext.destination);
    }
    
    floatTo16BitPCM(floatArray) {
        const int16Array = new Int16Array(floatArray.length);
        for (let i = 0; i < floatArray.length; i++) {
            // Clamp to [-1, 1]
            const s = Math.max(-1, Math.min(1, floatArray[i]));
            // Convert to 16-bit signed integer
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return int16Array.buffer;  // Return as ArrayBuffer
    }
    
    sendChunk(audioBytes, startTs, endTs, quality) {
        this.socketClient.sendChunk(audioBytes, startTs, endTs, quality);
    }
    
    async playRecordedFile(file) {
        // Load WAV file and stream chunks
        const arrayBuffer = await file.arrayBuffer();
        const audioData = await this.audioContext.decodeAudioData(arrayBuffer);
        
        const rawData = audioData.getChannelData(0);
        
        this.recording = true;
        this.startTime = performance.now();
        
        // Stream in 400ms chunks
        let offset = 0;
        while (offset < rawData.length && this.recording) {
            const end = Math.min(offset + CHUNK_SAMPLES, rawData.length);
            const chunk = rawData.slice(offset, end);
            
            const int16Array = this.floatTo16BitPCM(chunk);
            const currentTime = (offset / SAMPLE_RATE);
            
            this.sendChunk(
                int16Array,
                currentTime - CHUNK_DURATION,
                currentTime,
                "ok"
            );
            
            this.chunkCount++;
            document.getElementById("chunkCount").innerText = this.chunkCount;
            
            offset += CHUNK_SAMPLES;
            
            // Wait 400ms before next chunk (simulates real-time)
            await new Promise(resolve => setTimeout(resolve, CHUNK_DURATION * 1000));
        }
        
        this.stopCapture();
    }
    
    stopCapture() {
        this.recording = false;
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.processor) {
            this.processor.disconnect();
        }
        
        this.socketClient.sendEndSession();
        document.getElementById("status").innerText = "⚫ Stopped";
        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
    
    onWelcome(data) {
        console.log("[AUDIO] Session established:", data.session_id);
        document.getElementById("sessionId").innerText = data.session_id;
    }
}

// Global instance
let audioCapture = null;

function startCapture() {
    if (!audioCapture) {
        audioCapture = new AudioCapture();
    }
    
    const source = document.getElementById("audioSource").value;
    const deviceName = document.getElementById("deviceName").value;
    
    // Send welcome first
    audioCapture.socketClient.sendWelcome(deviceName);
    
    if (source === "microphone") {
        audioCapture.startMicrophone();
    } else {
        // Use recorded file
        document.getElementById("audioFile").click();
        document.getElementById("audioFile").onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                audioCapture.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioCapture.playRecordedFile(file);
            }
        };
    }
}

function stopCapture() {
    if (audioCapture) {
        audioCapture.stopCapture();
    }
}

function resetConnection() {
    if (audioCapture) {
        audioCapture.socketClient.reconnect();
    }
}
```

### 5.5 src/frontend/static/js/ui.js

```javascript
/**
 * UI components for displaying captions.
 */

class CaptionDisplay {
    constructor(elementId = "captions") {
        this.element = document.getElementById(elementId);
        this.captions = [];
    }
    
    addCaption(data) {
        const caption = {
            id: data.entry_id,
            speaker: data.speaker || "Speaker",
            text: data.text,
            isLate: data.is_late || false,
            timestamp: new Date().toLocaleTimeString(),
        };
        
        this.captions.push(caption);
        this.render();
    }
    
    render() {
        if (this.captions.length === 0) {
            this.element.innerHTML = '<p class="placeholder">No captions yet...</p>';
            return;
        }
        
        const html = this.captions.map(c => `
            <div class="caption ${c.isLate ? 'late' : ''}">
                <div class="caption-header">
                    <strong>${c.speaker}</strong>
                    <span class="time">${c.timestamp}</span>
                    ${c.isLate ? '<span class="tag-late">earlier</span>' : ''}
                </div>
                <div class="caption-text">${this.escapeHtml(c.text)}</div>
            </div>
        `).join("");
        
        this.element.innerHTML = html;
        // Scroll to bottom
        this.element.scrollTop = this.element.scrollHeight;
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

function displayCaption(data) {
    // Called from index.html
    if (!window.captionDisplay) {
        window.captionDisplay = new CaptionDisplay("captions");
    }
    window.captionDisplay.addCaption(data);
}

function displayMessage(data) {
    // Display system messages
    if (!window.captionDisplay) {
        window.captionDisplay = new CaptionDisplay("captions");
    }
    window.captionDisplay.addCaption({
        entry_id: "msg_" + Date.now(),
        speaker: data.source.toUpperCase(),
        text: data.text,
        is_late: false,
    });
}
```

### 5.6 src/frontend/static/css/style.css

```css
/* Global Styles */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    height: 100%;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-height: 100vh;
}

header {
    padding: 20px;
    border-bottom: 1px solid #eee;
}

header h1 {
    color: #333;
    margin-bottom: 10px;
    font-size: 1.8em;
}

.status {
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.95em;
    font-weight: 500;
    background: #e3f2fd;
    color: #1976d2;
    display: inline-block;
}

main {
    flex: 1;
    padding: 20px;
    overflow: auto;
}

footer {
    padding: 15px 20px;
    border-top: 1px solid #eee;
    background: #f9f9f9;
    font-size: 0.9em;
    color: #666;
}

footer p {
    margin: 5px 0;
}

/* Caption Box */

.caption-box {
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    min-height: 150px;
    max-height: 400px;
    overflow-y: auto;
    margin: 20px 0;
}

.caption {
    padding: 12px;
    margin: 8px 0;
    background: white;
    border-left: 4px solid #667eea;
    border-radius: 4px;
    line-height: 1.6;
    transition: all 0.2s ease;
}

.caption:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.caption.late {
    border-left-color: #ff9800;
    background: #fff8f0;
}

.caption-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 5px;
    gap: 10px;
}

.caption-header strong {
    color: #667eea;
    font-size: 0.95em;
}

.caption-header .time {
    font-size: 0.8em;
    color: #999;
}

.tag-late {
    background: #ff9800;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.75em;
}

.caption-text {
    color: #333;
    line-height: 1.5;
}

.placeholder {
    color: #999;
    text-align: center;
    padding: 30px 20px;
    font-style: italic;
}

/* Forms */

.setup, .controls, .local-captions {
    margin: 20px 0;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 8px;
}

.setup h2, .local-captions h2 {
    font-size: 1.1em;
    color: #333;
    margin-bottom: 15px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 5px;
    color: #333;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1em;
    transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Buttons */

.controls {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    background: transparent;
    padding: 0;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 600;
    transition: all 0.2s;
}

.btn-primary {
    background: #667eea;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: #5568d3;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-danger {
    background: #ef5350;
    color: white;
}

.btn-danger:hover:not(:disabled) {
    background: #e53935;
}

.btn-secondary {
    background: #bdbdbd;
    color: white;
}

.btn-secondary:hover:not(:disabled) {
    background: #9e9e9e;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Responsive */

@media (max-width: 600px) {
    .container {
        height: auto;
    }
    
    header h1 {
        font-size: 1.4em;
    }
    
    .controls {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
    }
    
    .caption-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
```

---

## SECTION 6: FINAL CHECKLIST BEFORE RUNNING

- [ ] Python 3.9+ installed
- [ ] venv activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file with `OPENAI_API_KEY=sk-...`
- [ ] Directories created: `data/recordings`, `data/sessions`, `src/frontend/static/{js,css}`, `src/frontend/templates`
- [ ] Backend code files: `app.py`, `models.py`, `storage.py`, `network.py`, `workers/asr_worker.py`
- [ ] Frontend code files: `index.html`, `recorder.html`, `js/socket-client.js`, `js/audio-capture.js`, `js/ui.js`, `css/style.css`
- [ ] Test Whisper API: `python test_whisper.py` → should output ✓
- [ ] Know your server IP: `ifconfig | grep inet`

---

## SECTION 7: RUNNING THE DEMO

### Terminal 1: Start Server

```bash
cd /Users/richa.agrawal1/Desktop/Project_mute
source venv/bin/activate
export FLASK_APP=src/backend/app.py
export OPENAI_API_KEY="sk-proj-..."
python -m flask run --host=0.0.0.0 --port=5000
```

**Expected Output**:
```
WARNING: This is a development server...
Running on http://0.0.0.0:5000
```

### Terminal 2 (or Browser Tab): Open Clients

**On same laptop** (easiest for testing):
```
Tab 1: http://localhost:5000/recorder.html (Device A)
Tab 2: http://localhost:5000/recorder.html (Device B)
Tab 3: http://localhost:5000/ (Monitor)
```

**On 2 phones** (more realistic, same WiFi):
```
Phone 1: http://192.168.1.100:5000/recorder.html (replace with your server IP)
Phone 2: http://192.168.1.100:5000/recorder.html
Monitor: http://192.168.1.100:5000/ (laptop or any device)
```

### Demo Flow

1. **Device A** (first phone):
   - Set name: "Speaker A"
   - Select: Microphone or Recorded File
   - Click "Start" → begins capturing
   - Speak naturally for 30+ seconds
   - Captions appear in 2-5 seconds

2. **Device B** (second phone):
   - Join same session (connects automatically)
   - Set name: "Speaker B"
   - Click "Start"
   - Speak (can overlap with A)

3. **Monitor** (Dashboard):
   - Shows both speakers' captions in real-time
   - Late entries shown with "earlier" tag
   - Session duration timer

4. **End**:
   - Either device clicks "Stop"
   - Transcript saved to `data/sessions/sess_*.sqlite`
   - Both devices notified

---

## APPENDIX: QUICK TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'openai'` | `pip install openai` |
| `OPENAI_API_KEY not set` | Create `.env` file with `OPENAI_API_KEY="sk-..."` |
| `WebSocket connection refused` | Check server is running, use `0.0.0.0:5000` not `localhost` |
| `Microphone permission denied` | Browser permissions → allow microphone access |
| `Audio is too quiet` | Increase microphone volume on device |
| `Transcription is garbage` | Try Vosk instead (local Whisper), or check audio format |
| `Port 5000 in use` | `lsof -i :5000` → `kill -9 <PID>` |

---

**END OF IMPLEMENTATION ROADMAP**

You now have:
✅ Complete backend + frontend code (ready to paste)
✅ Setup instructions
✅ Running demo guide
✅ Troubleshooting

**Next Step**: Create the directory structure and paste the files. Let me know if you hit any issues or need clarification on any section!

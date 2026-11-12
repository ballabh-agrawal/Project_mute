# PROJECT MUTE - COMPLETE FEASIBILITY & IMPLEMENTATION BLUEPRINT
**Date**: 2026-11-09  
**Status**: Ready for Implementation  
**Hackathon Scope**: 2-device demo with pre-recorded audio + live mic option

---

## SECTION 1: EXECUTIVE SUMMARY & DECISIONS

### What This Project Does
Real-time multi-speaker transcription system for deaf/hard-of-hearing users. Captures audio from 2+ speaking devices, transcribes using ASR (Automatic Speech Recognition), and displays captions in real-time with speaker identification.

### Your Decisions Made
1. ✅ **Audio Input**: Both recorded files + live microphone (start with recorded)
2. ✅ **Platform**: Browser (Web) - HTML/CSS/JS
3. ✅ **TTS**: Skipped (text-only captions for MVP)
4. ✅ **Device Count**: 2 devices (speaker A, speaker B) + 1 server
5. ✅ **ASR Model**: Free/low-cost option (Vosk for CPU, Whisper API for GPU)
6. ✅ **Latency Target**: ~2-5 seconds acceptable for hackathon

### MVP Scope (What We Build)
- ✅ Web UI (browser)
- ✅ Server (Python/Node)
- ✅ 2 device clients (browser)
- ✅ ASR integration (Vosk or Whisper)
- ✅ Real-time caption display
- ✅ Speaker labels (A, B, or names)
- ✅ Recording to SQLite on session end
- ✅ Pre-recorded audio playback for demo
- ✅ Live mic input (if time permits)

### Out of Scope (Not for MVP)
- ❌ Emotion detection
- ❌ Multiple simultaneous sessions
- ❌ User authentication/login
- ❌ Audio encryption
- ❌ Audio compression (uncompressed PCM16)
- ❌ TTS/audio reply to deaf user
- ❌ Smart glasses, wearables
- ❌ Mobile app (browser only)

---

## SECTION 2: COMPLETE SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CENTRAL SERVER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flask/FastAPI Web Server (Python) or Node.js Backend   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐    │  │
│  │  │ WebSocket   │  │ SessionHub   │  │ ASR Queue    │    │  │
│  │  │ Manager     │  │ (Router)     │  │ Manager      │    │  │
│  │  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘    │  │
│  │         │                 │                 │             │  │
│  │  ┌──────▼──────────────────▼─────────────────▼──────┐   │  │
│  │  │  SessionCoordinator (State Management)           │   │  │
│  │  │  - Track speaker timings (sync across devices)   │   │  │
│  │  │  - Buffer entries (audio chunks, transcriptions) │   │  │
│  │  │  - Detect speaker turns (overlap handling)       │   │  │
│  │  └───────────────────────┬──────────────────────────┘   │  │
│  │                          │                               │  │
│  │  ┌──────────────────────▼──────────────────────────┐   │  │
│  │  │  ASR Worker Pool (Process Audio → Text)         │   │  │
│  │  │  - Vosk OR OpenAI Whisper                       │   │  │
│  │  │  - Runs 1-2 concurrent workers (RTX 4050)       │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │  Storage (SQLite + JSONL Live Copy)              │   │  │
│  │  │  - Session transcript (saved at end)             │   │  │
│  │  │  - Safety backup (live append)                   │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │ WebSocket (audio + messages)
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼────┐    ┌─────▼────┐    ┌─────▼────┐
    │  Device  │    │  Device  │    │   UI     │
    │    A     │    │    B     │    │  Monitor │
    │(Browser) │    │(Browser) │    │(Optional)│
    │ Speaker  │    │ Speaker  │    │          │
    │  1 Audio │    │  2 Audio │    │ Real-time│
    │ Capture  │    │ Capture  │    │ Caption  │
    │          │    │          │    │ Display  │
    └──────────┘    └──────────┘    └──────────┘
```

### 2.2 Component Breakdown

| Component | Purpose | Technology | Runs On | Notes |
|-----------|---------|-----------|---------|-------|
| **WebSocket Server** | Real-time message routing | Flask-SocketIO or Node.js/Socket.io | Server | Handles 2-3 concurrent connections |
| **SessionCoordinator** | Sync, buffer, deduplicate | Python class | Server | Core business logic |
| **ASR Worker** | Audio → Text | Vosk or Whisper API | Server GPU | Process queue, rate-limited |
| **Storage** | Persist transcripts | SQLite + JSONL | Server (disk) | Session data after end |
| **Device Client** | Audio capture + UI | HTML5/JS/WebSocket | Browser | Runs on speaker device |
| **UI Dashboard** | Real-time caption display | HTML/CSS/JS | Browser | Optional, for monitoring |
| **Sync Module** | Clock offset calibration | Python | Server | Timestamp alignment |
| **Network Module** | Message protocol | JSON over WebSocket | Client ↔ Server | Define all message types |

---

## SECTION 3: TECHNOLOGY STACK & DEPENDENCIES

### 3.1 Backend Stack (Python)
```
Language: Python 3.9+
Framework: Flask (lightweight) OR FastAPI (modern, faster)
Real-time: Flask-SocketIO OR python-socketio
Audio Processing: librosa, soundfile
ASR Option 1: Vosk (pocketsphinx wrapper - local, CPU)
ASR Option 2: OpenAI Whisper (local GPU or API)
Storage: SQLite3 (built-in)
Utilities: NumPy, SciPy
Testing: pytest
```

**Install These**:
```bash
pip install flask flask-socketio python-socketio
pip install librosa soundfile  # Audio processing
pip install vosk                # Lightweight ASR (Option 1)
# OR
pip install openai              # Whisper API (Option 2)
pip install numpy scipy
pip install pytest              # Testing
```

### 3.2 Frontend Stack (Browser)
```
Language: JavaScript (ES6+) / HTML / CSS
Real-time: Socket.io client library
Audio: Web Audio API (native, no library needed)
UI Framework: Vanilla JS (lightweight) or Vue.js/React (optional)
Display: HTML5 + CSS3
Recording: MediaRecorder API (native)
Testing: Jest (optional)
```

**Include in HTML**:
```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
```

### 3.3 Deployment Options for Hackathon

**Option A: Local Network (Recommended for Demo)**
- Server: localhost or local IP (192.168.x.x)
- Clients: Same network
- Database: SQLite on server disk
- No cloud cost, works offline

**Option B: Free Cloud** (if needed)
- Backend: Heroku (free tier deprecated) → Railway, Render, or local
- Frontend: GitHub Pages or local HTTP server
- Database: SQLite (portable)

**Recommendation**: Run everything local with Flask on one laptop. Access from 2 browser tabs or 2 devices on same WiFi.

---

## SECTION 4: DETAILED MODULE SCHEMAS & DATA MODELS

### 4.1 Core Data Model (All modules use this)

```python
# Shared constants
SAMPLE_RATE = 16000  # Hz (16 kHz audio)
AUDIO_FORMAT = "PCM16"  # 16-bit signed integer
CHANNELS = 1  # Mono
CHUNK_DURATION = 0.4  # seconds (6400 samples per chunk)
OVERLAP_SLACK = 0.15  # 150ms clock tolerance
HIGH_THRESHOLD = 0.75  # Speaker diarization threshold
LOW_THRESHOLD = 0.55  # (configure based on tests)
LOUDNESS_GATE = -40  # dBFS (noise floor)
ASR_WORKERS = 2  # Concurrent ASR jobs (tune after benchmark)
LATENCY_CEILING = 5.0  # seconds (max acceptable delay)
```

### 4.2 Entry (Core Event Record)

Every event in the system is an `Entry`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Entry:
    """Represents one piece of data flowing through the system."""
    
    entry_id: str  # uuid4().hex - unique identifier
    session_id: str  # Which session this belongs to
    source: str  # "asr", "manual", "metadata", "tts" (event type)
    device_id: str  # Which device sent this (e.g., "device_a", "device_b")
    
    start_ts: float  # Timestamp when speech began (seconds)
    end_ts: float  # Timestamp when speech ended (seconds)
    
    speaker: Optional[str]  # "speaker_a", "speaker_b", or actual name
    speaker_confidence: Optional[float]  # 0.0-1.0
    
    text: Optional[str]  # Transcribed text (if source="asr")
    audio_bytes: Optional[bytes]  # Raw PCM16 audio (if source="audio")
    
    quality: Optional[str]  # "ok" or "low_quality"
    is_final: bool  # True when entry is complete and won't change
    is_late: bool  # True if arrived after display deadline
    
    # Metadata for deduplication
    connection_epoch: int  # Device connection counter (0, 1, 2...)
    chunk_seq: Optional[int]  # Sequence number within chunk stream (only for "asr" source)
    
    created_at: datetime  # When entry was created
    
    def to_dict(self):
        """Serialize for JSON transport."""
        return {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "source": self.source,
            "device_id": self.device_id,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "speaker": self.speaker,
            "speaker_confidence": self.speaker_confidence,
            "text": self.text,
            "audio_bytes_b64": base64.b64encode(self.audio_bytes).decode() if self.audio_bytes else None,
            "quality": self.quality,
            "is_final": self.is_final,
            "is_late": self.is_late,
            "chunk_seq": self.chunk_seq,
            "created_at": self.created_at.isoformat(),
        }
```

### 4.3 WebSocket Message Protocol

All communication uses JSON over WebSocket.

**Client → Server Messages**:

```python
# 1. CONNECT (implicit on WebSocket handshake)
# Client sends immediately after connection established
{
    "type": "welcome",
    "device_id": "device_a",
    "device_name": "Laptop Mic (John)",
    "connection_epoch": 0,
}

# 2. AUDIO CHUNK (streaming)
{
    "type": "chunk",
    "device_id": "device_a",
    "connection_epoch": 0,
    "chunk_seq": 0,  # Sequential counter
    "start_ts": 12.345,  # Server's clock time
    "end_ts": 12.745,
    "audio_bytes": "<base64 PCM16 audio>",  # 400ms of audio
    "audio_format": "PCM16",
    "sample_rate": 16000,
    "channels": 1,
    "quality": "ok",  # or "low_quality"
}

# 3. ACKNOWLEDGMENT (client confirms receipt)
{
    "type": "ack",
    "device_id": "device_a",
    "chunk_seq": 0,
}

# 4. END SESSION (when speaker is done)
{
    "type": "end_session",
    "device_id": "device_a",
    "reason": "manual",  # or "timeout", "error"
}
```

**Server → Client Messages**:

```python
# 1. WELCOME RESPONSE (after client sends welcome)
{
    "type": "welcome",
    "session_id": "sess_abc123",
    "server_time": 0.0,  # Server's current clock (for sync)
    "history": [  # Previous entries in this session
        {entry_id, session_id, source, device_id, ...},
        ...
    ],
}

# 2. CAPTION (transcribed text for display)
{
    "type": "caption",
    "entry_id": "entry_xyz789",
    "device_id": "device_a",
    "speaker": "device_a",  # or "Speaker 1", name, etc
    "text": "Hello, can you hear me?",
    "start_ts": 12.345,
    "end_ts": 12.745,
    "is_final": true,
    "is_late": false,
    "confidence": 0.92,
}

# 3. TEXT MESSAGE (metadata, status)
{
    "type": "text_message",
    "entry_id": "msg_123",
    "source": "system",
    "text": "Device B connected",
    "timestamp": 15.0,
}

# 4. SESSION ENDED
{
    "type": "session_ended",
    "session_id": "sess_abc123",
    "reason": "all_devices_ended",
    "total_duration": 125.4,  # seconds
    "transcript_saved": true,
    "transcript_path": "/path/to/session_abc123.sqlite",
}

# 5. ERROR
{
    "type": "error",
    "code": "tts_failed" | "asr_timeout" | "connection_lost",
    "message": "ASR failed for chunk #5: Vosk error",
    "device_id": "device_a",
}
```

### 4.4 SessionCoordinator State (Server-side)

```python
class SessionCoordinator:
    """Manages session state, syncing, buffering, deduplication."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries: list[Entry] = []  # All entries in session
        self.released_entries: list[Entry] = []  # Entries sent to UI
        
        # Sync state
        self.device_clocks: dict[str, float] = {}  # device_id → offset
        self.last_clock_sync: dict[str, float] = {}  # device_id → last sync time
        
        # Deduplication (device_id, connection_epoch, chunk_seq) → entry_id
        self.seen_chunks: set[tuple] = set()
        
        # Status
        self.active_devices: set[str] = set()
        self.ended_devices: set[str] = set()
        self.started_at: float = 0.0
    
    def receive_audio(self, entry: Entry) -> None:
        """Add audio chunk, check for duplicates."""
        key = (entry.device_id, entry.connection_epoch, entry.chunk_seq)
        if key in self.seen_chunks:
            return  # Duplicate, ignore
        self.seen_chunks.add(key)
        self.entries.append(entry)
        # Queue for ASR processing
        self.asr_queue.put(entry)
    
    def receive_asr_result(self, entry_id: str, text: str, confidence: float) -> None:
        """Update entry with ASR result."""
        entry = self.get_entry(entry_id)
        entry.text = text
        entry.speaker_confidence = confidence
        entry.is_final = True
        # Mark as ready for release to UI
        self.release_entry(entry_id)
    
    def released_entries(self) -> list[Entry]:
        """Get all entries ready for display (haven't been sent yet)."""
        return self.released_entries
    
    def release_entry(self, entry_id: str) -> None:
        """Mark entry as ready for UI display."""
        entry = self.get_entry(entry_id)
        # Check if late (arrived after 5s latency window)
        if time.time() - entry.start_ts > LATENCY_CEILING:
            entry.is_late = True
        self.released_entries.append(entry)
    
    def handle_device_connect(self, device_id: str) -> None:
        """Device connected."""
        self.active_devices.add(device_id)
        self.device_clocks[device_id] = 0.0
    
    def handle_device_disconnect(self, device_id: str) -> None:
        """Device disconnected (will reconnect with new epoch)."""
        self.active_devices.discard(device_id)
    
    def is_session_done(self) -> bool:
        """Check if all devices have ended."""
        return self.active_devices == set() and len(self.ended_devices) > 0
```

### 4.5 Database Schema (SQLite)

```sql
-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    ended_at TIMESTAMP,
    devices TEXT,  -- JSON list of device IDs
    total_duration_sec REAL,
    status TEXT  -- "active", "ended", "error"
);

-- Entries table (complete transcript)
CREATE TABLE entries (
    entry_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    source TEXT NOT NULL,  -- "asr", "audio", "metadata", "tts"
    device_id TEXT,
    start_ts REAL,
    end_ts REAL,
    speaker TEXT,
    speaker_confidence REAL,
    text TEXT,
    audio_bytes BLOB,  -- PCM16 raw audio
    quality TEXT,
    is_final BOOLEAN,
    is_late BOOLEAN,
    connection_epoch INTEGER,
    chunk_seq INTEGER,
    created_at TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    UNIQUE(session_id, device_id, connection_epoch, chunk_seq)  -- Deduplication
);

-- Index for queries
CREATE INDEX idx_session_speaker ON entries(session_id, speaker);
CREATE INDEX idx_session_time ON entries(session_id, start_ts);
```

### 4.6 ASR Worker Interface

```python
class ASRWorker:
    """Process audio chunks → transcribed text."""
    
    def __init__(self, model_type: str = "vosk"):
        # model_type: "vosk" | "whisper_api" | "whisper_local"
        self.model_type = model_type
        if model_type == "vosk":
            from vosk import Model, KaldiRecognizer
            self.model = Model(lang="en-us")  # Download beforehand
            self.recognizer = None
        elif model_type == "whisper_api":
            import openai
            self.client = openai.OpenAI()
    
    def process_chunk(self, audio_bytes: bytes, entry_id: str) -> tuple[str, float]:
        """
        Transcribe audio chunk.
        Returns: (text, confidence_score)
        """
        if self.model_type == "vosk":
            if self.recognizer is None:
                self.recognizer = KaldiRecognizer(self.model, 16000)
            
            self.recognizer.AcceptWaveform(audio_bytes)
            result = json.loads(self.recognizer.Result())
            
            text = result.get("result", [])  # List of words
            text_str = " ".join([w["conf"] for w in text])
            confidence = np.mean([w["conf"] for w in text]) if text else 0.0
            
            return text_str, confidence
        
        elif self.model_type == "whisper_api":
            # Send to OpenAI Whisper API
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                # Convert bytes to WAV
                sf.write(tmp.name, audio_bytes, 16000)
                with open(tmp.name, "rb") as f:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                    )
            return transcript.text, 0.95  # Whisper doesn't return confidence
```

---

## SECTION 5: COMPLETE DATA FLOW

### 5.1 Happy Path: Recording + Transcription + Display

```
STEP 1: Device A connects
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│ "Click Start"                │                       │            │
│ → WebSocket CONNECT          │                       │            │
│ → send "welcome"  ────────────────→ SessionCoordinator           │
│                              │     .handle_device_connect()      │
│                              │     ✓ session_id = "sess_123"     │
│                              │     ✓ device_a = active          │
│ ← receive "welcome" response ←────── send history, server_time   │
│   (session_id, history)      │                       │            │
└─────────────────────────────────────────────────────────────────┘

STEP 2: Device B connects (same session)
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│                              │                       │ "Click Start"
│                              │                       │ → CONNECT
│                              │                       │ → "welcome"
│                              │  SessionCoordinator   │            │
│                              │  .handle_device_connect("device_b")
│                              │  ✓ device_b = active │            │
│                              │  (broadcast to A & B) │            │
│ ← "text_message"           ←────── "Device B joined" │            │
│   "Device B joined"         │       │                │            │
│                              │       ├──→ "text_message" →        │
└─────────────────────────────────────────────────────────────────┘

STEP 3: Device A streams audio
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│ [Recording 400ms of audio]   │                       │            │
│ Entry (source="asr")         │                       │            │
│ - entry_id = uuid4().hex     │                       │            │
│ - audio_bytes = PCM16 (6400 samples)                │            │
│ - start_ts = 1.234, end_ts = 1.634                  │            │
│ - device_id = "device_a"     │                       │            │
│                              │                       │            │
│ send "chunk" message ────────────→ SessionCoordinator            │
│ (base64-encoded audio)       │     .receive_audio(entry)         │
│                              │     ✓ Check for duplicates        │
│ ← "ack"  ←────────────────────────── ✓ Add to entries list      │
│   (chunk_seq=0)              │     ✓ Enqueue for ASR processing  │
│                              │                       │            │
│ [Recording continues...]     │     ASR Worker picks up           │
│ send "chunk" (seq=1) ──────────────→ Process entry              │
│ ← "ack" (seq=1)              │     [Takes ~2s for Vosk]          │
└─────────────────────────────────────────────────────────────────┘

STEP 4: ASR processes audio
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│                              │ ASR Worker processes entry_1      │
│                              │ audio_bytes → Vosk recognizer     │
│                              │ Result: "Hello, can you hear me?" │
│                              │ confidence: 0.92                  │
│                              │                       │            │
│                              │ SessionCoordinator               │
│                              │ .receive_asr_result(entry_1)     │
│                              │ update entry.text = "Hello..."   │
│                              │ update entry.is_final = true     │
│                              │ .release_entry(entry_1)          │
│                              │                       │            │
│                              │ Broadcast caption message to UI: │
│ ← "caption"  ←─────────────────────── type="caption"           │
│   speaker="device_a"         │         text="Hello, can..."     │
│   text="Hello, can you hear me?"      is_final=true             │
│   confidence=0.92            │         speaker_confidence=0.92  │
│   is_final=true              │                       │            │
│                              │       ┌───────────────→ "caption" │
│ [Display on screen]          │       │                [Display]  │
│ "Speaker A: Hello, can       │       │                          │
│  you hear me?"               │       │                          │
└─────────────────────────────────────────────────────────────────┘

STEP 5: Device B speaks (overlap)
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│                              │                       │ [Recording]
│                              │                       │ send "chunk"
│ (still receiving A's audio)  │ ← chunk (device_b, seq=0, 2.5s) │
│ send "chunk" (seq=5) ──────────→                    │            │
│                              │ Coordinator stores B's audio     │
│ ← "ack" (seq=5)              │ queue for ASR (multi-threaded)   │
│                              │                       │            │
│                              │ ASR processes both A & B in      │
│                              │ parallel (up to ASR_WORKERS=2)   │
│                              │                       │            │
│ [A's caption still on screen]│ → "caption" (device_b)           │
│ "Speaker A: Hello..."        │   ┌────────────────→ "caption"   │
│ "Speaker B: Yeah I hear you" │   │                [Display B]    │
│                              │   │                          │    │
│ [UI shows both captions]     │   └─────────────────→ "caption"  │
│ [Arrange by timestamp]       │      (sent to device_a too)      │
└─────────────────────────────────────────────────────────────────┘

STEP 6: Session ends
┌─────────────────────────────────────────────────────────────────┐
│ Device A (Browser)          │ Server                │ Device B   │
│                              │                       │            │
│ User clicks "End Session"    │                       │            │
│ send "end_session" ────────────────→ SessionCoordinator         │
│                              │     .handle_device_disconnect()  │
│                              │     (still waiting for B)         │
│                              │       ├─────────────→            │
│                              │       │              (still 
│                              │       └──ack────────→  recording)
│                              │                       │            │
│ ← "text_message"            ←────────── "Device A ended session"│
│   "Waiting for Device B..." │                       │            │
│                              │                       │            │
│                              │                       │ User ends  │
│                              │                       │ send "end_s
│                              │ ← end_session ────────┤ ession"   │
│                              │                       │            │
│                              │ SessionCoordinator    │            │
│                              │ .is_session_done() = True        │
│                              │ Save to SQLite + JSONL backup    │
│                              │ /tmp/sessions/sess_123.sqlite    │
│                              │                       │            │
│ ← "session_ended"  ←─────────────────── broadcast to all clients
│   session_id="sess_123"      │     transcript_saved=true        │
│   transcript_path=...        │     total_duration=120.5         │
│                              │       ┌──────────────→            │
│ [Session closed]             │       │ "session_ended"          │
│ [Transcript saved locally]   │       │ [Download transcript]    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Error Handling Flow

```
ASR Timeout (stuck on one chunk)
┌──────────────────────────────────┐
│ ASR Worker                       │
│ process_chunk(audio_bytes)       │
│ [Vosk/Whisper takes >10 seconds] │
│ Timeout detected                 │
└──────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────┐
│ Coordinator                                  │
│ Mark entry.is_final = true                   │
│ entry.text = "[ASR failed]"                  │
│ Release to UI with error context             │
└──────────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────────┐
│ UI                                                  │
│ Display: "Speaker A: [ASR failed]"                  │
│ (Appears in transcript, but no transcription)       │
│ Continue accepting new chunks                       │
└─────────────────────────────────────────────────────┘

Device Reconnect
┌──────────────────────────────┐
│ Device A's connection drops   │
│ (WiFi hiccup, etc.)          │
└──────────────────────────────┘
                │
                ↓
┌────────────────────────────────────┐
│ Server detects socket disconnect   │
│ Coordinator:                       │
│ .handle_device_disconnect("A")     │
│ mark offline, keep history         │
└────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────┐
│ Device A (user reconnects)         │
│ send "welcome" again               │
│ connection_epoch = 1 (not 0)       │
└────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────┐
│ Server receives welcome (epoch=1)  │
│ SessionCoordinator:                │
│ .handle_device_connect("A", epoch=1)
│ Send full history + current state  │
│ chunk_seq resets to 0              │
│ (new connection = new seq stream)  │
└────────────────────────────────────┘
                │
                ↓
┌────────────────────────────────────┐
│ Device A's UI shows captions again │
│ (Filled in from history)           │
│ Live audio continues from epoch=1  │
│ No duplicates (dedup by            │
│  device_id, epoch, chunk_seq)      │
└────────────────────────────────────┘
```

---

## SECTION 6: STEP-BY-STEP SETUP & DEPLOYMENT GUIDE

### 6.1 Prerequisites (What You Need Before Starting)

**On Your Laptop (where server runs)**:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip package manager (`pip --version`)
- [ ] ~1 GB disk for Vosk model download (or skip if using Whisper API)
- [ ] RTX 4050 GPU (optional, but faster for ASR)
- [ ] Terminal/command line access

**Browsers (for device clients)**:
- [ ] Chrome, Firefox, Safari, or Edge (any modern browser)
- [ ] Microphone access enabled
- [ ] Same WiFi network as server (or localhost:8000 if testing on same machine)

### 6.2 Installation Steps

#### A. Clone/Setup Project

```bash
# Navigate to your project
cd /Users/richa.agrawal1/Desktop/Project_mute

# Initialize git (already done)
# git init
# git add .
# git commit -m "Initial commit"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-socketio python-socketio
pip install librosa soundfile numpy scipy
pip install vosk  # For Vosk ASR model
pip install pytest  # For testing
```

#### B. Download Vosk Model (Once)

```bash
# Create models directory
mkdir -p models/vosk

# Download English model (~60 MB)
cd models/vosk
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip
unzip vosk-model-en-us-0.42-gigaspeech.zip
# You should now have: models/vosk/vosk-model-en-us-0.42-gigaspeech/

cd /Users/richa.agrawal1/Desktop/Project_mute
```

Or if you prefer Whisper API:
```bash
# (Skip Vosk, use OpenAI Whisper instead)
pip install openai
# Set environment variable:
export OPENAI_API_KEY="sk-..."  # Get from https://platform.openai.com/account/api-keys
```

#### C. Create Project Directory Structure

```bash
# From project root:
mkdir -p src/{backend,frontend}
mkdir -p src/backend/{models,storage,workers}
mkdir -p src/frontend/{html,js,css}
mkdir -p tests/{backend,frontend}
mkdir -p data/{recordings,sessions}

# Structure
Project_mute/
├── planning/
│   ├── CLAUDE.md
│   ├── DECISIONS.md
│   ├── *.pdf
├── src/
│   ├── backend/
│   │   ├── app.py                 # Flask main app
│   │   ├── constants.py            # Shared constants
│   │   ├── models.py               # Entry, SessionCoordinator classes
│   │   ├── network.py              # WebSocket message handling
│   │   ├── sync.py                 # Clock offset calibration
│   │   ├── storage.py              # SQLite interface
│   │   ├── workers/
│   │   │   ├── asr_worker.py       # Vosk/Whisper wrapper
│   │   │   └── queue_manager.py    # Job queue
│   │   └── models/
│   │       └── vosk/               # Downloaded Vosk model
│   ├── frontend/
│   │   ├── index.html              # Main UI
│   │   ├── recorder.html           # Device client (audio capture)
│   │   ├── js/
│   │   │   ├── socket-client.js    # WebSocket connection
│   │   │   ├── audio-capture.js    # Web Audio API
│   │   │   ├── ui.js               # Caption display
│   │   │   └── utils.js
│   │   └── css/
│   │       └── style.css           # Styling
├── data/
│   ├── recordings/                 # Pre-recorded audio files for demo
│   │   ├── speaker_a.wav           # 60+ seconds of speech
│   │   └── speaker_b.wav
│   └── sessions/                   # Saved transcripts (SQLite)
├── tests/
│   ├── test_models.py
│   ├── test_asr.py
│   └── test_network.py
├── requirements.txt                # Python dependencies
├── FEASIBILITY_AND_ARCHITECTURE.md # This document
└── .gitignore

```

### 6.3 Running the Server

```bash
# Make sure venv is activated
source venv/bin/activate

# Set Flask settings
export FLASK_APP=src/backend/app.py
export FLASK_ENV=development
export PYTHONUNBUFFERED=1

# Start server
flask run --host=0.0.0.0 --port=5000

# Output should be:
# WARNING: This is a development server. Do not use it in production.
# Running on http://0.0.0.0:5000
```

### 6.4 Running the Device Clients (Browsers)

**Client 1 (Device A - Speaker)**:
```
Open browser: http://localhost:5000/recorder.html
Device Name: "Speaker A"
OR on another device on same network:
http://192.168.1.100:5000/recorder.html  (replace with your laptop's IP)
```

**Client 2 (Device B - Speaker)**:
```
Open another browser tab or second device:
http://localhost:5000/recorder.html
Device Name: "Speaker B"
```

**Monitor UI (Optional)**:
```
Open browser: http://localhost:5000/
(Shows real-time captions as they arrive)
```

### 6.5 Configuration File (config.py)

```python
# src/backend/config.py

import os

class Config:
    """Base configuration."""
    
    # Audio
    SAMPLE_RATE = 16000
    AUDIO_FORMAT = "PCM16"
    CHANNELS = 1
    CHUNK_DURATION = 0.4  # seconds
    
    # ASR
    ASR_ENGINE = os.getenv("ASR_ENGINE", "vosk")  # "vosk" or "whisper"
    VOSK_MODEL_PATH = "./models/vosk/vosk-model-en-us-0.42-gigaspeech"
    ASR_TIMEOUT = 10  # seconds before timing out
    ASR_WORKERS = 2  # Concurrent ASR jobs
    
    # Sync
    OVERLAP_SLACK = 0.15
    CLOCK_OFFSET_SAMPLES = 5
    CLOCK_OFFSET_REPEAT_INTERVAL = 60  # seconds
    CLOCK_OFFSET_MAX_RTT = 0.5
    
    # Storage
    DATABASE_PATH = "./data/sessions/session_{session_id}.sqlite"
    JSONL_BACKUP_PATH = "./data/sessions/session_{session_id}.jsonl"
    
    # Network
    LATENCY_CEILING = 5.0  # seconds
    SESSION_TIMEOUT = 15 * 60  # 15 minutes
    MAX_DEVICES_PER_SESSION = 4  # But using 2 for this hackathon
    
    # Thresholds (tune after testing)
    HIGH_THRESHOLD = 0.75
    LOW_THRESHOLD = 0.55
    LOUDNESS_GATE = -40  # dBFS
    MIN_SPEECH_RMS = 0.02
    ENROLL_MIN_SIMILARITY = 0.7
```

### 6.6 Docker Option (Advanced, Optional)

If you want to containerize for easy deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Vosk model
RUN mkdir -p models/vosk
RUN wget -O models/vosk/model.zip https://alphacephei.com/vosk/models/vosk-model-en-us-0.42-gigaspeech.zip
RUN cd models/vosk && unzip model.zip

COPY src/ src/

ENV FLASK_APP=src/backend/app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

Build and run:
```bash
docker build -t project-mute .
docker run -p 5000:5000 project-mute
```

---

## SECTION 7: DETAILED CODING TIMELINE (Realistic Estimates)

### Assumptions
- 1 developer (you)
- Python 3.9+ experience
- Vosk ASR (local, no API costs)
- 2 browser clients
- Pre-recorded audio for demo
- No TTS, no auth, no encryption

### Module-by-Module Timeline

| # | Module | Complexity | Est. Time | Notes |
|---|--------|-----------|-----------|-------|
| 1 | **Shared Models** | Low | 1-2 hrs | Entry dataclass, constants, basic Entry tests |
| 2 | **Sync Module** | Low | 1-2 hrs | Clock offset calibration, fake clock |
| 3 | **Network Module** | Medium | 2-3 hrs | WebSocket message protocol, JSON serialization |
| 4 | **Storage (SQLite)** | Low | 1-2 hrs | Schema, INSERT/SELECT, JSONL backup |
| 5 | **SessionCoordinator** | Medium | 2-3 hrs | State management, deduplication, entry release |
| 6 | **ASR Worker** | Low | 1-2 hrs | Vosk wrapper, error handling, queue |
| 7 | **Flask Backend (Main App)** | Medium | 3-4 hrs | Route setup, socket events, threading |
| 8 | **Browser Device Client** | Medium | 3-4 hrs | Audio capture, WebSocket client, reconnect |
| 9 | **UI Dashboard** | Low | 2-3 hrs | Caption display, speaker labels, CSS |
| 10 | **Integration & Testing** | Medium | 3-4 hrs | End-to-end tests, pre-recorded demo, debugging |
| | **TOTAL** | | **20-30 hrs** | 3-4 days coding, ~8-10 hrs/day |

**Fast-Path Option** (If time-crunched):
- Skip Sync (use server clock only)
- Skip reconnect handling
- Use pre-recorded files only
- Simpler UI (no speaker labels)
- **Reduced time: 12-15 hrs (~2 days)**

---

## SECTION 8: KNOWN RISKS & MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| **Vosk latency too high** | Medium | High | Benchmark first (30 min), switch to Whisper API if needed |
| **WebSocket disconnects frequently** | Low | Medium | Add exponential backoff reconnect (2-3 hrs to implement) |
| **SQLite write locks** | Low | Medium | Use PRAGMA journal_mode=WAL, or Redis if scaling |
| **Audio quality (mic noise)** | Medium | Low | Add noise gate pre-processing, document in README |
| **Clock drift > 150ms** | Low | Medium | More frequent offset sampling (5 samples every 30s) |
| **Browser Web Audio API issues** | Low | Low | Test in Chrome first, then Firefox/Safari |
| **Out-of-sync timestamps** | Medium | Medium | Use server time as ground truth, client adjusts |
| **ASR False positives** | Medium | Low | Display confidence scores, let users ignore wrong captions |
| **Data loss on session end** | Very Low | Critical | Dual write to SQLite + JSONL, validate on read |

**Top 3 Priority Mitigations**:
1. **Run Vosk benchmark BEFORE full coding** (this task #5 in your list)
2. **Pre-record demo audio files** (reduces 1 hour of testing time)
3. **Test browser WebSocket** (30 min - write minimal test client first)

---

## SECTION 9: FILE-BY-FILE CODING CHECKLIST

### Backend Files to Create

```python
# ============================================
# 1. src/backend/constants.py
# ============================================
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.4
OVERLAP_SLACK = 0.15
LATENCY_CEILING = 5.0
# ... (30 lines)

# ============================================
# 2. src/backend/models.py
# ============================================
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class Entry:
    entry_id: str
    session_id: str
    source: str
    # ... (fields from Section 4.2)
    
    def to_dict(self):
        # Serialize to JSON
        pass

class SessionCoordinator:
    """Session state, sync, buffering."""
    def __init__(self, session_id: str):
        pass
    
    def receive_audio(self, entry):
        pass
    # ... (methods from Section 4.4)

# ============================================
# 3. src/backend/sync.py
# ============================================
class SyncModule:
    """Clock offset calibration."""
    def __init__(self):
        self.device_offsets = {}
    
    def handle_clock_sample(self, device_id, rtt):
        # Vosk/Whisper benchmark measures RTT
        # Keep lowest 5 samples, discard > 0.5s
        pass
    
    def get_server_time(self):
        # Return current time
        pass

# ============================================
# 4. src/backend/network.py
# ============================================
def build_welcome_response(session_id, history):
    """Create welcome message."""
    return {
        "type": "welcome",
        "session_id": session_id,
        "history": [e.to_dict() for e in history],
    }

def build_caption_message(entry):
    """Create caption message."""
    return {
        "type": "caption",
        "entry_id": entry.entry_id,
        "text": entry.text,
        # ... (fields from Section 4.3)
    }

# ============================================
# 5. src/backend/storage.py
# ============================================
import sqlite3

class Storage:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_schema()
    
    def init_schema(self):
        """Create tables (from Section 4.5)."""
        pass
    
    def save_entry(self, entry):
        """Insert entry into DB."""
        pass
    
    def get_session_history(self, session_id):
        """Retrieve all entries for session."""
        pass
    
    def save_jsonl_backup(self, session_id, entries):
        """Write JSONL safety copy."""
        pass

# ============================================
# 6. src/backend/workers/asr_worker.py
# ============================================
from vosk import Model, KaldiRecognizer
import json

class ASRWorker:
    def __init__(self, model_type="vosk"):
        if model_type == "vosk":
            self.model = Model(lang="en-us")
    
    def process_chunk(self, audio_bytes, entry_id):
        """audio_bytes → (text, confidence)."""
        recognizer = KaldiRecognizer(self.model, 16000)
        recognizer.AcceptWaveform(audio_bytes)
        result = json.loads(recognizer.Result())
        # Extract text and confidence
        return text, confidence

class WorkerQueue:
    """Thread pool for concurrent ASR jobs."""
    def __init__(self, num_workers=2):
        from queue import Queue
        from threading import Thread
        self.queue = Queue()
        self.workers = [
            Thread(target=self._worker_loop, daemon=True)
            for _ in range(num_workers)
        ]
        for w in self.workers:
            w.start()
    
    def enqueue(self, entry):
        self.queue.put(entry)
    
    def _worker_loop(self):
        asr = ASRWorker()
        while True:
            entry = self.queue.get()
            text, confidence = asr.process_chunk(
                entry.audio_bytes, entry.entry_id
            )
            # Callback: coordinator.receive_asr_result()
            self.queue.task_done()

# ============================================
# 7. src/backend/app.py (MAIN FLASK APP)
# ============================================
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import base64
from src.backend.models import Entry, SessionCoordinator
from src.backend.storage import Storage
from src.backend.workers.asr_worker import WorkerQueue
import uuid
import time

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = "your-secret-key"
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
sessions = {}  # session_id → SessionCoordinator
storage = Storage("./data/sessions")
asr_queue = WorkerQueue(num_workers=2)

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/recorder.html")
def recorder():
    return render_template("recorder.html")

@socketio.on("connect")
def handle_connect(auth):
    print(f"Client connected: {auth}")
    emit("response", {"data": "Connected"})

@socketio.on("welcome")
def handle_welcome(data):
    """Device client sends: device_id, device_name, connection_epoch."""
    device_id = data.get("device_id")
    session_id = data.get("session_id", f"sess_{uuid.uuid4().hex[:8]}")
    
    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = SessionCoordinator(session_id)
    
    coordinator = sessions[session_id]
    coordinator.handle_device_connect(device_id)
    
    # Send welcome response
    history = [e.to_dict() for e in coordinator.released_entries()]
    emit("welcome", {
        "session_id": session_id,
        "server_time": time.time(),
        "history": history,
    })

@socketio.on("chunk")
def handle_chunk(data):
    """Device sends audio chunk."""
    device_id = data.get("device_id")
    session_id = data.get("session_id")
    audio_b64 = data.get("audio_bytes")
    
    # Decode audio
    audio_bytes = base64.b64decode(audio_b64)
    
    # Create entry
    entry = Entry(
        entry_id=uuid.uuid4().hex,
        session_id=session_id,
        source="asr",
        device_id=device_id,
        start_ts=data.get("start_ts"),
        end_ts=data.get("end_ts"),
        audio_bytes=audio_bytes,
        quality=data.get("quality"),
        connection_epoch=data.get("connection_epoch"),
        chunk_seq=data.get("chunk_seq"),
        is_final=False,
        is_late=False,
        speaker=device_id,
        created_at=datetime.now(),
    )
    
    # Receive and queue for ASR
    coordinator = sessions[session_id]
    coordinator.receive_audio(entry)
    asr_queue.enqueue(entry)
    
    # Send ACK
    emit("ack", {"chunk_seq": data.get("chunk_seq")})

# Callback from ASR worker
def on_asr_result(entry_id, text, confidence, session_id):
    """Called when ASR completes."""
    coordinator = sessions[session_id]
    coordinator.receive_asr_result(entry_id, text, confidence)
    
    # Broadcast caption to all clients
    entry = coordinator.get_entry(entry_id)
    socketio.emit("caption", {
        "entry_id": entry_id,
        "text": text,
        "confidence": confidence,
        "is_final": True,
    }, room=session_id)

@socketio.on("end_session")
def handle_end_session(data):
    """Device signals session end."""
    device_id = data.get("device_id")
    session_id = data.get("session_id")
    
    coordinator = sessions[session_id]
    coordinator.handle_device_disconnect(device_id)
    
    # Check if all devices done
    if coordinator.is_session_done():
        # Save to storage
        storage.save_session(session_id, coordinator.entries)
        storage.save_jsonl_backup(session_id, coordinator.entries)
        
        # Notify clients
        socketio.emit("session_ended", {
            "session_id": session_id,
            "total_duration": time.time() - coordinator.started_at,
            "transcript_saved": True,
        }, room=session_id)
        
        # Cleanup
        del sessions[session_id]

if __name__ == "__main__":
    import os
    os.makedirs("./data/sessions", exist_ok=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
```

### Frontend Files to Create

```html
<!-- ============================================ -->
<!-- templates/index.html (Dashboard/Monitor) -->
<!-- ============================================ -->
<!DOCTYPE html>
<html>
<head>
    <title>Project Mute - Transcript Monitor</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>Real-Time Transcript</h1>
        <div id="captions" class="caption-box">
            <p class="placeholder">Waiting for captions...</p>
        </div>
        <div id="status" class="status">Status: Not connected</div>
    </div>
    
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="/static/js/socket-client.js"></script>
    <script src="/static/js/ui.js"></script>
</body>
</html>

<!-- ============================================ -->
<!-- templates/recorder.html (Device Client) -->
<!-- ============================================ -->
<!DOCTYPE html>
<html>
<head>
    <title>Project Mute - Audio Capture</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="container">
        <h1>Device Audio Capture</h1>
        
        <div class="device-setup">
            <label>Device Name:</label>
            <input type="text" id="deviceName" placeholder="e.g., Speaker A">
            
            <label>Audio Source:</label>
            <select id="audioSource">
                <option value="microphone">Live Microphone</option>
                <option value="recorded">Pre-recorded File</option>
            </select>
            
            <input type="file" id="audioFile" accept=".wav,.mp3" style="display:none">
        </div>
        
        <div class="controls">
            <button id="startBtn" onclick="startCapture()">Start</button>
            <button id="stopBtn" onclick="stopCapture()" disabled>Stop</button>
            <button id="resetBtn" onclick="resetConnection()">Reset Connection</button>
        </div>
        
        <div id="status" class="status">Status: Not connected</div>
        <div id="localCaptions" class="caption-box">
            <p class="placeholder">No captions yet...</p>
        </div>
    </div>
    
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="/static/js/socket-client.js"></script>
    <script src="/static/js/audio-capture.js"></script>
    <script src="/static/js/ui.js"></script>
</body>
</html>

<!-- ============================================ -->
<!-- static/js/socket-client.js -->
<!-- ============================================ -->
class SocketClient {
    constructor(deviceId = null) {
        this.socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 10,
        });
        
        this.deviceId = deviceId || `device_${Math.random().toString(36).substr(2, 9)}`;
        this.sessionId = null;
        this.connectionEpoch = 0;
        this.chunkSeq = 0;
        
        this.setupListeners();
    }
    
    setupListeners() {
        this.socket.on("connect", () => {
            console.log("Connected to server");
            this.sendWelcome();
        });
        
        this.socket.on("welcome", (data) => {
            console.log("Received welcome:", data);
            this.sessionId = data.session_id;
            this.onWelcome(data);  // Callback for app
        });
        
        this.socket.on("caption", (data) => {
            console.log("Received caption:", data);
            this.onCaption(data);  // Callback for app
        });
        
        this.socket.on("ack", (data) => {
            console.log("Chunk ACK:", data.chunk_seq);
        });
        
        this.socket.on("disconnect", () => {
            console.log("Disconnected from server");
            this.onDisconnect();  // Callback
        });
        
        this.socket.on("session_ended", (data) => {
            console.log("Session ended:", data);
            this.onSessionEnded(data);  // Callback
        });
    }
    
    sendWelcome() {
        this.socket.emit("welcome", {
            device_id: this.deviceId,
            device_name: document.getElementById("deviceName")?.value || "Anonymous",
            connection_epoch: this.connectionEpoch,
        });
    }
    
    sendChunk(audioBytes, startTs, endTs, quality = "ok") {
        // Convert bytes to base64
        const b64 = btoa(String.fromCharCode(...new Uint8Array(audioBytes)));
        
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
    
    endSession() {
        this.socket.emit("end_session", {
            device_id: this.deviceId,
            session_id: this.sessionId,
            reason: "manual",
        });
    }
    
    reconnect() {
        this.connectionEpoch++;
        this.chunkSeq = 0;
        this.socket.connect();
    }
    
    // Callbacks (override in app)
    onWelcome(data) {}
    onCaption(data) {}
    onDisconnect() {}
    onSessionEnded(data) {}
}

<!-- ============================================ -->
<!-- static/js/audio-capture.js -->
<!-- ============================================ -->
class AudioCapture {
    constructor() {
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.recording = false;
        this.startTime = 0;
        this.chunkDuration = 0.4;  // 400ms
        
        this.socketClient = new SocketClient();
    }
    
    async startMicrophone() {
        try {
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: { echoCancellation: true, noiseSuppression: true }
            });
            this.setupAudioContext();
            this.recording = true;
            this.startTime = performance.now();
            document.getElementById("status").innerText = "Status: Recording...";
        } catch (error) {
            alert("Microphone access denied: " + error.message);
        }
    }
    
    setupAudioContext() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000,
        });
        
        const source = this.audioContext.createMediaStreamSource(this.mediaStream);
        const bufferSize = 6400;  // 400ms at 16kHz
        
        // Use ScriptProcessor (or AudioWorklet for production)
        this.processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);
        
        this.processor.onaudioprocess = (event) => {
            const inputData = event.inputBuffer.getChannelData(0);
            const audioBytes = this.floatTo16BitPCM(inputData);
            
            const currentTime = (performance.now() - this.startTime) / 1000;
            this.socketClient.sendChunk(
                audioBytes,
                currentTime - this.chunkDuration,
                currentTime,
                "ok"
            );
        };
        
        source.connect(this.processor);
        this.processor.connect(this.audioContext.destination);
    }
    
    floatTo16BitPCM(floatArray) {
        const buffer = new Int16Array(floatArray.length);
        for (let i = 0; i < floatArray.length; i++) {
            const s = Math.max(-1, Math.min(1, floatArray[i]));
            buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return buffer.buffer;
    }
    
    stopCapture() {
        this.recording = false;
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.processor) {
            this.processor.disconnect();
        }
        this.socketClient.endSession();
        document.getElementById("status").innerText = "Status: Stopped";
    }
}

let audioCapture;

function startCapture() {
    const source = document.getElementById("audioSource").value;
    if (source === "microphone") {
        audioCapture = new AudioCapture();
        audioCapture.startMicrophone();
    } else {
        // Load recorded file
        const file = document.getElementById("audioFile").files[0];
        // Playback logic...
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

<!-- ============================================ -->
<!-- static/js/ui.js -->
<!-- ============================================ -->
class CaptionDisplay {
    constructor() {
        this.captionBox = document.getElementById("captions") || document.getElementById("localCaptions");
        this.captions = [];
    }
    
    addCaption(data) {
        const entry = {
            entryId: data.entry_id,
            text: data.text,
            speaker: data.speaker || "Speaker",
            isLate: data.is_late || false,
            isFinal: data.is_final || false,
        };
        
        this.captions.push(entry);
        this.render();
    }
    
    render() {
        const html = this.captions.map(caption => `
            <div class="caption ${caption.isLate ? 'late' : ''}">
                <strong>${caption.speaker}:</strong> ${caption.text}
                ${caption.isLate ? '<span class="tag">earlier</span>' : ''}
            </div>
        `).join("");
        
        this.captionBox.innerHTML = html || '<p class="placeholder">No captions yet...</p>';
    }
}

let captionDisplay;

document.addEventListener("DOMContentLoaded", () => {
    captionDisplay = new CaptionDisplay();
    
    // Hook into socket client
    if (audioCapture && audioCapture.socketClient) {
        audioCapture.socketClient.onCaption = (data) => {
            captionDisplay.addCaption(data);
        };
    }
});

<!-- ============================================ -->
<!-- static/css/style.css -->
<!-- ============================================ -->
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

.caption-box {
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    min-height: 200px;
    max-height: 500px;
    overflow-y: auto;
    margin: 20px 0;
}

.caption {
    padding: 10px;
    margin: 5px 0;
    background: white;
    border-left: 4px solid #007bff;
    border-radius: 2px;
    line-height: 1.6;
}

.caption.late {
    border-left-color: #ffc107;
    opacity: 0.8;
}

.caption .tag {
    display: inline-block;
    background: #ffc107;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.8em;
    margin-left: 10px;
}

.caption strong {
    color: #007bff;
}

.placeholder {
    color: #999;
    text-align: center;
    padding: 20px;
}

.status {
    padding: 10px;
    background: #e3f2fd;
    border-radius: 4px;
    color: #1976d2;
    font-size: 0.9em;
    margin: 10px 0;
}

.controls {
    display: flex;
    gap: 10px;
    margin: 15px 0;
}

button {
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
}

button:hover {
    background: #0056b3;
}

button:disabled {
    background: #ccc;
    cursor: not-allowed;
}

input[type="text"], select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin: 5px 0;
    width: 100%;
}

.device-setup {
    margin: 15px 0;
    padding: 15px;
    background: #f0f0f0;
    border-radius: 4px;
}

.device-setup label {
    display: block;
    margin-top: 10px;
    font-weight: bold;
}
```

---

## SECTION 10: QUICK START (TL;DR)

**Do this first**:

1. **Ensure Vosk model downloaded**: `~/models/vosk/vosk-model-en-us-0.42-gigaspeech/`
2. **Install Python deps**: `pip install -r requirements.txt`
3. **Start server**: `python src/backend/app.py` → runs on `http://localhost:5000`
4. **Open browsers**:
   - Tab 1: `http://localhost:5000/recorder.html` (Device A)
   - Tab 2: `http://localhost:5000/recorder.html` (Device B)
   - Tab 3: `http://localhost:5000/` (Monitor)
5. **Test**:
   - Name Device A
   - Click "Start"
   - Speak into microphone
   - See captions appear in ~2 seconds

**Expected Latency**: 1.5-2.5 seconds (Vosk) or 0.5-1.5 seconds (Whisper API)

---

## SECTION 11: QUESTIONS FOR YOU

Before you start coding, clarify these:

1. **ASR Benchmark**: Do you have RTX 4050 available with CUDA installed? If not, we use Vosk (CPU-friendly).
2. **Pre-recorded files**: Can you record 2x ~60-second audio clips (one per speaker) for demo? This makes testing deterministic.
3. **Browser choice**: Will you test on Chrome first, then others?
4. **Deployment**: Keep everything local (localhost + LAN), or cloud?
5. **Session persistence**: Save transcripts to disk after session end (SQLite)? Or just in-memory?

---

## APPENDIX A: GLOSSARY

| Term | Definition |
|------|-----------|
| **Entry** | One piece of data (audio chunk, transcribed text, metadata) flowing through the system |
| **Chunk** | 400ms of PCM16 audio from a device |
| **Coordinator** | Server-side component managing session state (buffering, syncing, deduplication) |
| **Overlap** | Two speakers talking at the same time (handle with 150ms slack) |
| **ASR** | Automatic Speech Recognition (Vosk/Whisper turning audio → text) |
| **Latency Ceiling** | Max acceptable delay: 5 seconds from speech end to caption display |
| **Speaker ID** | Which device/person spoke (device_a, device_b, or name) |
| **Connection Epoch** | Counter for device reconnections (0, 1, 2...) |
| **Chunk Seq** | Sequential counter for audio chunks within a connection |
| **Deduplication** | Drop duplicate chunks from reconnects (key: device_id, epoch, chunk_seq) |
| **Late Entry** | Caption arriving after latency ceiling (shown at bottom with "earlier" tag) |

---

## APPENDIX B: TROUBLESHOOTING

### Server won't start
```
ERROR: Port 5000 already in use
SOLUTION: lsof -i :5000 # Kill the process, then restart
```

### Vosk model not found
```
ERROR: Model lang not found
SOLUTION: Download manually, set VOSK_MODEL_PATH in config.py
```

### Browser can't connect to server
```
ERROR: WebSocket connection failed
SOLUTION: Check firewall, use 0.0.0.0:5000 (not localhost from other devices)
```

### Audio quality is terrible
```
ERROR: Noise, crackling, echoes
SOLUTION: Enable echoCancellation and noiseSuppression in getUserMedia()
```

### Transcriptions are wrong
```
ERROR: ASR accuracy is low
SOLUTION: Adjust LOUDNESS_GATE, MIN_SPEECH_RMS, HIGH_THRESHOLD (Section 5)
```

---

**END OF FEASIBILITY & ARCHITECTURE DOCUMENT**

This document is complete and ready for coding. All sections reference each other for continuity. Start with Section 1 (decisions), then Section 6 (setup), then code modules in order (Section 9).

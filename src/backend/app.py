"""Project Mute - Main Flask + SocketIO Application."""

import os
import sys
import time
import uuid
import base64
import numpy as np
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging

from .models import Entry, SessionCoordinator
from .storage import Storage
from .workers.asr_worker import WorkerQueue
from .network import *
from .constants import *

# ============ SETUP ============

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(
    __name__,
    static_folder=str(Path(__file__).parent.parent / "frontend" / "static"),
    template_folder=str(Path(__file__).parent.parent / "frontend" / "templates")
)
app.config["SECRET_KEY"] = "project-mute-hackathon-secret"

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins=CORS_ORIGINS,
    async_mode="threading"
)

# Global state
sessions: dict = {}  # session_id → SessionCoordinator
storage: Storage = None
asr_queue: WorkerQueue = None


# ============ ASR CALLBACK ============

def on_asr_result(entry_id: str, text: str, confidence: float, session_id: str):
    """Callback when ASR worker completes transcription."""
    if session_id not in sessions:
        return

    coordinator = sessions[session_id]
    coordinator.receive_asr_result(entry_id, text, confidence)

    # Get updated entry
    entry = coordinator.get_entry(entry_id)
    if not entry:
        return

    # Build caption message
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

    # Broadcast to all clients in session
    socketio.emit("caption", caption_msg, room=session_id)


# ============ ROUTES ============

@app.route("/")
def dashboard():
    """Monitor/Dashboard UI."""
    return render_template("index.html")


@app.route("/recorder.html")
def recorder():
    """Device recorder UI."""
    return render_template("recorder.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "active_sessions": len(sessions),
        "asr_queue_size": asr_queue.queue_size() if asr_queue else 0
    }


# ============ WEBSOCKET EVENTS ============

@socketio.on("connect")
def handle_connect():
    """Client connects to WebSocket."""
    print(f"[WS] Client connected: {request.sid[:8]}")


@socketio.on("welcome")
def handle_welcome(data):
    """Device client sends welcome (initialization)."""

    device_id = data.get("device_id", f"device_{uuid.uuid4().hex[:8]}")
    device_name = data.get("device_name", device_id)
    connection_epoch = data.get("connection_epoch", 0)
    session_id = data.get("session_id")

    # Create or get session
    if not session_id or session_id not in sessions:
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        sessions[session_id] = SessionCoordinator(session_id)
        print(f"[NEW SESSION] {session_id}")

    coordinator = sessions[session_id]
    coordinator.handle_device_connect(device_id, connection_epoch)

    # Get history (for new device joining)
    history = [e.to_dict() for e in coordinator.get_all_entries()]

    # Send welcome response
    emit("welcome", build_welcome_response(
        session_id=session_id,
        server_time=time.time(),
        history=history
    ))

    # Broadcast join message
    msg = build_text_message("system", f"{device_name} joined", time.time())
    socketio.emit("text_message", msg, room=session_id, skip_sid=None)


@socketio.on("chunk")
def handle_chunk(data):
    """Receive audio chunk from device."""

    device_id = data.get("device_id")
    session_id = data.get("session_id")
    audio_b64 = data.get("audio_bytes")

    if not session_id or session_id not in sessions:
        emit("error", build_error("session_not_found", "Session does not exist"))
        return

    try:
        # Decode audio from base64
        if not audio_b64:
            emit("error", build_error("empty_audio", "No audio data received"))
            return

        audio_bytes_raw = base64.b64decode(audio_b64)

        if not audio_bytes_raw or len(audio_bytes_raw) < 100:
            emit("error", build_error("audio_too_short", "Audio chunk too short"))
            return

        # Convert bytes to numpy array (16-bit PCM)
        audio_array = np.frombuffer(audio_bytes_raw, dtype=np.int16).astype(np.float32) / 32768.0

        # Create entry
        entry = Entry.create_audio(
            session_id=session_id,
            device_id=device_id,
            audio_bytes=audio_bytes_raw,
            start_ts=data.get("start_ts", time.time()),
            end_ts=data.get("end_ts", time.time()),
            quality=data.get("quality", "ok"),
            epoch=data.get("connection_epoch", 0),
            chunk_seq=data.get("chunk_seq", 0)
        )

        # Receive and queue
        coordinator = sessions[session_id]
        coordinator.receive_audio(entry)
        asr_queue.enqueue(entry)

        # Send ACK
        emit("ack", build_ack(data.get("chunk_seq", 0)))

    except Exception as e:
        print(f"[CHUNK ERROR] {e}")
        emit("error", build_error("chunk_failed", f"Chunk processing failed: {str(e)[:50]}"))


@socketio.on("end_session")
def handle_end_session(data):
    """Device ends session."""

    device_id = data.get("device_id")
    session_id = data.get("session_id")

    if session_id not in sessions:
        return

    coordinator = sessions[session_id]
    coordinator.handle_device_disconnect(device_id)

    # Broadcast message
    msg = build_text_message("system", f"{device_id} ended session", time.time())
    emit("text_message", msg, room=session_id)

    # Check if all devices ended
    if coordinator.is_session_done():
        # Save to storage
        all_devices = list(coordinator.device_epochs.keys())
        duration = coordinator.get_session_duration()
        entries = coordinator.get_entries_sorted()

        storage.save_session(session_id, all_devices, duration, entries)
        storage.save_jsonl_backup(session_id, entries)

        print(f"[SESSION ENDED] {session_id} - {len(entries)} entries, {duration:.1f}s")

        # Notify clients
        ended_msg = build_session_ended(session_id, duration, True)
        emit("session_ended", ended_msg, room=session_id)

        # Cleanup
        del sessions[session_id]


@socketio.on("disconnect")
def handle_disconnect():
    """Client disconnects."""
    print(f"[WS] Client disconnected: {request.sid[:8]}")


# ============ INITIALIZATION ============

def init_app():
    """Initialize app and globals."""
    global storage, asr_queue

    # Create required directories
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Validate Whisper model exists
    try:
        import whisper as whisper_module
        whisper_module.load_model("small")
        print(f"[ASR] ✅ Whisper model loaded successfully")
    except Exception as e:
        print(f"[FATAL] Whisper model not found!")
        print(f"[FATAL] Run: python -c \"import whisper; whisper.load_model('small')\"")
        print(f"[FATAL] Error: {e}")
        sys.exit(1)

    # Initialize storage
    storage = Storage(DATABASE_PATH)

    # Initialize ASR worker queue
    asr_queue = WorkerQueue(num_workers=ASR_WORKERS, callback=on_asr_result)

    print(f"[APP] Initialized: {HOST}:{PORT}")


# ============ MAIN ============

if __name__ == "__main__":
    init_app()
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        allow_unsafe_werkzeug=True
    )

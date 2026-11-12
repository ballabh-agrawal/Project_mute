"""Global constants and configuration for Project Mute."""

import os
from pathlib import Path

# ============ AUDIO CONFIGURATION ============
SAMPLE_RATE = 16000  # Hz (16 kHz, required by Whisper)
AUDIO_FORMAT = "PCM16"  # 16-bit signed integer
CHANNELS = 1  # Mono
CHUNK_DURATION = 0.4  # seconds (400ms)
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)  # 6400 samples

# ============ TIMESTAMP CONFIGURATION ============
# Unix seconds as float (e.g., 1699603200.123)
# 3 decimal places = 1ms precision
TIMESTAMP_FORMAT = "unix_seconds_float"  # Not changed, use directly
TIMESTAMP_DECIMALS = 3  # For display only, precision inherent in float

# ============ ASR CONFIGURATION ============
ASR_ENGINE = "whisper_local"  # "whisper_local" or "whisper_api"
WHISPER_MODEL = "small"  # tiny, base, small, medium, large
ASR_WORKERS = 2  # Concurrent Whisper jobs
ASR_TIMEOUT = 15  # seconds before timeout
ASR_LANGUAGE = "en"  # English only

# ============ SYNC & TIMING ============
OVERLAP_SLACK = 0.15  # seconds (150ms clock tolerance)
CLOCK_OFFSET_SAMPLES = 5
CLOCK_OFFSET_REPEAT_INTERVAL = 60  # seconds
CLOCK_OFFSET_MAX_RTT = 0.5  # seconds
LATENCY_CEILING = 5.0  # seconds (max acceptable delay)

# ============ SESSION CONFIGURATION ============
SESSION_TIMEOUT = 15 * 60  # 15 minutes in seconds
HEARTBEAT_INTERVAL = 5  # seconds between heartbeats
MAX_DEVICES_PER_SESSION = 4
SESSION_ID_PREFIX = "sess_"
DEVICE_ID_PREFIX = "device_"

# ============ SPEAKER IDENTIFICATION ============
# Strategy: Hybrid - user-provided name, fallback to device_id
# Example: user enters "Alice" → speaker="Alice"
#          user leaves blank → speaker="Speaker A" or device_id
SPEAKER_ID_STRATEGY = "hybrid"  # hybrid, device_id, or name
DEFAULT_SPEAKER_FORMAT = "Speaker {number}"  # {number} = A, B, C...

# ============ DISPLAY & UI CONFIGURATION ============
# Caption ordering: Chronological by start_ts (overlapping speakers OK)
CAPTION_ORDER = "chronological"  # chronological or arrival_order

# Late entries: Inline with visual tag
LATE_ENTRY_DISPLAY = "inline_with_tag"  # inline_with_tag or separate_section
LATE_ENTRY_TAG_TEXT = "earlier"  # Display text for late entries
LATE_ENTRY_THRESHOLD = LATENCY_CEILING  # Use same as latency ceiling

# ============ DEDUPLICATION ============
# Key: (device_id, connection_epoch, chunk_seq) must be unique
# Handles retransmits, out-of-order, and reconnects
DEDUP_KEY_STRATEGY = "device_epoch_seq"  # Hardcoded, not configurable

# ============ STORAGE CONFIGURATION ============
DATA_DIR = Path(__file__).parent.parent.parent / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
RECORDINGS_DIR = DATA_DIR / "recordings"

# Create directories if not exist
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = str(SESSIONS_DIR / "main.sqlite")
JSONL_BACKUP_PATTERN = str(SESSIONS_DIR / "{session_id}.jsonl")

# ============ SERVER CONFIGURATION ============
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000
DEBUG = True
CORS_ORIGINS = "*"  # Allow all origins for hackathon

# ============ THRESHOLDS (Tuning Parameters) ============
# Speaker identification confidence thresholds
HIGH_THRESHOLD = 0.75  # High confidence
LOW_THRESHOLD = 0.55   # Low confidence
LOUDNESS_GATE = -40    # dBFS (noise floor)
MIN_SPEECH_RMS = 0.02  # Minimum energy for speech detection
ENROLL_MIN_SIMILARITY = 0.7  # For speaker enrollment (future)

# ============ PRE-RECORDED FILES ============
# Expected format: WAV (PCM16, 16kHz, mono)
DEMO_SPEAKER_A_FILE = RECORDINGS_DIR / "speaker_a.wav"
DEMO_SPEAKER_B_FILE = RECORDINGS_DIR / "speaker_b.wav"

# ============ LOGGING ============
LOG_LEVEL = "INFO"
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"

# ============ TESTING ============
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "tests" / "data"

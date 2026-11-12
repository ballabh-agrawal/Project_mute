"""Core data models for Project Mute."""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, List
import uuid
import json
import base64
import time

from .constants import (
    LATENCY_CEILING, SPEAKER_ID_STRATEGY, DEFAULT_SPEAKER_FORMAT,
    DEDUP_KEY_STRATEGY
)


@dataclass
class Entry:
    """Single event in the system (audio chunk, transcription, metadata)."""

    entry_id: str  # UUID4 hex (32 chars)
    session_id: str  # UUID4 hex prefix (8 chars as sess_ABC123)
    source: str  # "asr", "audio", "metadata"
    device_id: str  # "device_a", "device_b", etc

    start_ts: float  # Unix seconds (e.g., 1699603200.123)
    end_ts: float    # Unix seconds

    speaker: Optional[str] = None  # "Alice", "Speaker A", "device_a"
    speaker_confidence: Optional[float] = None  # 0.0-1.0
    text: Optional[str] = None  # Transcribed text
    audio_bytes: Optional[bytes] = None  # Raw PCM16 audio
    quality: Optional[str] = None  # "ok" or "low_quality"

    is_final: bool = False  # True when ASR complete
    is_late: bool = False   # True if arrived after latency ceiling

    connection_epoch: int = 0  # Device reconnect counter
    chunk_seq: Optional[int] = None  # Sequential chunk number

    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def create_audio(session_id: str, device_id: str, audio_bytes: bytes,
                    start_ts: float, end_ts: float, quality: str = "ok",
                    epoch: int = 0, chunk_seq: int = 0) -> "Entry":
        """Factory method for audio entry."""
        return Entry(
            entry_id=uuid.uuid4().hex,
            session_id=session_id,
            source="asr",
            device_id=device_id,
            start_ts=start_ts,
            end_ts=end_ts,
            audio_bytes=audio_bytes,
            quality=quality,
            connection_epoch=epoch,
            chunk_seq=chunk_seq,
            is_final=False,
            speaker=None,
        )

    @staticmethod
    def create_caption(session_id: str, device_id: str, text: str,
                      start_ts: float, end_ts: float, speaker: str = None,
                      confidence: float = None) -> "Entry":
        """Factory method for caption entry."""
        return Entry(
            entry_id=uuid.uuid4().hex,
            session_id=session_id,
            source="caption",
            device_id=device_id,
            start_ts=start_ts,
            end_ts=end_ts,
            text=text,
            speaker=speaker or device_id,
            speaker_confidence=confidence or 0.9,
            is_final=True,
        )

    def to_dict(self) -> Dict:
        """Serialize to JSON-compatible dict."""
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()

        # Encode audio as base64 for JSON
        if self.audio_bytes:
            d["audio_bytes"] = base64.b64encode(self.audio_bytes).decode()
        else:
            d["audio_bytes"] = None

        return d

    @staticmethod
    def from_dict(d: Dict) -> "Entry":
        """Deserialize from JSON-compatible dict."""
        d = d.copy()

        # Decode audio from base64
        if d.get("audio_bytes") and isinstance(d["audio_bytes"], str):
            d["audio_bytes"] = base64.b64decode(d["audio_bytes"])

        # Parse datetime
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])

        return Entry(**d)


class SessionCoordinator:
    """Manages session state, syncing, buffering, deduplication."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.entries: Dict[str, Entry] = {}  # entry_id → Entry
        self.released_entries: List[Entry] = []  # Entries ready for UI

        # Sync and deduplication
        self.seen_chunks: set = set()  # (device_id, epoch, chunk_seq)
        self.device_clocks: Dict[str, float] = {}  # device_id → time offset
        self.device_epochs: Dict[str, int] = {}  # device_id → latest epoch

        # Status tracking
        self.active_devices: set = set()
        self.ended_devices: set = set()
        self.started_at = datetime.now()
        self.asr_pending: Dict[str, Entry] = {}  # entry_id → Entry (waiting)

        print(f"[SESSION] Created: {session_id}")

    def receive_audio(self, entry: Entry) -> Optional[str]:
        """
        Add audio chunk. Returns entry_id if accepted, None if duplicate.
        Checks deduplication key: (device_id, connection_epoch, chunk_seq)
        """
        key = (entry.device_id, entry.connection_epoch, entry.chunk_seq)

        if key in self.seen_chunks:
            print(f"[DEDUP] Ignoring duplicate: {key}")
            return None  # Duplicate

        self.seen_chunks.add(key)
        self.entries[entry.entry_id] = entry
        self.asr_pending[entry.entry_id] = entry

        print(f"[AUDIO] Received from {entry.device_id}: {entry.entry_id[:8]}... "
              f"({entry.end_ts - entry.start_ts:.2f}s)")

        return entry.entry_id

    def receive_asr_result(self, entry_id: str, text: str, confidence: float) -> None:
        """
        Update entry with ASR result and mark as ready for display.
        """
        if entry_id not in self.entries:
            print(f"[ASR ERROR] Entry not found: {entry_id}")
            return

        entry = self.entries[entry_id]
        entry.text = text
        entry.speaker_confidence = confidence
        entry.is_final = True

        if entry_id in self.asr_pending:
            del self.asr_pending[entry_id]

        self.release_entry(entry_id)

        print(f"[ASR] Completed {entry_id[:8]}...: '{text[:50]}...' (conf={confidence:.2f})")

    def release_entry(self, entry_id: str) -> None:
        """
        Mark entry as ready for UI display.
        Check if late (arrived after LATENCY_CEILING).
        """
        entry = self.entries[entry_id]

        # Check if late
        now = time.time()
        elapsed = now - entry.start_ts

        if elapsed > LATENCY_CEILING:
            entry.is_late = True
            print(f"[LATE] Entry arrived {elapsed:.2f}s after start (ceiling={LATENCY_CEILING})")

        if entry not in self.released_entries:
            self.released_entries.append(entry)

    def get_released_entries(self) -> List[Entry]:
        """
        Get all entries ready for display, clear the released list.
        """
        entries = self.released_entries[:]
        self.released_entries.clear()
        return entries

    def handle_device_connect(self, device_id: str, epoch: int = 0) -> None:
        """Device connected (or reconnected with new epoch)."""
        self.active_devices.add(device_id)
        self.device_epochs[device_id] = epoch
        self.device_clocks[device_id] = 0.0
        print(f"[CONNECT] {device_id} (epoch={epoch})")

    def handle_device_disconnect(self, device_id: str) -> None:
        """Device disconnected."""
        self.active_devices.discard(device_id)
        self.ended_devices.add(device_id)
        print(f"[DISCONNECT] {device_id}")

    def is_session_done(self) -> bool:
        """
        Check if all devices have ended.
        True if at least one device ended AND no devices are active.
        """
        return len(self.ended_devices) > 0 and len(self.active_devices) == 0

    def get_session_duration(self) -> float:
        """Time since session started (seconds)."""
        return (datetime.now() - self.started_at).total_seconds()

    def get_all_entries(self) -> List[Entry]:
        """Get all entries in session (for storage)."""
        return list(self.entries.values())

    def get_entries_sorted(self) -> List[Entry]:
        """Get entries sorted by start_ts (chronological order)."""
        entries = self.get_all_entries()
        entries.sort(key=lambda e: e.start_ts)
        return entries

    def get_device_count(self) -> int:
        """Number of unique devices that connected."""
        return len(self.device_epochs)

    def get_entry(self, entry_id: str) -> Optional[Entry]:
        """Get entry by ID."""
        return self.entries.get(entry_id)

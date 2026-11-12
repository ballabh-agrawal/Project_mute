"""WebSocket message protocol and builders."""

from typing import Dict, Any, List
from datetime import datetime


def build_welcome_response(session_id: str, server_time: float, history: List[Dict]) -> Dict:
    """Server → Client: Session established, send history."""
    return {
        "type": "welcome",
        "session_id": session_id,
        "server_time": server_time,
        "history": history,
    }


def build_caption_message(entry_id: str, device_id: str, speaker: str,
                         text: str, start_ts: float, end_ts: float,
                         is_final: bool, is_late: bool, confidence: float) -> Dict:
    """Server → Client: Transcribed caption for display."""
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
        "source": source,  # "system", "server"
        "text": text,
        "timestamp": timestamp,
    }


def build_session_ended(session_id: str, total_duration: float,
                       transcript_saved: bool, transcript_path: str = None) -> Dict:
    """Server → Client: Session ended."""
    return {
        "type": "session_ended",
        "session_id": session_id,
        "total_duration": total_duration,
        "transcript_saved": transcript_saved,
        "transcript_path": transcript_path,
        "timestamp": datetime.now().isoformat(),
    }


def build_error(code: str, message: str, device_id: str = None) -> Dict:
    """Server → Client: Error notification."""
    return {
        "type": "error",
        "code": code,  # "asr_timeout", "connection_lost", "tts_failed"
        "message": message,
        "device_id": device_id,
        "timestamp": datetime.now().isoformat(),
    }


def build_ack(chunk_seq: int) -> Dict:
    """Server → Client: Acknowledge chunk receipt."""
    return {
        "type": "ack",
        "chunk_seq": chunk_seq,
    }

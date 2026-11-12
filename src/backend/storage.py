"""SQLite storage for Project Mute sessions."""

import sqlite3
import json
from datetime import datetime
from typing import List
from pathlib import Path

from .models import Entry
from .constants import DATABASE_PATH, JSONL_BACKUP_PATTERN


class Storage:
    """SQLite database interface for sessions and entries."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    def init_schema(self) -> None:
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_device_epoch ON entries(device_id, connection_epoch)")

        conn.commit()
        conn.close()

        print(f"[STORAGE] Schema initialized: {self.db_path}")

    def save_session(self, session_id: str, devices: List[str], duration: float,
                    entries: List[Entry]) -> bool:
        """Save session metadata and all entries to database."""
        try:
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

            print(f"[STORAGE] Saved session {session_id}: {len(entries)} entries")
            return True

        except Exception as e:
            print(f"[STORAGE ERROR] Failed to save session: {e}")
            return False

    def save_jsonl_backup(self, session_id: str, entries: List[Entry]) -> bool:
        """Write JSONL safety copy of session."""
        try:
            path = JSONL_BACKUP_PATTERN.format(session_id=session_id)
            with open(path, "w") as f:
                for entry in entries:
                    f.write(json.dumps(entry.to_dict()) + "\n")

            print(f"[STORAGE] Saved JSONL backup: {path} ({len(entries)} entries)")
            return True

        except Exception as e:
            print(f"[STORAGE ERROR] Failed to save JSONL: {e}")
            return False

    def get_session_history(self, session_id: str) -> List[Entry]:
        """Retrieve all entries for a session (for new device join)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT entry_id, session_id, source, device_id, start_ts, end_ts,
                       speaker, speaker_confidence, text, audio_bytes, quality,
                       is_final, is_late, connection_epoch, chunk_seq, created_at
                FROM entries
                WHERE session_id = ?
                ORDER BY start_ts ASC
            """, (session_id,))

            entries = []
            for row in cursor.fetchall():
                entry = Entry(
                    entry_id=row[0], session_id=row[1], source=row[2],
                    device_id=row[3], start_ts=row[4], end_ts=row[5],
                    speaker=row[6], speaker_confidence=row[7], text=row[8],
                    audio_bytes=row[9], quality=row[10], is_final=row[11],
                    is_late=row[12], connection_epoch=row[13], chunk_seq=row[14],
                    created_at=datetime.fromisoformat(row[15])
                )
                entries.append(entry)

            conn.close()
            return entries

        except Exception as e:
            print(f"[STORAGE ERROR] Failed to get session history: {e}")
            return []

    def get_all_sessions(self) -> List[dict]:
        """Get all saved sessions."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT session_id, created_at, ended_at, devices, total_duration_sec FROM sessions")

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "session_id": row[0],
                    "created_at": row[1],
                    "ended_at": row[2],
                    "devices": json.loads(row[3]) if row[3] else [],
                    "total_duration_sec": row[4],
                })

            conn.close()
            return sessions

        except Exception as e:
            print(f"[STORAGE ERROR] Failed to get sessions: {e}")
            return []

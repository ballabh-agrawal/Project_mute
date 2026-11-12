"""ASR Worker - Whisper transcription."""

import whisper
import tempfile
import soundfile as sf
import numpy as np
from queue import Queue
from threading import Thread
import time
import os


class ASRWorker:
    """Local Whisper transcription worker."""

    def __init__(self, model_size: str = "small"):
        """Initialize Whisper model."""
        print(f"[ASR] Loading Whisper model: {model_size}")
        try:
            self.model = whisper.load_model(model_size)
            print(f"[ASR] Model loaded successfully")
        except Exception as e:
            print(f"[ASR ERROR] Failed to load model: {e}")
            raise

    def process_chunk(self, audio_bytes: bytes, entry_id: str) -> tuple:
        """
        Transcribe audio chunk using Whisper.
        Returns: (text, confidence)
        """
        try:
            # Validate audio format
            if not audio_bytes or len(audio_bytes) < 100:
                return "[Audio too short]", 0.0

            if len(audio_bytes) % 2 != 0:  # PCM16 = 2 bytes per sample
                return "[Invalid audio format]", 0.0

            # Convert bytes to numpy float array
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe
            result = self.model.transcribe(
                audio_array,
                language="en",
                fp16=False  # Use CPU-friendly settings
            )

            text = result.get("text", "").strip()
            # Whisper doesn't return per-word confidence, use average
            confidence = 0.90

            if not text:
                text = "[No speech detected]"
                confidence = 0.0

            print(f"[ASR] {entry_id[:8]}...: '{text[:60]}...' (conf={confidence})")
            return text, confidence

        except Exception as e:
            print(f"[ASR ERROR] {entry_id}: {e}")
            return "[ASR failed]", 0.0


class WorkerQueue:
    """Thread pool for concurrent ASR jobs."""

    def __init__(self, num_workers: int = 2, callback=None):
        """
        Initialize worker thread pool.
        callback: Function called when ASR completes (entry_id, text, confidence, session_id)
        """
        self.queue = Queue()
        self.num_workers = num_workers
        self.callback = callback
        self.running = True
        self.workers = []

        # Start worker threads
        for i in range(num_workers):
            t = Thread(
                target=self._worker_loop,
                daemon=True,
                name=f"ASRWorker-{i}"
            )
            t.start()
            self.workers.append(t)

        print(f"[QUEUE] Started {num_workers} ASR workers")

    def enqueue(self, entry):
        """Add entry to processing queue."""
        self.queue.put(entry)

    def _worker_loop(self):
        """Worker thread main loop."""
        asr = ASRWorker(model_size="small")

        while self.running:
            try:
                entry = self.queue.get(timeout=1)

                if entry is None:  # Poison pill
                    break

                # Process audio
                text, confidence = asr.process_chunk(entry.audio_bytes, entry.entry_id)

                # Callback
                if self.callback:
                    self.callback(entry.entry_id, text, confidence, entry.session_id)

                self.queue.task_done()

            except:
                # Timeout or other error, continue
                pass

    def stop(self):
        """Stop all workers gracefully."""
        self.running = False
        for _ in range(self.num_workers):
            self.queue.put(None)
        for t in self.workers:
            t.join(timeout=5)
        print(f"[QUEUE] All workers stopped")

    def queue_size(self) -> int:
        """Get pending job count."""
        return self.queue.qsize()

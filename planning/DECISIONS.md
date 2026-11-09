# DECISIONS.md

Add every decision and every spec change here: date, change, reason. Entries below were recorded at handoff (2026-11-09).

## Decided

| Topic | Decision | Reason |
|---|---|---|
| Scope | Up to 4 speaking devices, 15-minute session, one session, one backend | Hackathon demo |
| Emotion layer | Out of scope | Team has not agreed on it |
| Latency | Ceiling 5 s measured from chunk close. Typical about 2 s. Sync holds each entry 1.0 s | Worst case with sequential ASR plus about 25% margin. Estimate, to be measured |
| Timestamps | Intervals (start_ts, end_ts), not points | Overlap needs a start and an end |
| Late lines | Shown at the bottom with an "earlier" tag and stored in true order. No cutoff | A missed sentence is worse than an out-of-order one for a deaf user |
| Overlap slack | 0.15 s, tune later | Clock error is small relative to turn gaps |
| Clock offset | 5 samples, keep the lowest round trip, discard above 0.5 s, repeat every 60 s. No separate clock tests | Simple version is enough for the demo. Accepted error about 50 to 100 ms |
| Wrong speaker label | No display cost, no "uncertain" tag | Team decision |
| Input quality | On-device flag (ok or low_quality) set while capturing | Tells the user when the capture is poor |
| Audio on the wire | PCM16, 16 kHz, mono, base64 in JSON, uncompressed | Simplest. About 1.4 Mbps with four devices speaking (estimate) |
| Reconnect | Device reconnects itself, chunk_seq restarts at 0, offline audio is dropped, history is sent after welcome | Simple and keeps the screen from going blank |
| Storage | SQLite at session end plus a live jsonl safety copy | The transcript must survive after the session |
| Security | None in v1 (local WiFi only) | Hackathon scope |

## Open (the user decides)

1. Device client type: browser, native app or Python.
2. Shared speaker: a separate device or the deaf user's own device.
3. TTS engine.
4. Base64 or binary WebSocket frames.
5. Whether to buffer audio while a device is offline.
6. ASR language (default English).

## Measurements pending

1. ASR benchmark on the RTX 4050 (1, 2 and 4 jobs at once). Sets ASR_WORKERS and checks the 5 s ceiling.
2. Real clock error between two test phones (optional for the demo).
3. Calibrate HIGH_THRESHOLD (0.75), LOW_THRESHOLD (0.55), LOUDNESS_GATE, MIN_SPEECH_RMS and ENROLL_MIN_SIMILARITY on real recordings.

## Mismatches found at handoff (resolve before coding the affected parts)

1. `SessionCoordinator.send` and `tick` are plain functions but `hub.broadcast` is a coroutine. Use an adapter queue.
2. The duplicate rule (device_id, connection_epoch, chunk_seq) must apply only to entries with source "asr", since typed entries have no chunk_seq.
3. Add `released_entries()` to SessionCoordinator for the history message.
4. `entry_id` is created where the Entry is created (uuid4 hex).
5. `send_audio` takes raw bytes under `audio_bytes`. DeviceLink base64-encodes and adds chunk_seq and audio_format.
6. The old data_model.docx is outdated. Use the Entry in the Cross-Module Contract.
7. Additions to the Network doc: messages `end_session` and `session_ended`, error code `tts_failed`.
8. The Server doc and final design.pdf were not reviewed. Compare them with the contract before coding.

## Change log

(Add new entries below.)

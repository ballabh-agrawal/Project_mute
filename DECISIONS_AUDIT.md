# DECISIONS AUDIT - What's Locked In vs. Open

**Date**: 2026-11-10  
**Status**: Pre-coding audit before implementation  
**Purpose**: Catch all ambiguities BEFORE code is written

---

## 🔒 FULLY DECIDED (Lock In Code)

These are **non-negotiable** and the code WILL implement exactly as specified:

### Audio & Timing

| Item | Decision | Code Impact | Changeable? |
|------|----------|------------|------------|
| **Sample Rate** | 16 kHz (16000 Hz) | Hardcoded in constants.py | ❌ No (Whisper requires this) |
| **Audio Format** | PCM16 (16-bit signed) | `np.int16` in audio-capture.js | ❌ No (Whisper requires this) |
| **Channels** | Mono (1 channel) | `channels=1` in all audio setup | ❌ No (Whisper requires this) |
| **Chunk Duration** | 400ms (0.4 seconds) | `CHUNK_DURATION = 0.4` in constants.py | ⚠️ Tunable, but fixed at start |
| **Chunk Size in Samples** | 6400 samples (16000 * 0.4) | Calculated, not hardcoded | ⚠️ Auto-derived from duration |
| **Timestamp Type** | Unix floats (seconds.milliseconds) | `time.time()` in Python, `performance.now()` in JS | ✅ Could switch to milliseconds |
| **Timestamp Precision** | To nearest millisecond (3 decimals) | Floating point, no explicit rounding | ✅ Could round to 2 decimals |
| **Overlap Slack** | 150ms (0.15 seconds) | `OVERLAP_SLACK = 0.15` in constants.py | ⚠️ Tunable post-demo |
| **Latency Ceiling** | 5 seconds max | `LATENCY_CEILING = 5.0` in constants.py | ⚠️ Tunable post-demo |

### Data Model (Entry)

| Field | Decision | Code Impact | Changeable? |
|-------|----------|------------|------------|
| **entry_id** | UUID4 hex (32 chars) | `uuid.uuid4().hex` | ❌ No (unique key) |
| **session_id** | UUID4 hex (8 chars prefix as `sess_ABC123`) | Derived from UUID | ✅ Could use different prefix |
| **source** | Enum: "asr", "audio", "metadata", "tts" | String field in Entry dataclass | ✅ Could add more types |
| **device_id** | String (e.g., "device_a", "speaker_1") | User input or auto-generated | ✅ Format changeable |
| **start_ts** | Float (server time in seconds) | `time.time()` | ⚠️ Or milliseconds |
| **end_ts** | Float (server time in seconds) | `time.time()` | ⚠️ Or milliseconds |
| **speaker** | String (device_id or user name) | `entry.speaker = device_id` default | ✅ Fully customizable |
| **speaker_confidence** | Float (0.0 - 1.0) | From Whisper output | ❌ No (ASR model provides this) |
| **text** | String (transcribed text) | From Whisper model | ❌ No (ASR model provides this) |
| **audio_bytes** | Binary PCM16 data (optional) | Stored in SQLite BLOB | ✅ Could store base64 instead |
| **quality** | Enum: "ok", "low_quality" | String flag set during capture | ✅ Could add more levels |
| **is_final** | Boolean | True when ASR completes | ❌ No (business logic) |
| **is_late** | Boolean | True if arrived after 5s ceiling | ❌ No (business logic) |
| **connection_epoch** | Integer (0, 1, 2...) | Counter per device reconnect | ❌ No (deduplication key) |
| **chunk_seq** | Integer (0, 1, 2... per chunk stream) | Sequential counter | ❌ No (deduplication key) |
| **created_at** | ISO datetime string | `datetime.now().isoformat()` | ✅ Format changeable |

### WebSocket Protocol

| Message | Fields | Decision | Code Impact | Changeable? |
|---------|--------|----------|------------|------------|
| **welcome** (client→server) | device_id, device_name, connection_epoch | Required on connect | Hardcoded in socket-client.js | ❌ Required field names |
| **welcome** (server→client) | session_id, server_time, history | Required response | Hardcoded in app.py | ❌ Required field names |
| **chunk** | device_id, session_id, connection_epoch, chunk_seq, audio_bytes, start_ts, end_ts, quality | Required format | Hardcoded in audio-capture.js + app.py | ❌ Required field names |
| **ack** | chunk_seq | Minimal response | Simple emit | ❌ Required field name |
| **caption** | entry_id, text, speaker, start_ts, end_ts, is_final, is_late, confidence | Display format | Hardcoded in ui.js | ❌ Required field names |
| **text_message** | source, text, timestamp | Status messages | Hardcoded in network.py | ✅ Could add more fields |
| **session_ended** | session_id, total_duration, transcript_saved | Session close | Hardcoded in app.py | ❌ Required field names |
| **error** | code, message, device_id | Error format | Hardcoded in network.py | ✅ Could add more error codes |

### Database Schema (SQLite)

| Table | Columns | Decision | Code Impact | Changeable? |
|-------|---------|----------|------------|------------|
| **sessions** | session_id (PK), created_at, ended_at, devices (JSON), total_duration_sec, status | Fixed schema | Hardcoded in storage.py | ❌ No (breaks existing DBs) |
| **entries** | 16 columns (see schema below) | Fixed schema | Hardcoded in storage.py | ❌ No (breaks existing DBs) |
| **UNIQUE constraint** | (session_id, device_id, connection_epoch, chunk_seq) | Deduplication rule | Hardcoded in storage.py | ❌ No (deduplication logic) |

### Server Configuration

| Config | Value | Code Impact | Changeable? |
|--------|-------|------------|------------|
| **Host** | 0.0.0.0 (all interfaces) | `socketio.run(app, host="0.0.0.0")` | ✅ Easy to change |
| **Port** | 5000 | `port=5000` | ✅ Easy to change |
| **ASR Engine** | Local Whisper Small | `model="small"` in asr_worker.py | ✅ Could switch to Base/Medium |
| **ASR Workers** | 2 concurrent jobs | `num_workers=2` in WorkerQueue | ✅ Tunable |
| **Session Timeout** | 15 minutes | `SESSION_TIMEOUT = 15 * 60` | ✅ Tunable |
| **Max Devices** | 4 per session | `MAX_DEVICES = 4` | ✅ Tunable |

### Frontend UI

| Component | Decision | Code Impact | Changeable? |
|-----------|----------|------------|------------|
| **Monitor Dashboard** | Shows captions in real-time, speaker labels, time | Hardcoded in index.html + ui.js | ✅ Layout/colors customizable |
| **Device Recorder** | Input fields, Start/Stop buttons, local captions | Hardcoded in recorder.html + audio-capture.js | ✅ Customizable |
| **Caption Display** | Text, speaker name, timestamp, "earlier" tag for late | Hardcoded in ui.js | ✅ Format customizable |
| **Late Entry Tag** | Text "earlier" in orange badge | Hardcoded in style.css + ui.js | ✅ Text/color changeable |
| **Colors** | Purple theme (#667eea, #764ba2) | Hardcoded in style.css | ✅ Easy to change |

### ASR (Whisper Model)

| Item | Decision | Code Impact | Changeable? |
|------|----------|------------|------------|
| **Model Size** | Small (1.4 GB) | `whisper.load_model("small")` | ✅ Could use Base/Medium/Large |
| **Language** | English only | `language="en"` in transcribe call | ✅ Could add multilingual |
| **Inference Engine** | Local (not API) | `import whisper` (not `openai.Audio.transcribe`) | ✅ Could switch to API |

---

## ⚠️ PARTIALLY DECIDED (Clarify Before Coding)

These were mentioned but need **explicit confirmation** before I write code:

### Timestamp Questions

**QUESTION 1: Unix Seconds vs. Milliseconds?**

```python
# Option A: Current plan (seconds as float)
start_ts = 12.345  # seconds, 3 decimal places
end_ts = 12.745

# Option B: Milliseconds (integer)
start_ts = 12345  # milliseconds
end_ts = 12745

# Option C: Milliseconds (float)
start_ts = 12345.678  # milliseconds with sub-ms precision
end_ts = 12745.123
```

**Why it matters**:
- Affects JSON serialization size
- Affects database storage (float vs integer)
- Affects UI display logic (how to format time)
- Affects synchronization precision

**My recommendation**: **Unix seconds as float (current plan)** because:
- Smaller JSON payload
- Works with Python's `time.time()` natively
- Display logic simpler (just format as HH:MM:SS)
- Precise enough for 400ms chunks (3 decimals = 1ms precision)

---

**QUESTION 2: Speaker Identification Method?**

```python
# Option A: Current plan (device_id as speaker)
speaker = "device_a"
speaker = "device_b"

# Option B: User-provided names
speaker = "Alice"
speaker = "Bob"

# Option C: Speaker index
speaker = "Speaker 1"
speaker = "Speaker 2"

# Option D: Hybrid (let user choose)
speaker = user_input if user_input else f"Speaker {device_number}"
```

**Why it matters**:
- UI display shows this value
- Stored in database
- Affects sorting/filtering logic

**My recommendation**: **Hybrid (user input optional)**
- Device name input field in recorder.html (defaults to "Speaker A")
- If user enters name, use that
- Otherwise fall back to device_id
- Simple, flexible, professional

---

**QUESTION 3: Pre-recorded File Format?**

```
# What format should speaker_a.wav be?
Option A: WAV (PCM16, 16kHz, mono)    ← Current plan
Option B: MP3 (smaller file size)
Option C: Flac (lossless compression)
Option D: Auto-detect format
```

**Why it matters**:
- Browser Web Audio API can decode some formats natively
- PCM WAV is easiest (no decoding needed)
- MP3 requires decoding library

**My recommendation**: **WAV (PCM16, 16kHz, mono)** because:
- Web Audio API decodes it directly
- No extra library needed
- Zero quality loss
- File size not critical for hackathon demo

---

### Deduplication Questions

**QUESTION 4: Deduplication Key - Is This Right?**

Currently: `(device_id, connection_epoch, chunk_seq)` must be unique

```python
# Example: Device A disconnects and reconnects
# Connection 1 (epoch=0)
chunk_seq=0  # OK
chunk_seq=1  # OK
chunk_seq=2  # OK (then device drops)

# Connection 2 (epoch=1) after reconnect
chunk_seq=0  # OK (new sequence, epoch incremented)
chunk_seq=1  # OK
```

**Is this correct?** YES, this handles:
- ✅ Duplicate chunks from retransmits
- ✅ Out-of-order chunk arrival
- ✅ Device reconnects with new audio stream

**Confirmed?** YES/NO

---

**QUESTION 5: What Counts as "Late"?**

Currently: Entry is late if `(now - start_ts) > LATENCY_CEILING (5.0 sec)`

```python
# Example timeline
t=0s:     User starts speaking (start_ts=0)
t=2.5s:   ASR finishes (entry released)    → is_late = False (2.5 < 5.0)
t=3.2s:   ASR finishes (another entry)     → is_late = False (3.2 < 5.0)
t=5.5s:   ASR finishes (slow query)        → is_late = True  (5.5 > 5.0)
t=8.0s:   ASR finishes (network lag)       → is_late = True  (8.0 > 5.0)

# UI displays late entries at BOTTOM with "earlier" tag
```

**Is this correct?** Confirm this is how you want "late" defined.

**Confirmed?** YES/NO

---

### Display Questions

**QUESTION 6: Caption Sorting Order in UI?**

```
Option A: Chronological (by start_ts)
  Speaker A: "Hello" (t=0-0.4s)
  Speaker B: "Hi there" (t=0.2-0.8s)    ← Overlaps with A
  Speaker A: "How are you?" (t=0.9-1.3s)

Option B: Speaker turn-based (A, then B, then A)
  Speaker A: "Hello" (t=0-0.4s)
  Speaker A: "How are you?" (t=0.9-1.3s)
  Speaker B: "Hi there" (t=0.2-0.8s)    ← Shown separately at bottom

Option C: Arrival order (when caption is received)
  Speaker A: "Hello" (received t=2.1s)
  Speaker B: "Hi there" (received t=2.3s)
  Speaker A: "How are you?" (received t=3.5s)
```

**My recommendation**: **Chronological (Option A)** because:
- Deaf user reads conversation flow naturally
- Overlaps make sense temporally
- Matches transcript order

**Confirmed?** YES/NO

---

**QUESTION 7: Should Late Entries Appear In Different Location?**

```
Option A: Same location, marked with "earlier" tag
  Speaker A: "Hello" (t=0-0.4s)
  Speaker B: "Hi there" (t=0.2-0.8s)
  Speaker A: "How are you?" (t=0.9-1.3s) [earlier]  ← Arrived late

Option B: Bottom section labeled "Earlier Captions"
  [Main Timeline]
  Speaker A: "Hello" (t=0-0.4s)
  Speaker B: "Hi there" (t=0.2-0.8s)
  
  [Earlier Captions]
  Speaker A: "How are you?" (t=0.9-1.3s) [arrived late]

Option C: Separate tab/panel for late entries
  [Current] [Earlier] ← Click to switch
  Speaker A: "Hello"
  Speaker B: "Hi there"
  
  (Click "Earlier" tab)
  Speaker A: "How are you?" [arrived late]
```

**My recommendation**: **Option A (inline with "earlier" tag)** because:
- Simpler UI (single list)
- User sees full conversation flow
- Tag provides visual indicator
- Matches the design spec in your docs

**Confirmed?** YES/NO

---

## 🟢 TECHNICALLY OPEN (But Won't Affect MVP Code)

These are decisions for **AFTER** the hackathon:

- **Multiple sessions**: Currently handles 1 session. Could extend.
- **Speaker diarization**: Currently uses device_id as speaker. Could use voice recognition.
- **Audio compression**: Currently uncompressed PCM16. Could add opus/aac.
- **Encryption**: Currently none. Could add TLS/end-to-end encryption.
- **TTS reply**: Currently skipped. Could add audio synthesis back.
- **Mobile apps**: Currently browser-only. Could build native iOS/Android.

---

## 📋 CHECKLIST: What I Need From You Before Writing Code

Answer these **7 questions** to lock in all ambiguities:

```
[ ] 1. Timestamps: Unix seconds (float) or milliseconds? 
        Your choice: _______

[ ] 2. Speaker ID: device_id ("device_a") or user name ("Alice") or hybrid?
        Your choice: _______

[ ] 3. Pre-recorded files: WAV (PCM16, 16kHz, mono) format confirmed?
        Your choice: YES / NO

[ ] 4. Deduplication key (device_id, epoch, chunk_seq) is correct?
        Your choice: YES / NO

[ ] 5. "Late" definition: (now - start_ts) > 5.0 seconds is correct?
        Your choice: YES / NO

[ ] 6. Caption order: Chronological by start_ts (mixed speakers OK)?
        Your choice: YES / NO

[ ] 7. Late entries: Display inline with "earlier" tag (same list)?
        Your choice: YES / NO
```

---

## SUMMARY: What This Means for Code

**After you answer these 7 questions:**

I will write code that:
- ✅ Hard-codes ALL your answers into constants.py
- ✅ Implements logic exactly as you specify
- ✅ Makes it easy to change (config file, not scattered in code)
- ✅ Passes all tests
- ✅ Runs identically on macOS and Windows

**If you change your mind AFTER code is written:**
- ✅ Easy changes (timing format, speaker display): 5 minutes
- ⚠️ Medium changes (dedup logic, late detection): 30 minutes
- ❌ Hard changes (WebSocket protocol, database schema): 2-3 hours (requires rewrite)

**So answer these 7 questions NOW to save time later.** 🎯

---

**END OF DECISIONS AUDIT**

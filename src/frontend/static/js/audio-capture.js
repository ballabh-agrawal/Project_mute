/**
 * Audio capture from microphone or file.
 */

const SAMPLE_RATE = 16000;
const CHUNK_DURATION = 0.4;
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

        this.socketClient.onCaption = (data) => this.captionDisplay.addCaption(data);
        this.socketClient.onWelcome = (data) => this.onWelcome(data);
        this.socketClient.onConnected = () => this.onConnected();
        this.socketClient.onSessionEnded = (data) => this.onSessionEnded(data);
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
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        // Note: Using native sample rate, Whisper will resample if needed

        const source = this.audioContext.createMediaStreamSource(this.mediaStream);
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
            const s = Math.max(-1, Math.min(1, floatArray[i]));
            int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return int16Array.buffer;
    }

    sendChunk(audioBytes, startTs, endTs, quality) {
        this.socketClient.sendChunk(audioBytes, startTs, endTs, quality);
    }

    async playRecordedFile(file) {
        const arrayBuffer = await file.arrayBuffer();
        const audioData = await this.audioContext.decodeAudioData(arrayBuffer);

        const rawData = audioData.getChannelData(0);

        this.recording = true;
        this.startTime = performance.now();

        let offset = 0;
        while (offset < rawData.length && this.recording) {
            const end = Math.min(offset + CHUNK_SAMPLES, rawData.length);
            const chunk = rawData.slice(offset, end);

            const int16Array = this.floatTo16BitPCM(chunk);
            const currentTime = (offset / SAMPLE_RATE);

            this.sendChunk(int16Array, currentTime - CHUNK_DURATION, currentTime, "ok");

            this.chunkCount++;
            document.getElementById("chunkCount").innerText = this.chunkCount;

            offset += CHUNK_SAMPLES;

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

    onConnected() {
        document.getElementById("status").innerText = "🟡 Connected, waiting...";
    }

    onWelcome(data) {
        console.log("[AUDIO] Session established:", data.session_id);
        document.getElementById("sessionId").innerText = data.session_id;
    }

    onSessionEnded(data) {
        document.getElementById("status").innerText = "✓ Session ended";
    }
}

let audioCapture = null;

function startCapture() {
    if (!audioCapture) {
        audioCapture = new AudioCapture();
    }

    const source = document.getElementById("audioSource").value;
    const deviceName = document.getElementById("deviceName").value;

    audioCapture.socketClient.sendWelcome(deviceName);

    if (source === "microphone") {
        audioCapture.startMicrophone();
    } else {
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

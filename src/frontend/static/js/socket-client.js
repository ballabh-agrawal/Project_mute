/**
 * WebSocket client for Project Mute.
 */

class SocketClient {
    constructor(deviceId = null) {
        this.socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 10,
        });

        this.deviceId = deviceId || `device_${this.randomId()}`;
        this.sessionId = null;
        this.connectionEpoch = 0;
        this.chunkSeq = 0;

        this.setupListeners();
    }

    randomId() {
        return Math.random().toString(36).substr(2, 9);
    }

    setupListeners() {
        this.socket.on("connect", () => {
            console.log("[SOCKET] Connected to server");
            this.onConnected();
        });

        this.socket.on("welcome", (data) => {
            console.log("[SOCKET] Welcome:", data);
            this.sessionId = data.session_id;
            this.onWelcome(data);
        });

        this.socket.on("caption", (data) => {
            console.log("[SOCKET] Caption:", data);
            this.onCaption(data);
        });

        this.socket.on("ack", (data) => {
            // Chunk acknowledged
        });

        this.socket.on("text_message", (data) => {
            console.log("[SOCKET] Message:", data);
            this.onTextMessage(data);
        });

        this.socket.on("session_ended", (data) => {
            console.log("[SOCKET] Session ended:", data);
            this.onSessionEnded(data);
        });

        this.socket.on("error", (data) => {
            console.error("[SOCKET] Error:", data);
            this.onError(data);
        });

        this.socket.on("disconnect", () => {
            console.log("[SOCKET] Disconnected");
            this.onDisconnected();
        });
    }

    sendWelcome(deviceName) {
        this.socket.emit("welcome", {
            device_id: this.deviceId,
            device_name: deviceName,
            connection_epoch: this.connectionEpoch,
            session_id: this.sessionId,
        });
    }

    sendChunk(audioBytes, startTs, endTs, quality = "ok") {
        const b64 = this.bytesToBase64(audioBytes);

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

    sendEndSession() {
        this.socket.emit("end_session", {
            device_id: this.deviceId,
            session_id: this.sessionId,
            reason: "manual",
        });
    }

    reconnect() {
        this.connectionEpoch++;
        this.chunkSeq = 0;
        this.socket.disconnect();
        this.socket.connect();
    }

    bytesToBase64(bytes) {
        return btoa(String.fromCharCode(...new Uint8Array(bytes)));
    }

    // Callbacks (override in app)
    onConnected() {}
    onWelcome(data) {}
    onCaption(data) {}
    onTextMessage(data) {}
    onSessionEnded(data) {}
    onError(data) {}
    onDisconnected() {}
}

/**
 * UI utilities for caption display.
 */

class CaptionDisplay {
    constructor(elementId = "captions") {
        this.element = document.getElementById(elementId);
        this.captions = [];
    }

    addCaption(data) {
        const caption = {
            id: data.entry_id,
            speaker: data.speaker || "Speaker",
            text: data.text,
            isLate: data.is_late || false,
            timestamp: new Date().toLocaleTimeString(),
        };

        this.captions.push(caption);
        this.render();
    }

    render() {
        if (this.captions.length === 0) {
            this.element.innerHTML = '<p class="placeholder">No captions yet...</p>';
            return;
        }

        const html = this.captions.map(c => `
            <div class="caption ${c.isLate ? 'late' : ''}">
                <div class="caption-header">
                    <strong>${this.escapeHtml(c.speaker)}</strong>
                    <span class="time">${c.timestamp}</span>
                    ${c.isLate ? '<span class="tag-late">earlier</span>' : ''}
                </div>
                <div class="caption-text">${this.escapeHtml(c.text)}</div>
            </div>
        `).join("");

        this.element.innerHTML = html;
        this.element.scrollTop = this.element.scrollHeight;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

function displayCaption(data) {
    if (!window.captionDisplay) {
        window.captionDisplay = new CaptionDisplay("captions");
    }
    window.captionDisplay.addCaption(data);
}

function displayMessage(data) {
    if (!window.captionDisplay) {
        window.captionDisplay = new CaptionDisplay("captions");
    }
    window.captionDisplay.addCaption({
        entry_id: "msg_" + Date.now(),
        speaker: data.source.toUpperCase(),
        text: data.text,
        is_late: false,
    });
}

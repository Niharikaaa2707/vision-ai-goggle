// app.js - VISION Dashboard Frontend
// Connects to backend via WebSocket and updates UI panels

const WS_URL = "ws://localhost:8765";
let socket = null;

// Status indicator
const statusIndicator = document.getElementById("status-indicator");

function connectWebSocket() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("[WS] Connected to VISION backend");
        statusIndicator.textContent = "System Online";
        statusIndicator.className = "status online";
    };

    socket.onclose = () => {
        console.log("[WS] Disconnected. Retrying in 3 seconds...");
        statusIndicator.textContent = "System Offline";
        statusIndicator.className = "status offline";
        setTimeout(connectWebSocket, 3000);
    };

    socket.onerror = (err) => {
        console.error("[WS] Error:", err);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleEvent(data);
    };
}

function handleEvent(data) {
    // Will be expanded in future commits
    console.log("[Event]", data);
}

// Start connection on page load
window.onload = () => {
    connectWebSocket();
};
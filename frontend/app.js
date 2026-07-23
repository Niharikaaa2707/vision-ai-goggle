// app.js - VISION Dashboard Frontend

const WS_URL = "ws://localhost:8765";
let socket = null;

const statusIndicator = document.getElementById("status-indicator");
const detectionList = document.getElementById("detection-list");
const transcriptBox = document.getElementById("transcript-box");
const alertBox = document.getElementById("alert-box");

function connectWebSocket() {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        statusIndicator.textContent = "System Online";
        statusIndicator.className = "status online";
    };

    socket.onclose = () => {
        statusIndicator.textContent = "System Offline";
        statusIndicator.className = "status offline";
        setTimeout(connectWebSocket, 3000);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleEvent(data);
    };
}

function handleEvent(data) {
    if (data.type === "detection") {
        updateDetections(data.detections);
    } else if (data.type === "alert") {
        updateAlert(data.level, data.message);
    } else if (data.type === "transcript") {
        transcriptBox.textContent = data.text;
    }
}

function updateDetections(detections) {
    detectionList.innerHTML = "";
    detections.forEach(det => {
        const li = document.createElement("li");
        li.textContent = `${det.class_name} — ${det.direction}, ${det.distance}m`;
        detectionList.appendChild(li);
    });
}

function updateAlert(level, message) {
    alertBox.textContent = message;
    alertBox.className = level.toLowerCase();
}

window.onload = () => {
    connectWebSocket();
};
// app.js - VISION Dashboard Frontend
// Connects to backend via WebSocket and updates UI panels in real time

const WS_URL = "ws://localhost:8765";
let socket = null;

const statusIndicator = document.getElementById("status-indicator");
const detectionList = document.getElementById("detection-list");
const transcriptBox = document.getElementById("transcript-box");
const alertBox = document.getElementById("alert-box");
const batteryStatus = document.getElementById("battery-status");
const cpuStatus = document.getElementById("cpu-status");
const sceneBox = document.getElementById("scene-box");

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

    socket.onerror = (err) => {
        console.error("[WS] Error:", err);
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
    } else if (data.type === "scene") {
        sceneBox.textContent = data.description;
    } else if (data.type === "status") {
        batteryStatus.textContent = "Battery: " + data.battery + "%";
        cpuStatus.textContent = "CPU: " + data.cpu + "%";
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
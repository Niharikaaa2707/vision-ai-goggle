// app.js - VISION Dashboard Frontend
// Added voice transcript live update and command mode display

const WS_URL = "ws://localhost:8765";
let socket = null;
let alertHistory = [];

const statusIndicator = document.getElementById("status-indicator");
const detectionList = document.getElementById("detection-list");
const detectionCount = document.getElementById("detection-count");
const transcriptBox = document.getElementById("transcript-box");
const commandStatus = document.getElementById("command-status");
const alertBox = document.getElementById("alert-box");
const alertHistoryBox = document.getElementById("alert-history");
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
        transcriptBox.textContent = `"${data.text}"`;
    } else if (data.type === "command") {
        commandStatus.textContent = `Mode: ${data.mode}`;
    } else if (data.type === "scene") {
        sceneBox.textContent = data.description;
    } else if (data.type === "status") {
        batteryStatus.textContent = "Battery: " + data.battery + "%";
        cpuStatus.textContent = "CPU: " + data.cpu + "%";
    }
}

function updateDetections(detections) {
    detectionList.innerHTML = "";
    if (detections.length === 0) {
        detectionCount.textContent = "No objects detected";
        return;
    }
    detectionCount.textContent = `${detections.length} object(s) detected`;
    detections.forEach(det => {
        const li = document.createElement("li");
        li.textContent = `${det.class_name} — ${det.direction}, ${det.distance}m`;
        detectionList.appendChild(li);
    });
}

function updateAlert(level, message) {
    alertBox.textContent = message;
    alertBox.className = level.toLowerCase();

    // Add to history
    const time = new Date().toLocaleTimeString();
    alertHistory.unshift(`[${time}] ${message}`);
    if (alertHistory.length > 5) alertHistory.pop();
    alertHistoryBox.textContent = alertHistory.join("\n");
}

window.onload = () => {
    connectWebSocket();
};
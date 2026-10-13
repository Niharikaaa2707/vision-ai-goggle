# VISION — AI-Powered Smart Goggles for the Visually Impaired

VISION is an AI-powered assistive system designed to help visually impaired individuals understand their surroundings through real-time audio feedback. It combines computer vision, speech recognition, and text-to-speech to identify objects, estimate their distance, and describe the environment around the user.

The system runs locally on a laptop without requiring an internet connection, making its core features accessible even in environments with limited connectivity.

## Features

- **Real-Time Object Detection:** Uses YOLOv8s to detect and identify objects in the camera feed.
- **Distance Estimation:** Estimates how far detected objects are from the user.
- **Directional Awareness:** Identifies whether an object is on the left, centre, or right.
- **Voice Commands:** Lets users interact with the system through spoken instructions.
- **Object Search:** Finds specific objects on request, such as a bottle, person, or chair.
- **Scene Description:** Uses Moondream2 to generate natural-language descriptions of the surroundings.
- **Offline Speech Recognition:** Uses faster-whisper to convert spoken commands into text.
- **Audio Feedback:** Uses Piper TTS to communicate object information and alerts through speech.
- **Proximity Alerts:** Provides audio warnings when objects are detected nearby.
- **System Monitoring:** Tracks system information such as battery status and CPU usage.
- **Live Monitoring Dashboard:** Provides a web interface for viewing system activity in real time.
- **Fault Recovery:** Includes camera reconnection handling and crash-recovery mechanisms to improve reliability.

## How It Works

VISION brings together several components to provide audio-based environmental awareness.

1. The camera continuously captures frames from the surroundings.
2. YOLOv8s detects objects in the frames.
3. The distance and direction modules estimate the position of detected objects.
4. The alert system checks proximity conditions and triggers warnings when needed.
5. The user can issue voice commands, which are processed using faster-whisper and matched to supported actions.
6. When a scene description is requested, Moondream2 analyses the image and generates a natural-language response.
7. Piper TTS converts the system's responses into speech so the user can hear the information through earphones.

The system also monitors its operating status and handles camera disconnections and unexpected failures.

## Voice Commands

| Voice command | Action |
|---|---|
| `Find [object]` | Search for a specific object |
| `Describe` | Get a description of the surroundings |
| `Distance` | Ask for the distance to a nearby detected object |
| `What is on my left?` | Get information about objects on the left |
| `What is on my right?` | Get information about objects on the right |
| `Is the path clear?` | Request a basic environmental safety check |
| `Battery` | Check battery status |
| `Help` | List available voice commands |
| `Stop` | Exit the current search or return to normal operation |

## Technology Stack

| Technology | Purpose |
| Python 3.12 | Core application logic |
| Ultralytics YOLOv8s | Real-time object detection |
| faster-whisper | Offline speech recognition |
| Moondream2 | Image understanding and scene description |
| Piper TTS | Offline speech synthesis |
| OpenCV | Camera access and image processing |
| FastAPI | Backend services for the dashboard |
| WebSockets | Real-time communication between the backend and dashboard |
| RapidFuzz | Matching voice-recognized text with supported commands |
| NumPy | Numerical operations and image-related processing |
| psutil | CPU and system-status monitoring |

## Project Structure

```text
vision-ai-goggle/
├── main.py
├── config.py
├── modules/
│   ├── detector.py
│   ├── distance.py
│   ├── direction.py
│   ├── speech_input.py
│   ├── speech_output.py
│   ├── scene_describer.py
│   ├── command_matcher.py
│   ├── system_status.py
│   ├── camera_manager.py
│   ├── alert_system.py
│   └── logger.py
├── models/
├── logs/
├── images/
├── requirements.txt
└── README.md
```

The application is organised into separate modules so that detection, speech processing, distance estimation, alerts, and system monitoring can be maintained and improved independently.

*Note: The structure above reflects the modular architecture; adjust it if your current repository differs.*

## Getting Started

### Prerequisites

- Python 3.12
- A working camera
- A microphone for voice commands
- Earphones or headphones for audio feedback
- Sufficient memory and processing power to run the selected AI models locally

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Niharikaaa2707/vision-ai-goggle.git
cd vision-ai-goggle
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the environment**

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

**4. Install the dependencies**

```bash
pip install -r requirements.txt
```

Some models may require their model weights or voice files to be downloaded and configured before the first run. Ensure these assets are available locally if you intend to use the system without internet connectivity.

**5. Run the application**

```bash
python main.py
```

Follow the application's startup messages to check whether the camera and required models have loaded successfully.

## Project Demo

### Working Screenshot

![VISION live camera feed](images/vision_live%20feed.png)

The screenshot shows the live camera feed during operation.

### Video Demonstration

A video demonstration of VISION is available in this repository, showcasing the system's working pipeline and its real-time capabilities.

https://youtu.be/CMdxbIUNjDg

## Team

- **Prakriti** — AI/ML backend pipeline, model integration, object detection, speech processing, and environmental awareness logic.
- **Niharika** — Frontend dashboard and system integration.

## Challenges and Future Improvements

Building an assistive system that runs offline involves balancing model accuracy, processing speed, memory usage, and response time. Other challenges include handling camera failures, recognising commands correctly in noisy environments, and providing useful alerts without overwhelming the user.

Potential improvements include integrating dedicated depth sensors for more reliable distance measurement, optimising inference for low-power hardware, improving obstacle detection, and expanding voice-command support.

## Important Note

VISION is an assistive prototype intended to provide additional environmental awareness. Distance estimates and object detections may be inaccurate, and the system cannot guarantee that a path is safe. It should not replace a cane, guide dog, or other established mobility aids.

## Acknowledgements

VISION brings together open-source computer vision, speech processing, and language-model technologies to explore how AI can make everyday interactions with the surrounding environment more accessible.



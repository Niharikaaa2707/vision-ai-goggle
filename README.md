\# VISION — AI Smart Goggle for the Visually Impaired



A real-time AI-powered assistive system that helps visually impaired individuals navigate their surroundings using computer vision, speech recognition, and text-to-speech — running fully offline on a laptop.



\## Features

\- Real-time object detection with YOLOv8s (up to 25 FPS)

\- Distance and direction estimation (left/centre/right)

\- Offline speech recognition using faster-whisper

\- Natural language scene description using moondream2

\- Text-to-speech narration using Piper TTS

\- Voice-commanded object search ("Find bottle")

\- Proximity alerts with audio feedback

\- Battery and CPU monitoring

\- Web dashboard for real-time monitoring

\- Crash recovery and camera reconnect handling



\## Team

\- Prakriti — AI/ML Backend Pipeline

\- Niharika — Frontend Dashboard \& System Integration



\## Tech Stack

\- Python 3.12

\- YOLOv8s (Ultralytics)

\- faster-whisper (OpenAI Whisper)

\- Piper TTS (Coqui)

\- moondream2 (Vision Language Model)

\- OpenCV

\- FastAPI + WebSockets



\## Setup



```bash

\# Clone the repo

git clone https://github.com/Niharikaaa2707/vision-ai-goggle.git

cd vision-ai-goggle



\# Create virtual environment

python -m venv venv

venv\\Scripts\\activate  # Windows



\# Install dependencies

pip install -r requirements.txt



\# Run

python main.py

```



\## Voice Commands

| Command | Action |

|---|---|

| "Find \[object]" | Search for specific object |

| "Describe" | Full scene description |

| "Distance" | Distance to nearest object |

| "What is on my left/right" | Directional awareness |

| "Is the path clear" | Safety check |

| "Stop" | Return to normal mode |

| "Battery" | Battery status |

| "Help" | List all commands |


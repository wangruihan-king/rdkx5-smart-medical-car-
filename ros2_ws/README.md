OriginCar Smart Medical Competition Solution

Project Structure

ros2_ws/
├── src/
│   ├── qr_detector/          # QR code recognition package
│   ├── human_detector/       # Human detection and LLM interface
│   ├── navigation/           # Navigation and obstacle avoidance package
│   ├── voice_output/         # Voice output package
│   └── task_manager/         # Task manager main node
├── install_dependencies.sh   # Dependency installation script
└── README.md                 # Project description

Functional Modules

QR Code Recognition (qr_detector)
Uses the pyzbar library for QR code decoding
Publishes task information to the /qr_detector/task_info topic

Human Detection and LLM Interface (human_detector)
Uses YOLOv8 for human detection
Supports both local LLMs and cloud-based LLMs (e.g., GPT-4o)
Sends detected human images to the LLM for image-to-text generation
Publishes recognition results to the /llm_interface/image_caption topic

Navigation and Obstacle Avoidance (navigation)
LiDAR-based obstacle avoidance
Path planning (supports clockwise/counter-clockwise)
Motion control

Voice Output (voice_output)
Supports task information broadcasting
Supports human recognition result broadcasting
Supports task status broadcasting

Task Manager (task_manager)
Coordinates the entire competition task workflow
Task state management
Time management

Launch Commands

Launch the Complete Competition System
ros2 launch task_manager competition.launch.py

Launch Individual Packages
ros2 launch qr_detector qr_detector.launch.py
ros2 launch human_detector human_detector.launch.py
ros2 launch navigation navigation.launch.py
ros2 launch voice_output voice_output.launch.py
ros2 launch task_manager task_manager.launch.py

Parameter Configuration

Navigation Parameters (navigation/config/navigation_params.yaml)
safety_distance: Safety distance (default: 0.5m)
max_speed: Maximum speed (default: 0.5m/s)
target_position_tolerance: Target position tolerance (default: 0.3m)

LLM Parameters
local_llm_enabled: Whether to enable the local LLM
local_llm_url: Local LLM endpoint URL
api_key: Cloud LLM API key

Competition Task Workflow

Sub-task 1: The vehicle starts from the starting point (P) and proceeds to the task release point to scan a QR code to obtain the task.
Sub-task 2: According to the task requirements (clockwise/counter-clockwise), drive along the yellow lane, detect human standees, and perform image-to-text generation.
Sub-task 3: Return to the starting point (P) to complete the task.

Dependency Installation

bash install_dependencies.sh

Hardware Requirements

OriginCar series intelligent robot kit
RDK X3/X5/S100 main controller board
Single-line TOF LiDAR (VP100L / Lunqu N10)
Depth camera (OJ Aurora 930)
Monocular camera
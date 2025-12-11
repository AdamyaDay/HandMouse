# Hand Gesture Mouse

This project implements a virtual mouse controlled entirely by hand gestures using a webcam.  
It uses MediaPipe for hand landmark detection, OpenCV for video processing, and PyAutoGUI for mouse control.  
The system supports smooth cursor movement, clicking, scrolling, and drag-and-drop using intuitive finger gestures.

## Features:
- Smooth and stable cursor movement using fingertip tracking
- Left-click: Thumb + Index finger pinch
- Right-click: Thumb + Middle finger pinch
- Scroll mode: Index + Middle finger touching + move vertically
- Drag and drop: Thumb + Ring finger pinch
- Toggle mouse control with the "E" key
- Real-time on-screen status indicators
- Movement smoothing (dead-zone, adaptive smoothing, jump limiting)

## Installation:
Install the required Python libraries:
```
pip install opencv-python mediapipe pyautogui numpy
```
Make sure your webcam is connected and accessible.

## Usage:
Run the program using:

python hand_mouse.py

## Gesture Controls:
```
Move Cursor  -> Move your index finger
Left Click   -> Touch index finger to thumb
Right Click  -> Touch middle finger to thumb
Scroll       -> Touch index + middle finger, then move up/down
Drag & Drop  -> Touch ring finger to thumb
Toggle Mouse -> Press E
Quit Program -> Press Q
```
## How It Works:
The program performs real-time hand tracking using MediaPipe Hands.
The index fingertip position is mapped to screen coordinates using interpolation.

## Smoothing:
- Dead-zone filtering eliminates jitter
- Adaptive smoothing adjusts sensitivity
- Jump limiting prevents sudden cursor jumps

Gestures are detected by measuring distances between specific finger landmarks.

## Project Structure:
```
handmousepython/
    hand_mouse.py     Main application file
    README.md         Documentation
```
## Known Limitations:
- The OpenCV preview window may freeze if dragged (Windows limitation)
- Requires good lighting for accurate detection
- Webcam FPS affects smoothness

## Future Improvements:
- Add GUI interface
- Gesture-based double click
- Drag-lock feature
- Real-time FPS counter
- Standalone Windows executable
- Gesture customization options

## Author:
Adamya Srivastava
B.Tech Electronics and Communication Engineering
Hand Gesture Interaction Project

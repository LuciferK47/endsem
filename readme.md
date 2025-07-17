# Waypoint Navigator Robot

A Python-based autonomous navigation system for the PiCar-X robot that enables waypoint-to-waypoint navigation with obstacle avoidance capabilities.

## Overview

This project implements a state-machine-based navigation system that allows a PiCar-X robot to autonomously navigate to user-specified coordinates while avoiding obstacles in its path. The robot uses ultrasonic sensors for obstacle detection and dead reckoning for position tracking.

## Features

- **Autonomous Waypoint Navigation**: Navigate to any X,Y coordinate within the robot's operating range
- **Obstacle Avoidance**: Automatically detect and navigate around obstacles using ultrasonic sensors
- **State Machine Architecture**: Clean, maintainable code structure using enum-based states
- **Dead Reckoning Odometry**: Track robot position and heading using movement calculations
- **Real-time Feedback**: Console output showing navigation progress and status

## System Architecture

### State Machine Design

The robot operates using four distinct states:

1. **IDLE**: Initial state, waiting for navigation commands
2. **NAVIGATING**: Actively moving toward the target waypoint
3. **AVOIDING_OBSTACLE**: Executing obstacle avoidance maneuvers
4. **GOAL_REACHED**: Successfully arrived at the target location

### Navigation Algorithm

The navigation system uses a simple but effective approach:

1. **Heading Calculation**: Compute the required heading angle to reach the goal
2. **Turn-to-Heading**: Rotate the robot to face the target direction
3. **Forward Movement**: Move straight toward the goal in discrete steps
4. **Obstacle Detection**: Continuously monitor for obstacles using ultrasonic sensor
5. **Avoidance Maneuver**: Execute a 4-step avoidance sequence when obstacles are detected

## Key Components

### WaypointNavigator Class

The main class that handles all navigation logic:

- **Position Tracking**: Maintains current X, Y coordinates and heading angle
- **Goal Management**: Stores target coordinates and calculates navigation vectors
- **State Management**: Handles transitions between different operational states
- **Sensor Integration**: Processes ultrasonic sensor data for obstacle detection

### Obstacle Avoidance System

A sophisticated 4-step avoidance sequence:

1. **Backup**: Reverse away from the obstacle
2. **Turn Right**: Rotate to avoid the obstacle
3. **Bypass**: Move forward to clear the obstacle
4. **Re-align**: Turn back toward the original heading

## Configuration Parameters

The system includes several tunable parameters for different environments:

```python
METERS_PER_SEC_AT_FORWARD_SPEED = 0.25  # Robot speed calibration
FORWARD_SPEED = 30                       # Motor speed for forward movement
TURN_SPEED = 25                         # Motor speed for turning
GOAL_TOLERANCE_M = 0.1                  # Distance tolerance for goal arrival
HEADING_TOLERANCE_DEG = 5.0             # Angular tolerance for heading
OBSTACLE_THRESHOLD_CM = 25.0            # Obstacle detection distance
AVOID_BACKUP_DURATION_S = 1.0           # Backup duration during avoidance
AVOID_TURN_ANGLE_DEG = 35.0             # Turn angle for obstacle avoidance
AVOID_BYPASS_DURATION_S = 1.5           # Forward duration during bypass
```

## Usage

### Basic Navigation

```python
# Create navigator instance
navigator = WaypointNavigator()

# Navigate to specific coordinates
navigator.navigate_to_point(2.0, 1.5)  # Navigate to (2.0m, 1.5m)
```

### Interactive Mode

Run the main script for interactive coordinate input:

```bash
python waypoint_navigator.py
```

The program will prompt for target coordinates:
```
Enter the target X coordinate (in meters): 2.0
Enter the target Y coordinate (in meters): 1.5
```

## Technical Implementation

### Odometry System

The robot tracks its position using dead reckoning:

- **Position Update**: `x += distance * cos(heading)`, `y += distance * sin(heading)`
- **Heading Update**: Updated based on steering angle and movement duration
- **Calibration**: Speed and turning coefficients calibrated for PiCar-X hardware

### Sensor Integration

- **Ultrasonic Sensor**: Provides distance measurements for obstacle detection
- **Servo Motor**: Controls steering angle for directional movement
- **DC Motors**: Provide forward/backward propulsion

### Error Handling

The system includes robust error handling for:
- Invalid coordinate input
- Keyboard interrupts (Ctrl+C)
- Sensor reading failures
- Motor control exceptions

## Dependencies

- **picarx**: PiCar-X hardware control library
- **math**: Mathematical calculations for navigation
- **time**: Sleep functions for timing control
- **enum**: State machine implementation

## Installation and Setup

1. Ensure PiCar-X hardware is properly assembled and calibrated
2. Install required dependencies
3. Place the script on the robot's Raspberry Pi
4. Run with appropriate permissions for GPIO access

## Performance Characteristics

- **Navigation Accuracy**: Typically within 10cm of target coordinates
- **Obstacle Detection Range**: 25cm threshold with ultrasonic sensor
- **Movement Speed**: 0.25 m/s forward speed
- **Turn Rate**: Approximately 1.5 degrees per steering unit per second

## Future Enhancements

Potential improvements for the navigation system:

- **Sensor Fusion**: Integrate IMU for improved heading accuracy
- **Path Planning**: Implement A* or other path planning algorithms
- **SLAM**: Add simultaneous localization and mapping capabilities
- **Multi-waypoint**: Support for sequential waypoint navigation
- **Visual Navigation**: Camera-based obstacle detection and navigation

## Troubleshooting

### Common Issues

1. **Robot doesn't reach exact coordinates**: Adjust `GOAL_TOLERANCE_M` parameter
2. **Frequent obstacle detection**: Lower `OBSTACLE_THRESHOLD_CM` value
3. **Inaccurate turning**: Calibrate turning coefficients in `_turn_to_heading()`
4. **Drift during navigation**: Recalibrate `METERS_PER_SEC_AT_FORWARD_SPEED`

### Debug Information

The system provides detailed console output including:
- Current position and heading
- Distance to goal
- Obstacle detection status
- State transitions
- Avoidance maneuver progress




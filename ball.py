import time
from gpiozero import Servo

# --- Servo Configuration ---
servo_pins = {
    "Base": 17,
    "Shoulder": 18,
    "Elbow": 22,
    "WristPitch": 23,
    "WristRoll": 24,
    "Gripper": 25
}

# --- Servo Initialization ---
servos = {}
print("Initializing servos...")
for name, pin in servo_pins.items():
    try:
        servos[name] = Servo(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
        print(f"  > Successfully initialized '{name}' servo on GPIO {pin}")
    except Exception as e:
        print(f"  > ERROR: Could not initialize '{name}' servo on GPIO {pin}. Details: {e}")
        servos[name] = None
print("All servos initialized.")


class RobotArm:
    """A class to control the robotic arm."""

    def _init_(self):
        self.current_angles = {name: 0 for name in servo_pins.keys()}

    def set_angle(self, servo_name, angle):
        if servo_name not in servos or servos[servo_name] is None:
            print(f"Warning: Servo '{servo_name}' is not available.")
            return

        angle = max(0, min(180, angle))
        servo_value = (angle / 90.0) - 1.0  # Map 0–180° to -1 to +1
        servos[servo_name].value = servo_value
        self.current_angles[servo_name] = angle
        print(f"Moved '{servo_name}' to {angle}° (value = {servo_value:.2f})")

    def move_to_position(self, position_angles, delay=1.0):
        print(f"\nMoving to new position...")
        for name, angle in position_angles.items():
            self.set_angle(name, angle)
            time.sleep(0.1)
        print("Move complete.")
        time.sleep(delay)

    def home_position(self):
        """
        Moves to the physical default position as seen in your image.
        These values are estimates — tune as needed.
        """
        print("\nMoving to DEFAULT IMAGE POSITION (Home)...")
        home_angles = {
            "Base": 60,         # Slightly turned inward
            "Shoulder": 120,    # Raised up
            "Elbow": 60,        # Bent toward middle
            "WristPitch": 90,   # Flat forward
            "WristRoll": 90,    # Neutral
            "Gripper": 10       # Slightly closed
        }
        self.move_to_position(home_angles, delay=1.5)

    def slumped_position(self):
        """
        Moves to a relaxed or parked position.
        """
        print("\nMoving to SLUMPED RESTING position...")
        slumped_angles = {
            "Base": 90,
            "Shoulder": 45,
            "Elbow": 45,
            "WristPitch": 90,
            "WristRoll": 90,
            "Gripper": 90
        }
        self.move_to_position(slumped_angles, delay=1.5)

    def demonstration_sequence(self):
        """
        A short routine that moves and returns to default image pose.
        """
        print("\n--- Starting demonstration sequence ---")

        self.set_angle("Base", 45)
        time.sleep(0.5)
        self.set_angle("Base", 135)
        time.sleep(0.5)
        self.set_angle("Base", 90)
        time.sleep(1)

        self.set_angle("Shoulder", 70)
        self.set_angle("Elbow", 110)
        time.sleep(0.7)
        self.set_angle("Shoulder", 110)
        self.set_angle("Elbow", 70)
        time.sleep(0.7)

        self.home_position()

        self.set_angle("Gripper", 180)  # Open gripper
        time.sleep(1)
        self.set_angle("Gripper", 10)   # Close gripper
        time.sleep(1)

        print("--- Demonstration complete ---")

    def release_servos(self):
        print("\nReleasing all servos...")
        for name, servo in servos.items():
            if servo is not None:
                servo.detach()
                print(f"  > '{name}' servo released.")


# --- Main Program Execution ---
if _name_ == "_main_":
    my_arm = RobotArm()

    try:
        my_arm.home_position()
        my_arm.demonstration_sequence()
        my_arm.slumped_position()
        input("\nMovement finished. Press Enter to exit and release servos.\n")

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        my_arm.release_servos()
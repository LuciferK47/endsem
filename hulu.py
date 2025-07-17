from picarx import Picarx
import math
from time import sleep
from enum import Enum, auto

class RobotState(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    AVOIDING_OBSTACLE = auto()
    GOAL_REACHED = auto()

class WaypointNavigator:
    METERS_PER_SEC_AT_FORWARD_SPEED = 0.25
    FORWARD_SPEED = 30
    TURN_SPEED = 25
    GOAL_TOLERANCE_M = 0.1
    HEADING_TOLERANCE_DEG = 5.0
    OBSTACLE_THRESHOLD_CM = 25.0
    AVOID_BACKUP_DURATION_S = 1.0
    AVOID_TURN_ANGLE_DEG = 35.0
    AVOID_BYPASS_DURATION_S = 1.5

    def __init__(self):
        self.px = Picarx()
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_heading_deg = 0.0
        self.goal_x = 0.0
        self.goal_y = 0.0
        self.state = RobotState.IDLE
        self.avoidance_step = 0

    def navigate_to_point(self, goal_x, goal_y):
        print(f"--- Starting Navigation to Goal: ({goal_x:.2f}, {goal_y:.2f}) ---")
        self.goal_x = goal_x
        self.goal_y = goal_y
        self.state = RobotState.NAVIGATING

        while self.state != RobotState.GOAL_REACHED and self.state != RobotState.IDLE:
            distance_cm = self.px.ultrasonic.read()
            self._update_state_handler(distance_cm)
            self._execute_state_action()
            sleep(0.05)

        print("--- Navigation Complete ---")
        self.px.stop()

    def _update_state_handler(self, distance_cm):
        if self.state == RobotState.NAVIGATING:
            if self._is_goal_reached():
                self.state = RobotState.GOAL_REACHED
                print("State Change: -> GOAL_REACHED")
            elif 0 < distance_cm < self.OBSTACLE_THRESHOLD_CM:
                self.state = RobotState.AVOIDING_OBSTACLE
                self.avoidance_step = 0
                print(f"State Change: Obstacle at {distance_cm:.1f} cm -> AVOIDING_OBSTACLE")

        elif self.state == RobotState.AVOIDING_OBSTACLE:
            pass

    def _execute_state_action(self):
        if self.state == RobotState.NAVIGATING:
            self._handle_navigation()
        elif self.state == RobotState.AVOIDING_OBSTACLE:
            self._handle_avoidance()
        elif self.state == RobotState.GOAL_REACHED:
            self.px.stop()

    def _handle_navigation(self):
        target_heading_deg = self._calculate_heading_to_goal()
        heading_error = (target_heading_deg - self.current_heading_deg + 180) % 360 - 180

        if abs(heading_error) > self.HEADING_TOLERANCE_DEG:
            self._turn_to_heading(target_heading_deg)
        else:
            self._move_forward_step()

    def _handle_avoidance(self):
        if self.avoidance_step == 0:
            print("Avoidance (1/4): Backing up...")
            self.px.set_dir_servo_angle(0)
            self.px.backward(self.FORWARD_SPEED)
            sleep(self.AVOID_BACKUP_DURATION_S)
            self.px.stop()
            self.avoidance_step += 1

        elif self.avoidance_step == 1:
            print(f"Avoidance (2/4): Turning right {self.AVOID_TURN_ANGLE_DEG}°...")
            target_heading = (self.current_heading_deg - self.AVOID_TURN_ANGLE_DEG) % 360
            self._turn_to_heading(target_heading, is_avoidance_turn=True)
            self.avoidance_step += 1

        elif self.avoidance_step == 2:
            print("Avoidance (3/4): Moving forward to bypass...")
            self.px.set_dir_servo_angle(0)
            self.px.forward(self.FORWARD_SPEED)
            sleep(self.AVOID_BYPASS_DURATION_S)
            self.px.stop()
            distance = self.METERS_PER_SEC_AT_FORWARD_SPEED * self.AVOID_BYPASS_DURATION_S
            self._update_odometry(distance_moved=distance)
            self.avoidance_step += 1

        elif self.avoidance_step == 3:
            print(f"Avoidance (4/4): Turning left {self.AVOID_TURN_ANGLE_DEG}° to re-align...")
            target_heading = (self.current_heading_deg + self.AVOID_TURN_ANGLE_DEG) % 360
            self._turn_to_heading(target_heading, is_avoidance_turn=True)
            self.avoidance_step += 1

        elif self.avoidance_step == 4:
            print("Avoidance complete. Resuming navigation.")
            self.state = RobotState.NAVIGATING

    def _turn_to_heading(self, target_heading_deg, is_avoidance_turn=False):
        target_heading_deg = target_heading_deg % 360
        heading_error = (target_heading_deg - self.current_heading_deg + 180) % 360 - 180

        while abs(heading_error) > self.HEADING_TOLERANCE_DEG:
            steer_angle = max(-35, min(35, heading_error * 2.0))

            self.px.set_dir_servo_angle(steer_angle)
            self.px.forward(self.TURN_SPEED)
            
            turn_duration = 0.1
            sleep(turn_duration)
            
            degrees_turned = -steer_angle * turn_duration * 1.5
            self._update_odometry(angle_turned_degrees=degrees_turned)
            
            heading_error = (target_heading_deg - self.current_heading_deg + 180) % 360 - 180
            print(f"  Turning... Target: {target_heading_deg:.1f}°, Current: {self.current_heading_deg:.1f}°, Steer: {steer_angle:.1f}°")

        self.px.stop()
        self.px.set_dir_servo_angle(0)
        print(f"Turn complete. Final heading: {self.current_heading_deg:.1f}°")

        if is_avoidance_turn:
            self.avoidance_step += 1

    def _move_forward_step(self):
        print("Moving forward...")
        move_duration_s = 0.5
        self.px.set_dir_servo_angle(0)
        self.px.forward(self.FORWARD_SPEED)
        sleep(move_duration_s)
        self.px.stop()

        distance_moved = self.METERS_PER_SEC_AT_FORWARD_SPEED * move_duration_s
        self._update_odometry(distance_moved=distance_moved)

    def _update_odometry(self, distance_moved=0.0, angle_turned_degrees=0.0):
        self.current_heading_deg = (self.current_heading_deg + angle_turned_degrees) % 360

        if distance_moved > 0:
            angle_rad = math.radians(self.current_heading_deg)
            self.current_x += distance_moved * math.cos(angle_rad)
            self.current_y += distance_moved * math.sin(angle_rad)

        print(f"  Odometry Updated: Pos=({self.current_x:.2f}, {self.current_y:.2f}), Head={self.current_heading_deg:.1f}°")

    def _calculate_heading_to_goal(self):
        dx = self.goal_x - self.current_x
        dy = self.goal_y - self.current_y
        return math.degrees(math.atan2(dy, dx)) % 360

    def _is_goal_reached(self):
        distance_to_goal = math.sqrt((self.current_x - self.goal_x)**2 + (self.current_y - self.goal_y)**2)
        print(f"Distance to goal: {distance_to_goal:.2f} m")
        return distance_to_goal < self.GOAL_TOLERANCE_M

def main():
    navigator = WaypointNavigator()
    try:
        goal_x = float(input("Enter the target X coordinate (in meters): "))
        goal_y = float(input("Enter the target Y coordinate (in meters): "))
        navigator.navigate_to_point(goal_x, goal_y)

    except (ValueError, TypeError):
        print("Invalid input. Please enter numeric values for coordinates.")
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        navigator.px.stop()

if __name__ == '__main__':
    main()
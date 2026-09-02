"""Module 7 solution: a small behaviour built from the pieces of modules 2-6.

Drive forward; when the laser controller reports `blocked`, disable it, rotate away from the
obstacle via the RotateToAngle action, re-enable and continue. Keeps the decision logic in a
plain function (`choose_turn`) so it can be unit-tested without ROS.

Run:  ros2 launch turtlebot_py_controller wander.launch.py use_rviz:=false
"""
import math
from enum import Enum, auto

import rclpy
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool
from turtlebot_interfaces.action import RotateToAngle
from turtlebot_interfaces.msg import ObstacleInfo


class State(Enum):
    DRIVING = auto()
    TURNING = auto()


def choose_turn(obstacle_angle: float, base_turn: float = math.radians(90)) -> float:
    """Turn away from the obstacle: obstacle on the left (angle > 0) -> turn right (negative)."""
    return -base_turn if obstacle_angle > 0 else base_turn


class Wander(Node):

    def __init__(self):
        super().__init__('wander')
        self.declare_parameter('turn_angle_deg', 90.0)
        self.declare_parameter('angular_speed', 0.8)
        self.state = State.DRIVING

        self.info_sub = self.create_subscription(ObstacleInfo, 'obstacle_info', self.on_obstacle, 10)
        self.enable_cli = self.create_client(SetBool, 'enable_motion')
        self.rotate_cli = ActionClient(self, RotateToAngle, 'rotate_to_angle')

        self.enable_cli.wait_for_service()
        self.rotate_cli.wait_for_server()
        self.get_logger().info('wander ready')

    def on_obstacle(self, info: ObstacleInfo):
        if self.state != State.DRIVING or not info.blocked:
            return
        self.state = State.TURNING
        turn = choose_turn(info.angle, math.radians(self.get_parameter('turn_angle_deg').value))
        self.get_logger().info(f'blocked at {math.degrees(info.angle):.0f} deg -> turning {math.degrees(turn):.0f} deg')

        # 1) stop the laser controller (async! we are inside a callback)
        fut = self.enable_cli.call_async(SetBool.Request(data=False))
        fut.add_done_callback(lambda _: self.start_turn(turn))

    def start_turn(self, turn: float):
        goal = RotateToAngle.Goal(angle=turn, angular_speed=self.get_parameter('angular_speed').value)
        self.rotate_cli.send_goal_async(goal).add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('rotation rejected, resuming')
            self.resume()
            return
        handle.get_result_async().add_done_callback(lambda _: self.resume())

    def resume(self):
        fut = self.enable_cli.call_async(SetBool.Request(data=True))

        def back_to_driving(_):
            self.state = State.DRIVING
            self.get_logger().info('driving again')
        fut.add_done_callback(back_to_driving)


def main(args=None):
    rclpy.init(args=args)
    node = Wander()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

"""Module 5 solution: action client. Sends one rotation goal, prints feedback, exits with the result.

Run:  ros2 run turtlebot_py_controller rotate_action_client 90        (degrees)
"""
import math
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlebot_interfaces.action import RotateToAngle


class RotateActionClient(Node):

    def __init__(self):
        super().__init__('rotate_action_client')
        self._client = ActionClient(self, RotateToAngle, 'rotate_to_angle')

    def send_goal(self, angle_deg: float, speed: float = 0.6):
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('rotate_to_angle server not available')
            rclpy.shutdown()
            return
        goal = RotateToAngle.Goal(angle=math.radians(angle_deg), angular_speed=speed)
        self._client.send_goal_async(goal, feedback_callback=self.on_feedback) \
            .add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Goal rejected')
            rclpy.shutdown()
            return
        self.get_logger().info('Goal accepted')
        handle.get_result_async().add_done_callback(self.on_result)

    def on_feedback(self, msg):
        self.get_logger().info(f'remaining: {math.degrees(msg.feedback.remaining):6.1f} deg',
                               throttle_duration_sec=0.5)

    def on_result(self, future):
        result = future.result().result
        self.get_logger().info(f'final yaw: {math.degrees(result.final_yaw):.1f} deg')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    angle = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0
    node = RotateActionClient()
    node.send_goal(angle)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()

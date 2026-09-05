"""Module 5 solution: action server that rotates the robot by a relative angle using odometry.

Run:  ros2 run turtlebot_py_controller rotate_action_server
Try:  ros2 action list -t
      ros2 action send_goal /rotate_to_angle turtlebot_interfaces/action/RotateToAngle \
          "{angle: 1.57, angular_speed: 0.5}" --feedback
      (Ctrl+C while it runs -> cancel)
Note: stop the laser_controller first (or disable it via /enable_motion), otherwise both
      nodes publish to /cmd_vel and fight each other.
"""
import math
import time

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from turtlebot_interfaces.action import RotateToAngle

MAX_ANGULAR_SPEED = 2.0   # rad/s (burger limit is 2.84)
TOLERANCE = 0.02          # rad


def yaw_from_quaternion(q) -> float:
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


def wrap(angle: float) -> float:
    """Wrap to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


class RotateActionServer(Node):

    def __init__(self):
        super().__init__('rotate_action_server')
        self.yaw = None
        cb_group = ReentrantCallbackGroup()
        # Odometry must keep arriving while `execute` runs -> same reentrant group + multithreaded executor
        self.odom_sub = self.create_subscription(Odometry, 'odom', self.on_odom, 10, callback_group=cb_group)
        self.cmd_pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self._server = ActionServer(
            self, RotateToAngle, 'rotate_to_angle',
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=self.on_cancel,
            callback_group=cb_group)
        self.get_logger().info('rotate_action_server ready')

    def on_odom(self, msg: Odometry):
        self.yaw = yaw_from_quaternion(msg.pose.pose.orientation)

    def on_goal(self, goal: RotateToAngle.Goal) -> GoalResponse:
        if self.yaw is None:
            self.get_logger().warn('No odometry yet, rejecting goal')
            return GoalResponse.REJECT
        if goal.angular_speed <= 0.0:
            return GoalResponse.REJECT
        if abs(goal.angle) > math.pi:
            # `remaining` in execute() is a wrapped error, so it cannot tell "20 deg to go" from
            # "340 deg the other way": a bigger goal looks overshot on the first iteration and would
            # succeed without moving. Reject it rather than lie in the result.
            self.get_logger().warn(f'|angle| must be <= pi, got {goal.angle:.2f} rad, rejecting goal')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def on_cancel(self, goal_handle) -> CancelResponse:
        return CancelResponse.ACCEPT

    def publish_twist(self, wz: float):
        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.angular.z = wz
        self.cmd_pub.publish(cmd)

    def execute(self, goal_handle):
        goal: RotateToAngle.Goal = goal_handle.request
        speed = min(goal.angular_speed, MAX_ANGULAR_SPEED)
        direction = 1.0 if goal.angle >= 0 else -1.0
        target_yaw = wrap(self.yaw + goal.angle)
        self.get_logger().info(f'Rotating {math.degrees(goal.angle):.0f} deg at {speed:.2f} rad/s')

        feedback = RotateToAngle.Feedback()
        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.publish_twist(0.0)
                goal_handle.canceled()
                self.get_logger().info('Rotation canceled')
                return RotateToAngle.Result(final_yaw=self.yaw)

            remaining = wrap(target_yaw - self.yaw)
            # Once we overshoot, remaining changes sign relative to the direction of travel
            if abs(remaining) < TOLERANCE or remaining * direction < 0:
                break

            # Slow down near the target to reduce overshoot
            wz = direction * max(0.1, min(speed, abs(remaining) * 2.0))
            self.publish_twist(wz)

            feedback.remaining = remaining
            goal_handle.publish_feedback(feedback)
            time.sleep(0.05)   # 20 Hz control loop

        self.publish_twist(0.0)
        goal_handle.succeed()
        result = RotateToAngle.Result(final_yaw=self.yaw)
        self.get_logger().info(f'Done, final yaw {math.degrees(self.yaw):.1f} deg')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = RotateActionServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

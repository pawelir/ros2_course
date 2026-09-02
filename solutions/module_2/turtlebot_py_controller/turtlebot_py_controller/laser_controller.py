"""Module 2 solution: subscribe to /scan, publish /cmd_vel, stop in front of obstacles.

Run:  ros2 run turtlebot_py_controller laser_controller
"""
import math

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

FORWARD_SPEED = 0.15   # m/s
STOP_DISTANCE = 0.5    # m


def min_valid_range(scan: LaserScan) -> float:
    """Smallest finite range inside the sensor's valid interval, or inf if none."""
    valid = [r for r in scan.ranges
             if math.isfinite(r) and scan.range_min <= r <= scan.range_max]
    return min(valid) if valid else math.inf


class LaserController(Node):

    def __init__(self):
        super().__init__('laser_controller')
        self.scan_sub = self.create_subscription(LaserScan, 'scan', self.on_scan, 10)
        self.cmd_pub = self.create_publisher(TwistStamped, 'cmd_vel', 10)
        self.get_logger().info('laser_controller started')

    def on_scan(self, msg: LaserScan):
        closest = min_valid_range(msg)
        blocked = closest < STOP_DISTANCE

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.linear.x = 0.0 if blocked else FORWARD_SPEED
        self.cmd_pub.publish(cmd)

        # throttle_duration_sec avoids flooding the terminal at scan rate
        self.get_logger().info(
            f'closest obstacle: {closest:.2f} m -> {"STOP" if blocked else "go"}',
            throttle_duration_sec=1.0)


def main(args=None):
    rclpy.init(args=args)
    node = LaserController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

"""Module 3 solution: parameters (declared, from YAML, validated, changeable at runtime).

Run:  ros2 launch turtlebot_py_controller laser_controller.launch.py
Try:  ros2 param list /laser_controller
      ros2 param set /laser_controller stop_distance 1.0
      ros2 param set /laser_controller forward_speed 5.0     -> rejected
"""
import math

import rclpy
from geometry_msgs.msg import TwistStamped
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


def min_valid_range(scan: LaserScan) -> float:
    valid = [r for r in scan.ranges
             if math.isfinite(r) and scan.range_min <= r <= scan.range_max]
    return min(valid) if valid else math.inf


class LaserController(Node):

    def __init__(self):
        super().__init__('laser_controller')

        self.declare_parameter('forward_speed', 0.15,
                               ParameterDescriptor(description='Cruise speed [m/s], 0 < v <= 0.22'))
        self.declare_parameter('stop_distance', 0.5,
                               ParameterDescriptor(description='Stop if an obstacle is closer [m]'))
        self.declare_parameter('scan_topic', 'scan')
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')

        # Cache values that are read in every callback; refresh them in the callback below.
        self.forward_speed = self.get_parameter('forward_speed').value
        self.stop_distance = self.get_parameter('stop_distance').value
        self.add_on_set_parameters_callback(self.on_params_changed)

        # Topic names are only read at startup; changing them later has no effect.
        scan_topic = self.get_parameter('scan_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.scan_sub = self.create_subscription(LaserScan, scan_topic, self.on_scan, 10)
        self.cmd_pub = self.create_publisher(TwistStamped, cmd_vel_topic, 10)

        self.get_logger().info(
            f'laser_controller started: speed={self.forward_speed} stop={self.stop_distance} '
            f'scan="{scan_topic}" cmd_vel="{cmd_vel_topic}"')

    def on_params_changed(self, params) -> SetParametersResult:
        for p in params:
            if p.name == 'forward_speed':
                if not 0.0 < p.value <= 0.22:      # TurtleBot3 burger max linear speed
                    return SetParametersResult(successful=False,
                                               reason='forward_speed must be in (0, 0.22]')
                self.forward_speed = p.value
            elif p.name == 'stop_distance':
                if p.value <= 0.0:
                    return SetParametersResult(successful=False, reason='stop_distance must be > 0')
                self.stop_distance = p.value
        return SetParametersResult(successful=True)

    def on_scan(self, msg: LaserScan):
        closest = min_valid_range(msg)
        blocked = closest < self.stop_distance

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.linear.x = 0.0 if blocked else self.forward_speed
        self.cmd_pub.publish(cmd)

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

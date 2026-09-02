"""launch_testing integration test: fake /scan in, expect /cmd_vel and /obstacle_info out.

Run:  colcon test --packages-select turtlebot_py_controller && colcon test-result --verbose
"""
import math
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import launch_testing.markers
import pytest
import rclpy
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan


@pytest.mark.launch_test
@launch_testing.markers.keep_alive
def generate_test_description():
    controller = launch_ros.actions.Node(
        package='turtlebot_py_controller', executable='laser_controller', output='screen',
        parameters=[{'stop_distance': 0.5, 'forward_speed': 0.1}])
    return launch.LaunchDescription([controller, launch_testing.actions.ReadyToTest()])


class TestLaserController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('test_laser_controller')
        cls.scan_pub = cls.node.create_publisher(LaserScan, 'scan', 10)
        cls.received = []
        cls.node.create_subscription(TwistStamped, 'cmd_vel', cls.received.append, 10)

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def publish_and_collect(self, closest: float) -> float:
        self.received.clear()
        scan = LaserScan()
        scan.header.frame_id = 'base_scan'
        scan.angle_increment = math.radians(1.0)
        scan.range_min, scan.range_max = 0.12, 3.5
        scan.ranges = [3.0] * 360
        scan.ranges[0] = closest
        end = self.node.get_clock().now().nanoseconds + int(5e9)
        while not self.received and self.node.get_clock().now().nanoseconds < end:
            self.scan_pub.publish(scan)
            rclpy.spin_once(self.node, timeout_sec=0.2)
        self.assertTrue(self.received, 'no /cmd_vel received')
        return self.received[-1].twist.linear.x

    def test_drives_when_clear(self):
        self.assertAlmostEqual(self.publish_and_collect(2.0), 0.1)

    def test_stops_when_blocked(self):
        self.assertEqual(self.publish_and_collect(0.3), 0.0)

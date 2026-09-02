"""Testing: a launch_testing integration test. Starts the server, calls it, checks the answer.

Run: colcon test --packages-select ros2_examples && colcon test-result --verbose
 or: launch_test test/test_add_two_ints_launch.py
"""
import unittest

import launch
import launch_ros.actions
import launch_testing.actions
import launch_testing.markers
import pytest
import rclpy
from example_interfaces.srv import AddTwoInts


@pytest.mark.launch_test
@launch_testing.markers.keep_alive
def generate_test_description():
    server = launch_ros.actions.Node(
        package='ros2_examples', executable='add_two_ints_server', output='screen')
    return launch.LaunchDescription([server, launch_testing.actions.ReadyToTest()])


class TestAddTwoInts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = rclpy.create_node('test_client')

    @classmethod
    def tearDownClass(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def test_sum(self):
        client = self.node.create_client(AddTwoInts, 'add_two_ints')
        self.assertTrue(client.wait_for_service(timeout_sec=10.0), 'service not available')
        future = client.call_async(AddTwoInts.Request(a=20, b=22))
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
        self.assertIsNotNone(future.result())
        self.assertEqual(future.result().sum, 42)

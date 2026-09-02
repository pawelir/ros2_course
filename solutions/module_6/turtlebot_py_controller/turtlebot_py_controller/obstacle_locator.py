"""Module 6 solution: TF2 lookup + callback groups.

Takes /obstacle_info (distance + bearing in base_scan), transforms the point into the odom
frame with tf2 and publishes it as geometry_msgs/PointStamped on /obstacle_point, so RViz
can show where the obstacle is in the world even while the robot turns.

Run:  ros2 run turtlebot_py_controller obstacle_locator
Try:  ros2 topic echo /obstacle_point
      ros2 run tf2_tools view_frames
      rviz2: add PointStamped display on /obstacle_point (Fixed Frame: odom)

The `slow_diagnostics` timer simulates an expensive callback (e.g. writing a report).
Without callback groups + MultiThreadedExecutor it would freeze the obstacle updates for 2 s
every 10 s. Comment out the `callback_group=` arguments and `executor` to see the problem.
"""
import math
import time

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from tf2_geometry_msgs import do_transform_point   # noqa: F401  registers PointStamped with tf2
from tf2_ros import Buffer, TransformException, TransformListener
from turtlebot_interfaces.msg import ObstacleInfo


class ObstacleLocator(Node):

    def __init__(self):
        super().__init__('obstacle_locator')
        self.declare_parameter('target_frame', 'odom')
        self.target_frame = self.get_parameter('target_frame').value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        fast = MutuallyExclusiveCallbackGroup()
        slow = MutuallyExclusiveCallbackGroup()
        self.info_sub = self.create_subscription(ObstacleInfo, 'obstacle_info', self.on_obstacle, 10,
                                                 callback_group=fast)
        self.point_pub = self.create_publisher(PointStamped, 'obstacle_point', 10)
        self.create_timer(10.0, self.slow_diagnostics, callback_group=slow)

        self.count = 0
        self.get_logger().info(f'obstacle_locator: publishing obstacle in "{self.target_frame}"')

    def on_obstacle(self, info: ObstacleInfo):
        if not math.isfinite(info.distance):
            return
        # Point in the scan frame
        p = PointStamped()
        p.header = info.header
        p.point.x = info.distance * math.cos(info.angle)
        p.point.y = info.distance * math.sin(info.angle)

        try:
            # Ask tf2 to transform into target_frame at the message's timestamp,
            # waiting up to 100 ms for the transform to become available.
            p_out = self.tf_buffer.transform(p, self.target_frame, timeout=Duration(seconds=0.1))
        except TransformException as ex:
            self.get_logger().warn(f'TF {info.header.frame_id} -> {self.target_frame} failed: {ex}',
                                   throttle_duration_sec=2.0)
            return

        self.point_pub.publish(p_out)
        self.count += 1
        self.get_logger().info(
            f'obstacle in {self.target_frame}: x={p_out.point.x:.2f} y={p_out.point.y:.2f}',
            throttle_duration_sec=1.0)

    def slow_diagnostics(self):
        self.get_logger().info('diagnostics: crunching numbers for 2 s ...')
        time.sleep(2.0)
        self.get_logger().info(f'diagnostics: {self.count} points published so far')


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleLocator()
    executor = MultiThreadedExecutor(num_threads=2)
    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

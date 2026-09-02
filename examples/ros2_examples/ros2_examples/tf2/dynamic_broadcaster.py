"""TF2: publish a moving transform odom -> base_link (robot driving in a circle).

Run:   ros2 run ros2_examples dynamic_broadcaster
Check: ros2 run tf2_ros tf2_echo odom base_link
       ros2 run tf2_tools view_frames      -> frames.pdf
       rviz2 (Fixed Frame: odom, add TF display)
"""
import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class DynamicBroadcaster(Node):

    def __init__(self):
        super().__init__('dynamic_broadcaster')
        self.broadcaster = TransformBroadcaster(self)
        self.t0 = self.get_clock().now()
        self.create_timer(0.05, self.tick)     # 20 Hz

    def tick(self):
        now = self.get_clock().now()
        elapsed = (now - self.t0).nanoseconds * 1e-9
        radius, omega = 1.0, 0.5               # m, rad/s
        yaw = omega * elapsed

        t = TransformStamped()
        t.header.stamp = now.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = radius * math.cos(yaw)
        t.transform.translation.y = radius * math.sin(yaw)
        t.transform.rotation.z = math.sin((yaw + math.pi / 2) / 2)
        t.transform.rotation.w = math.cos((yaw + math.pi / 2) / 2)
        self.broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicBroadcaster()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

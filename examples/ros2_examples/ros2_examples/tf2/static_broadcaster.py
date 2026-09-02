"""TF2: publish a fixed transform base_link -> laser once (latched on /tf_static).

Run:   ros2 run ros2_examples static_broadcaster
Check: ros2 topic echo /tf_static
       ros2 run tf2_ros tf2_echo base_link laser
Same thing from the CLI, no code needed:
       ros2 run tf2_ros static_transform_publisher --x 0.1 --z 0.2 --frame-id base_link --child-frame-id laser
"""
import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster


def quaternion_from_yaw(yaw: float):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))  # x, y, z, w


class StaticBroadcaster(Node):

    def __init__(self):
        super().__init__('static_broadcaster')
        self.broadcaster = StaticTransformBroadcaster(self)

        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'          # parent
        t.child_frame_id = 'laser'               # child
        t.transform.translation.x = 0.1
        t.transform.translation.z = 0.2
        qx, qy, qz, qw = quaternion_from_yaw(math.radians(90))
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.broadcaster.sendTransform(t)        # sent once, latched for late subscribers
        self.get_logger().info('Published static transform base_link -> laser')


def main(args=None):
    rclpy.init(args=args)
    node = StaticBroadcaster()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

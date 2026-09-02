"""TF2: look up odom -> laser at 1 Hz. Needs both broadcasters running.

Run (three terminals):
    ros2 run ros2_examples static_broadcaster
    ros2 run ros2_examples dynamic_broadcaster
    ros2 run ros2_examples frame_listener
The chain odom -> base_link -> laser is resolved by tf2 automatically.
"""
import math

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from tf2_ros import Buffer, TransformException, TransformListener


class FrameListener(Node):

    def __init__(self):
        super().__init__('frame_listener')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)   # fills the buffer from /tf, /tf_static
        self.create_timer(1.0, self.tick)

    def tick(self):
        try:
            # (target frame, source frame, time). Time 0 = "latest available".
            t = self.tf_buffer.lookup_transform('odom', 'laser', rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().warn(f'Could not transform odom -> laser: {ex}')
            return
        p = t.transform.translation
        q = t.transform.rotation
        yaw = math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y ** 2 + q.z ** 2)))
        self.get_logger().info(f'laser in odom: x={p.x:.2f} y={p.y:.2f} z={p.z:.2f} yaw={yaw:.0f} deg')


def main(args=None):
    rclpy.init(args=args)
    node = FrameListener()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

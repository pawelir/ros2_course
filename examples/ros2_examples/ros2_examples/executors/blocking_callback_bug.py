"""Executors: THE BUG. A slow service callback starves a fast timer.

Run:   ros2 run ros2_examples blocking_callback_bug
Then:  ros2 service call /slow_add example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
Watch: the 'heartbeat' log stops for 3 s while the service works.

Why: the default SingleThreadedExecutor runs one callback at a time, so anything
that blocks (time.sleep, a long computation, a blocking service call) stalls
every other callback of the node. See multithreaded_fix.py for the fix.
"""
import time

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class BlockingNode(Node):

    def __init__(self):
        super().__init__('blocking_node')
        self.create_timer(0.5, self.heartbeat)
        self.create_service(AddTwoInts, 'slow_add', self.slow_add)

    def heartbeat(self):
        self.get_logger().info('heartbeat')

    def slow_add(self, request, response):
        self.get_logger().info('slow_add: working for 3 s ...')
        time.sleep(3.0)                       # blocks the whole executor
        response.sum = request.a + request.b
        return response


def main(args=None):
    rclpy.init(args=args)
    node = BlockingNode()
    try:
        rclpy.spin(node)                      # SingleThreadedExecutor by default
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

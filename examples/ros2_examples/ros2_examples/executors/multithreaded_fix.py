"""Executors: THE FIX. MultiThreadedExecutor + callback groups.

Run:   ros2 run ros2_examples multithreaded_fix
Then:  ros2 service call /slow_add example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
Watch: 'heartbeat' keeps ticking while slow_add sleeps.

Rules of thumb:
- MutuallyExclusiveCallbackGroup: callbacks in the group never run concurrently
  (safe to share state between them without locks). Default group for a node.
- ReentrantCallbackGroup: callbacks may run in parallel, even with themselves.
- Put the slow stuff in its own group so it cannot block the rest.
"""
import time

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node


class NonBlockingNode(Node):

    def __init__(self):
        super().__init__('non_blocking_node')
        self.fast_group = MutuallyExclusiveCallbackGroup()
        self.slow_group = MutuallyExclusiveCallbackGroup()

        self.create_timer(0.5, self.heartbeat, callback_group=self.fast_group)
        self.create_service(AddTwoInts, 'slow_add', self.slow_add, callback_group=self.slow_group)

    def heartbeat(self):
        self.get_logger().info('heartbeat')

    def slow_add(self, request, response):
        self.get_logger().info('slow_add: working for 3 s ...')
        time.sleep(3.0)
        response.sum = request.a + request.b
        return response


def main(args=None):
    rclpy.init(args=args)
    node = NonBlockingNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

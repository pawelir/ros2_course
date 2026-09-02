"""Services: a one-shot client. Shows the async call + spin_until_future_complete pattern.

Run: ros2 run ros2_examples add_two_ints_server
     ros2 run ros2_examples add_two_ints_client 4 5
"""
import sys

import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class AddTwoIntsClient(Node):

    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for /add_two_ints ...')

    def send_request(self, a: int, b: int) -> int:
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        # call_async returns a Future. Never use the blocking `call()` from inside a callback:
        # it would deadlock a single-threaded executor.
        future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result().sum


def main(args=None):
    rclpy.init(args=args)
    a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) >= 3 else (1, 2)
    node = AddTwoIntsClient()
    try:
        result = node.send_request(a, b)
        node.get_logger().info(f'Result: {a} + {b} = {result}')
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

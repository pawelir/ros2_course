"""Actions: client that sends a goal, prints feedback and the result, then exits.

Run: ros2 run ros2_examples fibonacci_server
     ros2 run ros2_examples fibonacci_client 10
"""
import sys

import rclpy
from example_interfaces.action import Fibonacci
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class FibonacciClient(Node):

    def __init__(self):
        super().__init__('fibonacci_client')
        self._client = ActionClient(self, Fibonacci, 'fibonacci')

    def send_goal(self, order: int):
        self._client.wait_for_server()
        goal = Fibonacci.Goal()
        goal.order = order
        # Step 1: send the goal, wait until the server accepts/rejects it
        send_future = self._client.send_goal_async(goal, feedback_callback=self.on_feedback)
        send_future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            rclpy.shutdown()
            return
        self.get_logger().info('Goal accepted')
        # Step 2: wait for the result
        goal_handle.get_result_async().add_done_callback(self.on_result)

    def on_feedback(self, feedback_msg):
        self.get_logger().info(f'Feedback: {list(feedback_msg.feedback.sequence)}')

    def on_result(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: {list(result.sequence)}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    order = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    node = FibonacciClient()
    node.send_goal(order)
    try:
        rclpy.spin(node)  # returns once on_result calls rclpy.shutdown()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()

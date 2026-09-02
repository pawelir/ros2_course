"""Actions: server for example_interfaces/action/Fibonacci with feedback and cancel.

Run:   ros2 run ros2_examples fibonacci_server
Check: ros2 action list -t
       ros2 interface show example_interfaces/action/Fibonacci
       ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 8}" --feedback
"""
import time

import rclpy
from example_interfaces.action import Fibonacci
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node


class FibonacciServer(Node):

    def __init__(self):
        super().__init__('fibonacci_server')
        self._server = ActionServer(
            self, Fibonacci, 'fibonacci',
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=self.on_cancel,
            # Reentrant group + multithreaded executor so cancel requests are
            # processed while `execute` is still running.
            callback_group=ReentrantCallbackGroup(),
        )

    def on_goal(self, goal_request) -> GoalResponse:
        if goal_request.order < 0 or goal_request.order > 50:
            self.get_logger().warn(f'Rejecting order {goal_request.order}')
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def on_cancel(self, goal_handle) -> CancelResponse:
        self.get_logger().info('Cancel requested')
        return CancelResponse.ACCEPT

    def execute(self, goal_handle):
        self.get_logger().info(f'Executing goal, order={goal_handle.request.order}')
        feedback = Fibonacci.Feedback()
        feedback.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result(sequence=feedback.sequence)

            feedback.sequence.append(feedback.sequence[i] + feedback.sequence[i - 1])
            goal_handle.publish_feedback(feedback)
            time.sleep(0.5)      # simulate long-running work

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback.sequence
        self.get_logger().info(f'Result: {list(result.sequence)}')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

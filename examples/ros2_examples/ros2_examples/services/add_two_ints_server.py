"""Services: a server answering example_interfaces/srv/AddTwoInts.

Run:   ros2 run ros2_examples add_two_ints_server
Check: ros2 service list -t
       ros2 interface show example_interfaces/srv/AddTwoInts
       ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 2, b: 3}"
"""
import rclpy
from example_interfaces.srv import AddTwoInts
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class AddTwoIntsServer(Node):

    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.handle_request)

    def handle_request(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'{request.a} + {request.b} = {response.sum}')
        return response      # the response object must be returned


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

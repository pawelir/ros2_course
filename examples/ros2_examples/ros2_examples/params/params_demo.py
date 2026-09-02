"""Parameters: declare, read, validate and react to changes at runtime.

Run:   ros2 run ros2_examples params_demo
   or: ros2 run ros2_examples params_demo --ros-args -p rate_hz:=5.0 -p greeting:=Hi
   or: ros2 launch ros2_examples params.launch.py   (loads config/params.yaml)
Then:  ros2 param list
       ros2 param get /params_demo rate_hz
       ros2 param set /params_demo rate_hz 0.5
       ros2 param set /params_demo rate_hz -1.0   -> rejected by the callback
"""
import rclpy
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter


class ParamsDemo(Node):

    def __init__(self):
        super().__init__('params_demo')

        # Declaring gives the parameter a type and a default. Undeclared params are rejected.
        self.declare_parameter('greeting', 'Hello')
        self.declare_parameter(
            'rate_hz', 1.0,
            ParameterDescriptor(description='Timer frequency in Hz, must be > 0'))
        self.declare_parameter('names', ['world'])

        # Read once at startup
        rate = self.get_parameter('rate_hz').value
        self.timer = self.create_timer(1.0 / rate, self.tick)

        # Called *before* a parameter is changed; return successful=False to reject.
        self.add_on_set_parameters_callback(self.validate_params)

    def validate_params(self, params: list[Parameter]) -> SetParametersResult:
        for p in params:
            if p.name == 'rate_hz':
                if p.value <= 0.0:
                    return SetParametersResult(successful=False, reason='rate_hz must be > 0')
                # Re-create the timer with the new period
                self.timer.cancel()
                self.timer = self.create_timer(1.0 / p.value, self.tick)
        return SetParametersResult(successful=True)

    def tick(self):
        # Reading every tick means `ros2 param set greeting` takes effect immediately.
        greeting = self.get_parameter('greeting').value
        names = self.get_parameter('names').value
        self.get_logger().info(f'{greeting}, {", ".join(names)}!')


def main(args=None):
    rclpy.init(args=args)
    node = ParamsDemo()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

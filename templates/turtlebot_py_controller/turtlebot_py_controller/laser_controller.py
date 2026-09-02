"""Module 2 starting point. Fill in the TODOs.

Run after building:  ros2 run turtlebot_py_controller laser_controller
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

# TODO: import LaserScan (sensor_msgs.msg) and TwistStamped (geometry_msgs.msg)


class LaserController(Node):

    def __init__(self):
        super().__init__('laser_controller')
        # TODO: create a subscription to /scan (queue size 10) with self.on_scan as callback
        # TODO: create a publisher of TwistStamped on /cmd_vel
        self.get_logger().info('laser_controller started')

    def on_scan(self, msg):
        # TODO: compute the smallest *valid* distance in msg.ranges
        #       (ignore inf/nan and values outside [range_min, range_max])
        # TODO: log it
        # TODO: publish forward velocity, or zero if the obstacle is closer than 0.5 m
        pass


def main(args=None):
    rclpy.init(args=args)
    node = LaserController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

"""Module 4 solution: custom message + two services.

Run:  ros2 launch turtlebot_py_controller laser_controller.launch.py use_rviz:=false
Try:  ros2 topic echo /obstacle_info
      ros2 service list -t
      ros2 service call /enable_motion std_srvs/srv/SetBool "{data: false}"
      ros2 service call /set_speed turtlebot_interfaces/srv/SetSpeed "{speed: 0.2}"
      ros2 service call /set_speed turtlebot_interfaces/srv/SetSpeed "{speed: 9.0}"   -> success: false
"""
import math

import rclpy
from geometry_msgs.msg import TwistStamped
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool
from turtlebot_interfaces.msg import ObstacleInfo
from turtlebot_interfaces.srv import SetSpeed

MAX_SPEED = 0.22   # TurtleBot3 burger


def closest_obstacle(scan: LaserScan, fov: float = 2 * math.pi) -> tuple[float, float]:
    """(distance, angle) of the smallest valid range within +-fov/2 of straight ahead.

    Returns (inf, 0.0) if there is no valid range in the sector. Angle is wrapped to [-pi, pi],
    0 = straight ahead, positive = left.
    """
    best_r, best_angle = math.inf, 0.0
    for i, r in enumerate(scan.ranges):
        if not (math.isfinite(r) and scan.range_min <= r <= scan.range_max and r < best_r):
            continue
        angle = scan.angle_min + i * scan.angle_increment
        angle = math.atan2(math.sin(angle), math.cos(angle))   # wrap to [-pi, pi]
        if abs(angle) <= fov / 2.0:
            best_r, best_angle = r, angle
    return best_r, best_angle


class LaserController(Node):

    def __init__(self):
        super().__init__('laser_controller')

        self.declare_parameter('forward_speed', 0.15,
                               ParameterDescriptor(description='Cruise speed [m/s], 0 < v <= 0.22'))
        self.declare_parameter('stop_distance', 0.5,
                               ParameterDescriptor(description='Stop if an obstacle is closer [m]'))
        self.declare_parameter('field_of_view_deg', 120.0,
                               ParameterDescriptor(description='Only obstacles within this sector ahead count'))
        self.declare_parameter('scan_topic', 'scan')
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')

        # Cache values used in every scan callback; refreshed by on_params_changed.
        self.forward_speed = self.get_parameter('forward_speed').value
        self.stop_distance = self.get_parameter('stop_distance').value
        self.fov = math.radians(self.get_parameter('field_of_view_deg').value)
        self.add_on_set_parameters_callback(self.on_params_changed)

        self.enabled = True   # toggled by the /enable_motion service

        scan_topic = self.get_parameter('scan_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.scan_sub = self.create_subscription(LaserScan, scan_topic, self.on_scan, 10)
        self.cmd_pub = self.create_publisher(TwistStamped, cmd_vel_topic, 10)
        self.info_pub = self.create_publisher(ObstacleInfo, 'obstacle_info', 10)

        # Services: a standard one (std_srvs/SetBool) and a custom one (turtlebot_interfaces/SetSpeed)
        self.enable_srv = self.create_service(SetBool, 'enable_motion', self.on_enable_motion)
        self.speed_srv = self.create_service(SetSpeed, 'set_speed', self.on_set_speed)

        self.get_logger().info('laser_controller started (module 4)')

    # ---- services -------------------------------------------------------------------------
    def on_enable_motion(self, request: SetBool.Request, response: SetBool.Response):
        self.enabled = request.data
        response.success = True
        response.message = 'motion enabled' if self.enabled else 'motion disabled'
        self.get_logger().info(response.message)
        return response

    def on_set_speed(self, request: SetSpeed.Request, response: SetSpeed.Response):
        if not 0.0 < request.speed <= MAX_SPEED:
            response.success = False
            response.message = f'speed must be in (0, {MAX_SPEED}]'
            return response
        # Go through the parameter API so `ros2 param get` stays consistent with reality.
        self.set_parameters([rclpy.parameter.Parameter(
            'forward_speed', rclpy.parameter.Parameter.Type.DOUBLE, float(request.speed))])
        response.success = True
        response.message = f'speed set to {request.speed:.2f} m/s'
        return response

    # ---- parameters -----------------------------------------------------------------------
    def on_params_changed(self, params) -> SetParametersResult:
        for p in params:
            if p.name == 'forward_speed':
                if not 0.0 < p.value <= MAX_SPEED:
                    return SetParametersResult(successful=False,
                                               reason=f'forward_speed must be in (0, {MAX_SPEED}]')
                self.forward_speed = p.value
            elif p.name == 'stop_distance':
                if p.value <= 0.0:
                    return SetParametersResult(successful=False, reason='stop_distance must be > 0')
                self.stop_distance = p.value
            elif p.name == 'field_of_view_deg':
                if not 0.0 < p.value <= 360.0:
                    return SetParametersResult(successful=False, reason='field_of_view_deg must be in (0, 360]')
                self.fov = math.radians(p.value)
        return SetParametersResult(successful=True)

    # ---- main loop (driven by incoming scans) ----------------------------------------------
    def on_scan(self, msg: LaserScan):
        distance, angle = closest_obstacle(msg, self.fov)
        blocked = distance < self.stop_distance

        info = ObstacleInfo()
        info.header = msg.header
        info.distance = float(distance)
        info.angle = float(angle)
        info.blocked = blocked
        self.info_pub.publish(info)

        cmd = TwistStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.header.frame_id = 'base_link'
        cmd.twist.linear.x = self.forward_speed if (self.enabled and not blocked) else 0.0
        self.cmd_pub.publish(cmd)

        self.get_logger().info(
            f'closest obstacle: {distance:.2f} m at {math.degrees(angle):.0f} deg -> '
            f'{"STOP" if blocked else ("go" if self.enabled else "disabled")}',
            throttle_duration_sec=1.0)


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

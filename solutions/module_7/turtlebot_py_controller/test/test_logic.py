"""Plain pytest unit tests: no ROS runtime, runs in milliseconds.

Run:  colcon test --packages-select turtlebot_py_controller && colcon test-result --verbose
  or: pytest src/turtlebot_py_controller/test/test_logic.py
"""
import math

from sensor_msgs.msg import LaserScan
from turtlebot_py_controller.laser_controller import closest_obstacle
from turtlebot_py_controller.rotate_action_server import wrap
from turtlebot_py_controller.wander import choose_turn


def make_scan(ranges, range_min=0.12, range_max=3.5):
    scan = LaserScan()
    scan.angle_min = 0.0
    scan.angle_increment = math.radians(1.0)
    scan.range_min = range_min
    scan.range_max = range_max
    scan.ranges = ranges
    return scan


def test_closest_obstacle_ignores_invalid_values():
    ranges = [3.0] * 360
    ranges[10] = 0.05           # below range_min -> ignored
    ranges[20] = math.inf       # ignored
    ranges[30] = float('nan')   # ignored
    ranges[45] = 1.2            # the real one
    dist, angle = closest_obstacle(make_scan(ranges))
    assert math.isclose(dist, 1.2, rel_tol=1e-6)   # ranges are float32
    assert math.isclose(angle, math.radians(45))


def test_closest_obstacle_empty_scan():
    dist, angle = closest_obstacle(make_scan([math.inf] * 10))
    assert dist == math.inf and angle == 0.0


def test_closest_obstacle_angle_is_wrapped():
    ranges = [3.0] * 360
    ranges[270] = 0.5           # 270 deg == -90 deg
    _, angle = closest_obstacle(make_scan(ranges))
    assert math.isclose(angle, -math.pi / 2)


def test_closest_obstacle_respects_field_of_view():
    ranges = [3.0] * 360
    ranges[180] = 0.2           # right behind the robot
    ranges[20] = 1.0            # 20 deg to the left
    dist, angle = closest_obstacle(make_scan(ranges), fov=math.radians(120))
    assert math.isclose(dist, 1.0, rel_tol=1e-6)
    assert math.isclose(angle, math.radians(20))


def test_wrap():
    assert math.isclose(wrap(3 * math.pi), math.pi) or math.isclose(wrap(3 * math.pi), -math.pi)
    assert math.isclose(wrap(0.5), 0.5)


def test_choose_turn_turns_away():
    assert choose_turn(math.radians(30)) < 0     # obstacle left -> turn right
    assert choose_turn(math.radians(-30)) > 0    # obstacle right -> turn left

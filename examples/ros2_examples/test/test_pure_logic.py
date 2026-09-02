"""Testing: plain pytest, no ROS runtime needed. Keep the logic you want to test
out of callbacks and into plain functions, then testing is trivial.

Run: pytest examples/ros2_examples/test/test_pure_logic.py
"""
import math

from ros2_examples.tf2.static_broadcaster import quaternion_from_yaw


def test_zero_yaw_is_identity():
    assert quaternion_from_yaw(0.0) == (0.0, 0.0, 0.0, 1.0)


def test_quaternion_is_unit_length():
    x, y, z, w = quaternion_from_yaw(1.234)
    assert math.isclose(x * x + y * y + z * z + w * w, 1.0, abs_tol=1e-9)

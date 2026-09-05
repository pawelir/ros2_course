"""Smoke test for the simulation launch file.

It catches typos in `sim.launch.py` and a missing simulation package long before anyone waits
for Gazebo to open.

Run:  colcon test --packages-select course_bringup
"""
import importlib.util
import pathlib

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument


def build_launch_description() -> LaunchDescription:
    """Import launch/sim.launch.py by path (launch files are data, not an importable module)."""
    path = pathlib.Path(__file__).resolve().parent.parent / 'launch' / 'sim.launch.py'
    spec = importlib.util.spec_from_file_location('sim_launch', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()


def test_generates_a_launch_description():
    assert isinstance(build_launch_description(), LaunchDescription)


def test_declares_the_documented_arguments():
    declared = {a.name for a in build_launch_description().entities
                if isinstance(a, DeclareLaunchArgument)}
    assert {'gui', 'world', 'x_pose', 'y_pose'} <= declared

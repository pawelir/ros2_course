"""Launch: start one node with a YAML parameter file and a launch argument.

Run: ros2 launch ros2_examples params.launch.py
     ros2 launch ros2_examples params.launch.py greeting:=Hey
     ros2 launch ros2_examples params.launch.py --show-args
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('ros2_examples'), 'config', 'params.yaml')

    greeting_arg = DeclareLaunchArgument(
        'greeting', default_value='Hello from launch',
        description='Overrides the greeting parameter from the YAML file')

    node = Node(
        package='ros2_examples',
        executable='params_demo',
        name='params_demo',
        output='screen',
        # Later entries win: the launch argument overrides the YAML value.
        parameters=[config, {'greeting': LaunchConfiguration('greeting')}],
    )

    return LaunchDescription([greeting_arg, node])

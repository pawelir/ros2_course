"""Module 3 solution: simulation + controller (with YAML params) + RViz, all from one launch file.

Run:  ros2 launch turtlebot_py_controller laser_controller.launch.py
      ros2 launch turtlebot_py_controller laser_controller.launch.py gui:=false
      ros2 launch turtlebot_py_controller laser_controller.launch.py use_rviz:=false stop_distance:=1.0
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('turtlebot_py_controller')
    params_file = os.path.join(pkg_share, 'config', 'laser_controller.yaml')
    rviz_config = os.path.join(pkg_share, 'rviz', 'laser.rviz')

    use_sim = DeclareLaunchArgument('use_sim', default_value='true',
                                    description='Also start the Gazebo simulation')
    gui = DeclareLaunchArgument('gui', default_value='true', description='Gazebo GUI (false on headless machines)')
    use_rviz = DeclareLaunchArgument('use_rviz', default_value='true')
    stop_distance = DeclareLaunchArgument('stop_distance', default_value='0.4',
                                          description='Overrides the YAML value')

    simulation = IncludeLaunchDescription(
        # FindPackageShare is resolved lazily, so use_sim:=false works even without the sim packages installed
        PythonLaunchDescriptionSource(PathJoinSubstitution(
            [FindPackageShare('course_bringup'), 'launch', 'sim.launch.py'])),
        launch_arguments={'gui': LaunchConfiguration('gui')}.items(),
        condition=IfCondition(LaunchConfiguration('use_sim')),
    )

    controller = Node(
        package='turtlebot_py_controller',
        executable='laser_controller',
        name='laser_controller',
        output='screen',
        # YAML first, then overrides from launch arguments (later wins)
        parameters=[params_file, {'stop_distance': LaunchConfiguration('stop_distance')}],
    )

    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz2', output='log',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    return LaunchDescription([use_sim, gui, use_rviz, stop_distance, simulation, controller, rviz])

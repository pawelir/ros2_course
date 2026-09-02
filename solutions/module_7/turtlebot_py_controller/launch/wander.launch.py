"""Module 7 solution: whole system. Sim + laser controller + rotate action server + wander + RViz.

Run:  ros2 launch turtlebot_py_controller wander.launch.py
      ros2 launch turtlebot_py_controller wander.launch.py use_sim:=false use_rviz:=false record:=true
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('turtlebot_py_controller')

    use_sim = DeclareLaunchArgument('use_sim', default_value='true')
    gui = DeclareLaunchArgument('gui', default_value='true')
    use_rviz = DeclareLaunchArgument('use_rviz', default_value='true')
    record = DeclareLaunchArgument('record', default_value='false',
                                   description='Record /scan /odom /cmd_vel /obstacle_info to a bag')

    # Re-use the module 6 launch file (sim + controller + locator + rviz)
    base = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_share, 'launch', 'laser_controller.launch.py')),
        launch_arguments={'use_sim': LaunchConfiguration('use_sim'),
                          'gui': LaunchConfiguration('gui'),
                          'use_rviz': LaunchConfiguration('use_rviz')}.items())

    rotate_server = Node(package='turtlebot_py_controller', executable='rotate_action_server',
                         name='rotate_action_server', output='screen')
    wander = Node(package='turtlebot_py_controller', executable='wander', name='wander', output='screen',
                  parameters=[{'turn_angle_deg': 90.0, 'angular_speed': 0.8}])

    bag = ExecuteProcess(
        cmd=['ros2', 'bag', 'record', '-o', '/tmp/wander_bag', '/scan', '/odom', '/cmd_vel', '/obstacle_info'],
        output='screen', condition=IfCondition(LaunchConfiguration('record')))

    return LaunchDescription([use_sim, gui, use_rviz, record, base, rotate_server, wander, bag])

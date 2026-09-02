"""TurtleBot3 (burger) in Gazebo Harmonic. Same as turtlebot3_gazebo/turtlebot3_world.launch.py
but with a `gui` switch, so it also runs on machines without a display.

Run:  ros2 launch course_bringup sim.launch.py
      ros2 launch course_bringup sim.launch.py gui:=false
      ros2 launch course_bringup sim.launch.py world:=turtlebot3_house
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
    # The turtlebot3_gazebo launch files read this at import time; default it so the launch
    # also works outside the devcontainer (which sets it in containerEnv).
    os.environ.setdefault('TURTLEBOT3_MODEL', 'burger')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gui = DeclareLaunchArgument('gui', default_value='true', description='Start the Gazebo GUI')
    world = DeclareLaunchArgument('world', default_value='turtlebot3_world',
                                  description='World file name in turtlebot3_gazebo/worlds (without .world)')
    x_pose = DeclareLaunchArgument('x_pose', default_value='-2.0')
    y_pose = DeclareLaunchArgument('y_pose', default_value='-0.5')

    world_file = PathJoinSubstitution([tb3_gazebo, 'worlds', [LaunchConfiguration('world'), '.world']])

    gz_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -s -v2 ', world_file], 'on_exit_shutdown': 'true'}.items())

    gz_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-g -v2 ', 'on_exit_shutdown': 'true'}.items(),
        condition=IfCondition(LaunchConfiguration('gui')))

    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items())

    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')),
        launch_arguments={'x_pose': LaunchConfiguration('x_pose'),
                          'y_pose': LaunchConfiguration('y_pose')}.items())

    models_path = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(tb3_gazebo, 'models'))

    return LaunchDescription([gui, world, x_pose, y_pose, models_path,
                              gz_server, gz_client, spawn_robot, robot_state_publisher])

"""Launch: two nodes, a remapped topic, a namespace and a conditional node.

Run: ros2 launch ros2_examples pubsub.launch.py
     ros2 launch ros2_examples pubsub.launch.py with_listener:=false
Then: ros2 topic list   -> /demo/greetings instead of /chatter
      rqt_graph
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    with_listener = DeclareLaunchArgument('with_listener', default_value='true')

    talker = Node(
        package='ros2_examples', executable='minimal_publisher',
        namespace='demo', name='talker', output='screen',
        remappings=[('chatter', 'greetings')],
    )
    listener = Node(
        package='ros2_examples', executable='minimal_subscriber',
        namespace='demo', name='listener', output='screen',
        remappings=[('chatter', 'greetings')],
        condition=IfCondition(LaunchConfiguration('with_listener')),
    )
    return LaunchDescription([with_listener, talker, listener])

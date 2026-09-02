import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'ros2_examples'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pawel Irzyk',
    maintainer_email='pawel.irzyk6@gmail.com',
    description='Minimal rclpy examples for the ROS 2 course.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # topics
            'minimal_publisher = ros2_examples.topics.minimal_publisher:main',
            'minimal_subscriber = ros2_examples.topics.minimal_subscriber:main',
            # parameters
            'params_demo = ros2_examples.params.params_demo:main',
            # services
            'add_two_ints_server = ros2_examples.services.add_two_ints_server:main',
            'add_two_ints_client = ros2_examples.services.add_two_ints_client:main',
            # actions
            'fibonacci_server = ros2_examples.actions.fibonacci_server:main',
            'fibonacci_client = ros2_examples.actions.fibonacci_client:main',
            # tf2
            'static_broadcaster = ros2_examples.tf2.static_broadcaster:main',
            'dynamic_broadcaster = ros2_examples.tf2.dynamic_broadcaster:main',
            'frame_listener = ros2_examples.tf2.frame_listener:main',
            # executors
            'blocking_callback_bug = ros2_examples.executors.blocking_callback_bug:main',
            'multithreaded_fix = ros2_examples.executors.multithreaded_fix:main',
        ],
    },
)

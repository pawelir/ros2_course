import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'turtlebot_py_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='Course package: laser-based TurtleBot3 controller.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'laser_controller = turtlebot_py_controller.laser_controller:main',
            'rotate_action_server = turtlebot_py_controller.rotate_action_server:main',
            'rotate_action_client = turtlebot_py_controller.rotate_action_client:main',
            'obstacle_locator = turtlebot_py_controller.obstacle_locator:main',
        ],
    },
)

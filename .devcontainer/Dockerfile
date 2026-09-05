FROM osrf/ros:jazzy-desktop-full

ARG DEBIAN_FRONTEND=noninteractive

# Simulation (TurtleBot3 + Gazebo Harmonic), tooling used in the exercises
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-turtlebot3 \
    ros-jazzy-turtlebot3-gazebo \
    ros-jazzy-turtlebot3-msgs \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-rqt-common-plugins \
    ros-jazzy-tf2-tools \
    ros-jazzy-ros2bag \
    ros-jazzy-rosbag2-storage-mcap \
    ros-jazzy-example-interfaces \
    ros-jazzy-launch-testing \
    ros-jazzy-launch-testing-ros \
    python3-colcon-common-extensions \
    python3-pytest \
    python3-pip \
    git nano tree bash-completion \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu 24.04 base image already has user "ubuntu" (uid 1000); give it sudo
RUN apt-get update && apt-get install -y --no-install-recommends sudo \
    && echo "ubuntu ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    && rm -rf /var/lib/apt/lists/*


ENV GZ_SIM_RESOURCE_PATH=/opt/ros/jazzy/share/turtlebot3_gazebo/models

USER ubuntu
WORKDIR /workspaces/ros2_course

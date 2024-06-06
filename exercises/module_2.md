
# module 1

## Theory

- Package structure
- ROS 2 C++ Client Library (rclcpp)
- Subscriber and Publisher
- Parameters
- Launch file
- Rviz visualization

## Exercise

The exercise goal is to create first ROS 2 package and node. The responsibility of a created node will be to process subscribed laser scan data from turtlebot3 robot. This will serve as a base for further development on later course stages.

Make sure to check out the ROS 2 package template for reference, you'll find it in [pawelir/ros2_templates](https://github.com/pawelir/ros2_templates) repository. It will help you a lot with the implementation, now and later during the course.

1. Create the package `turtlebot_laser_controller`. (Lecture 2, Slides x-x)

   1. OPTIONAL (more difficult) - Create the package from scratch. You can use the command `ros2 pkg create` to create a new package with the dependencies: `rclcpp` `sensor_msgs`.

   2. OR (easy): Clone predefined package from github.

        ```bash
        cd /workspaces/vscode_ros2_workspace/src
        git clone https://github.com/pawelir/turtlebot_laser_controller.git
        ```

1. Inspect the `CMakelists.txt` and `package.xml` files. (Lecture 2 Slides x-x)

   1. Make sure that dependencies are set in both files

1. Create a subscriber to the `/scan` topic. (Lecture 2 Slides x-x)

1. Add a configuration file with parameters `topic_name` and `queue_size` for the subscriber of the topic
`/scan`. (Lecture 2 Slides x-x)

1. Create a callback method for that subscriber which outputs the smallest distance
measurement from the `ranges` vector in the message of the `/scan` topic. Inspect the message type [here](https://docs.ros2.org/latest/api/sensor_msgs/msg/LaserScan.html).

1. Add launch file to the package, that will be responsible for:
   1. Running `turtlebot_laser_controller` node
   2. Loading node's parameters from configuration file

1. Pass the argument laser_enabled from your launch file to the
smb_gazebo.launch file with value true.

1. [OPTIONAL] Check the [ros2_laser_scan_merger](https://github.com/mich1342/ros2_laser_scan_merger) package, find out what it is doing. What topics node subscribes and publishes, what are the node parameters.
TODO: Add more steps e.g.

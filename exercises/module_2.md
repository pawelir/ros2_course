# Module 2: First package, publisher and subscriber

## Theory

- Package anatomy for Python (`package.xml`, `setup.py`, `setup.cfg`, `resource/`)
- rclpy: `Node`, `create_subscription`, `create_publisher`, `create_timer`, logging, `spin`
- Building with `colcon build --symlink-install`, sourcing `install/setup.bash`
- Message types: `sensor_msgs/LaserScan`, `geometry_msgs/TwistStamped`

Lecture examples: `examples/ros2_examples/ros2_examples/topics/`.

## Exercise

Goal: a node that reads the laser scanner and stops the robot before it hits something. This package grows through the
rest of the course.

1. **Create the package `turtlebot_py_controller`.** _Slides: 02-workspace-and-packages_

   Either from scratch (harder):

   ```bash
   mkdir -p /workspaces/ros2_course/src && cd /workspaces/ros2_course/src
   ros2 pkg create turtlebot_py_controller --build-type ament_python --node-name laser_controller \
       --dependencies rclpy sensor_msgs geometry_msgs
   ```

   or from the template (easier):

   ```bash
   cp -r /workspaces/ros2_course/templates/turtlebot_py_controller /workspaces/ros2_course/src/
   ```

   Open `package.xml` and `setup.py`. Where are dependencies declared? Where do executables get their names?

2. **Build and run the empty node.**

   ```bash
   cd /workspaces/ros2_course
   colcon build --symlink-install
   source install/setup.bash
   ros2 run turtlebot_py_controller laser_controller
   ```

   The template's node only logs a message. With `--symlink-install` you can edit Python and re-run without rebuilding,
   unless you touch `setup.py` (then rebuild). If `ros2 run` says "No executable found", check the `console_scripts`
   entry in `setup.py`.

3. **Subscribe to `/scan`.** _Slides: 03-rclpy (Init and spin, Logging, Topic subscriber)_

   In the callback, compute the smallest *valid* distance: ignore `inf`/`nan` and anything outside
   `[range_min, range_max]`. Log it. Run with the simulation and drive around with teleop. Does the value make sense?

   Logging at 5 Hz is noisy. Use `throttle_duration_sec=1.0` in `get_logger().info(...)`.

4. **Publish to `/cmd_vel`.**

   Publish a `TwistStamped` in the same callback: `linear.x = 0.15` if the closest obstacle is farther than 0.5 m,
   otherwise `0.0`. Set `header.stamp` to the node's clock. Stop teleop first, two publishers on `/cmd_vel` fight.

   **Checkpoint:** the robot drives forward and stops in front of the first wall or pillar. `ros2 topic hz /cmd_vel`
   shows about 5 Hz (why exactly that rate?).

5. **Inspect what you built.** `ros2 node info /laser_controller`, `rqt_graph`. Your node should sit between the bridge
   and... the bridge.

### Stretch

- Move the "smallest valid range" computation into a plain function outside the class. Module 7 will unit-test it.
- Only consider the front 60 degrees of the scan. Which indices are those? (Careful: index 0 is straight ahead and the
  scan wraps around, so the front sector is `ranges[-30:] + ranges[:30]`.)

Solution: `solutions/module_2/`.

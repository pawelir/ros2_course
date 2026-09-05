# Module 4: Custom interfaces and services

## Theory

- Interface packages (`ament_cmake` + `rosidl_generate_interfaces`), `.msg` / `.srv` / `.action` syntax
- Services: server callback, `create_client`, `call_async` and why not to block inside callbacks
- Standard interfaces worth knowing: `std_srvs`, `example_interfaces`

Lecture examples: `examples/ros2_examples/ros2_examples/services/`.

## Exercise

Goal: publish a structured "closest obstacle" message and control the node through services.

1. **Interface package.** _Slides: 05-services-and-actions (Custom interfaces, Services)_ Create
   `turtlebot_interfaces` (this one must be `ament_cmake`, Python packages
   cannot generate interfaces):

   ```bash
   cd /workspaces/ros2_course/src
   ros2 pkg create --build-type ament_cmake turtlebot_interfaces --dependencies std_msgs geometry_msgs
   ```

   Add `msg/ObstacleInfo.msg`:

   ```text
   std_msgs/Header header
   float32 distance     # [m]
   float32 angle        # [rad], 0 = straight ahead, positive = left
   bool blocked
   ```

   and `srv/SetSpeed.srv`:

   ```text
   float32 speed
   ---
   bool success
   string message
   ```

   Wire them into `CMakeLists.txt` and `package.xml` as in the slides (`rosidl_default_generators`,
   `rosidl_default_runtime`, `rosidl_interface_packages` group). Build, source, then:

   ```bash
   ros2 interface show turtlebot_interfaces/msg/ObstacleInfo
   ros2 interface show turtlebot_interfaces/srv/SetSpeed
   ```

   Common trap: after adding a new interface you must re-source `install/setup.bash` in every terminal.

2. **Publish `ObstacleInfo`.** Extend the scan callback to also compute the *angle* of the closest range
   (`angle_min + index * angle_increment`, wrapped to `[-pi, pi]`) and publish `/obstacle_info`.
   Add `turtlebot_interfaces` to `package.xml`.

   While you are there: a wall *behind* the robot should not stop it. Add a parameter `field_of_view_deg`
   (default 120) and only consider rays within half of it to either side of straight ahead.

   **Checkpoint:** `ros2 topic echo /obstacle_info` while you push the robot toward a pillar with teleop.

3. **Enable/disable service.** Add a `std_srvs/srv/SetBool` server on `enable_motion`. When it is switched
   off, publish one zero velocity — remember module 1, the last command stays latched, so you have to send
   a stop actively — and then keep off `/cmd_vel` entirely until it is switched back on. Keep publishing
   `/obstacle_info` either way. Module 5 adds a second node that drives `/cmd_vel`; if this one kept
   publishing zeros the two would fight over the topic.

   ```bash
   ros2 service list -t
   ros2 service call /enable_motion std_srvs/srv/SetBool "{data: false}"
   ```

4. **Custom service.** Add a `SetSpeed` server on `set_speed`. Validate the range like the parameter callback did.
   Bonus consistency: implement it by calling `self.set_parameters([...])` so `ros2 param get forward_speed`
   agrees with what the robot does.

   **Checkpoint:** `{speed: 9.0}` returns `success: false` with a message, `{speed: 0.2}` speeds the robot up.

5. **A client.** Write a tiny script (or node) that calls `set_speed` from Python with `call_async` and
   `spin_until_future_complete`. Compare with the lecture example `add_two_ints_client.py`.

### Stretch

- Why would calling `client.call()` (synchronous) from inside a subscription callback hang forever with the default
  executor? Try it. Module 6 explains the fix.

Solution: `solutions/module_4/` (also contains the `.action` file used in module 5).

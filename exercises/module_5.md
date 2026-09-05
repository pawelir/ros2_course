# Module 5: Actions

## Theory

- Why actions: long-running goals, feedback, cancel, result
- `ActionServer`: goal / cancel / execute callbacks, goal handle states
- `ActionClient`: `send_goal_async`, feedback callback, result future
- `ros2 action` CLI

Lecture examples: `examples/ros2_examples/ros2_examples/actions/`.

## Exercise

Goal: rotate the robot by a requested angle using odometry, with live feedback and cancellation.

1. **Define the action** in `turtlebot_interfaces/action/RotateToAngle.action`:

   ```text
   float32 angle            # [rad] relative, positive = counter-clockwise, |angle| <= pi
   float32 angular_speed    # [rad/s]
   ---
   float32 final_yaw        # [rad]
   ---
   float32 remaining        # [rad]
   ```

   Add it to `rosidl_generate_interfaces`, build, `ros2 interface show turtlebot_interfaces/action/RotateToAngle`.

2. **Yaw from odometry.** _Slides: 05-services-and-actions (Actions)_ In a new node `rotate_action_server`
   subscribe to `/odom` and convert
   `pose.pose.orientation` (quaternion) to yaw:

   ```python
   yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
   ```

3. **Action server.** Create an `ActionServer` on `rotate_to_angle`.
   - `goal_callback`: reject if no odometry yet, if `angular_speed <= 0`, or if `|angle| > pi` (see below).
   - `execute_callback`: compute `target_yaw = wrap(yaw + angle)`; loop at 20 Hz publishing `TwistStamped` with
     `angular.z`, publishing feedback `remaining`, until `|remaining| < 0.02`. Then publish zero, `succeed()`, return
     the result.
   - `cancel_callback`: accept; in the loop check `goal_handle.is_cancel_requested`, stop the robot, `canceled()`.

   `remaining` is a *wrapped* error, so it cannot tell "20 degrees to go" apart from "340 degrees the other
   way round". That is why goals are limited to `|angle| <= pi`: without the check, a goal of 4 rad looks
   already overshot on the very first iteration and the server reports success without ever moving. Reject
   it in `goal_callback` instead of lying in the result.

   The execute loop blocks for seconds. For odometry to keep arriving during that time, the server needs a
   `ReentrantCallbackGroup` and a `MultiThreadedExecutor` (see `fibonacci_server.py`). Without them, `yaw` never
   updates and the loop never ends. Try it once to see the symptom.

   ```bash
   ros2 service call /enable_motion std_srvs/srv/SetBool "{data: false}"   # stop the laser controller first
   ros2 run turtlebot_py_controller rotate_action_server
   ros2 action send_goal /rotate_to_angle turtlebot_interfaces/action/RotateToAngle \
       "{angle: 1.57, angular_speed: 0.5}" --feedback
   ```

   **Checkpoint:** the robot turns 90 degrees and stops within a couple of degrees. `Ctrl+C` during the motion
   cancels the goal and the robot stops. Watch it in RViz (TF display).

4. **Action client.** Write `rotate_action_client` that takes an angle in degrees from the command line, prints
   feedback and exits after the result. Structure: `send_goal_async` -> goal response callback ->
   `get_result_async` -> result callback -> `rclpy.shutdown()`.

### Stretch

- Slow down near the target (`angular.z` proportional to `remaining`, with a minimum) to reduce overshoot.
- Reject a new goal while one is executing, or abort the running one (look at `ActionServer(handle_accepted_callback=...)`).
- Lift the `|angle| <= pi` limit: accumulate the yaw actually travelled each iteration instead of comparing
  against a wrapped target, so `angle: 6.28` really turns a full circle.

Solution: `solutions/module_5/`.

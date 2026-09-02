# Module 6: TF2 and executors

## Theory

- TF2: frames, the tree, static vs dynamic transforms, `Buffer`, `TransformListener`, `lookup_transform`, time
- `tf2_ros` CLI: `tf2_echo`, `view_frames`, `static_transform_publisher`
- Executors: single vs multi-threaded, callback groups (mutually exclusive vs reentrant)

Lecture examples: `examples/ros2_examples/ros2_examples/tf2/`, `examples/ros2_examples/ros2_examples/executors/`.

## Exercise

Goal: put the closest obstacle on the map (odom frame) and learn why callbacks sometimes freeze.

1. **Explore the tree.** With the simulation running:

   ```bash
   ros2 run tf2_tools view_frames            # writes frames_*.pdf
   ros2 run tf2_ros tf2_echo odom base_scan
   ```

   Which frames exist? Who publishes `odom -> base_footprint` (dynamic) and `base_link -> base_scan` (static)?
   Look at `ros2 topic echo /tf_static --once`.

2. **Obstacle locator node.** _Slides: 04-tools (TF2), 03-rclpy (Executors)_ New node `obstacle_locator`:
   - subscribes to `/obstacle_info`,
   - builds a `geometry_msgs/PointStamped` in the scan frame: `x = d*cos(angle)`, `y = d*sin(angle)`,
     `header = info.header`,
   - transforms it to `odom` with `tf_buffer.transform(point, 'odom', timeout=Duration(seconds=0.1))`
     (import `tf2_geometry_msgs` first, that registers `PointStamped` with tf2),
   - publishes `/obstacle_point`. Catch `TransformException` and warn (throttled) instead of crashing.

   Make the target frame a parameter. Add a `PointStamped` display in RViz.

   **Checkpoint:** drive around a pillar with teleop. The red dot in RViz stays *on the pillar* while the robot
   moves, because it is expressed in `odom`, not in the robot frame.

3. **Plant a bug.** Add a timer (every 10 s) whose callback does `time.sleep(2.0)` and logs a statistic.
   Run it: `/obstacle_point` freezes for 2 s each time. Why? Reproduce with `ros2 topic hz /obstacle_point`.

4. **Fix it with callback groups.** Put the subscription and the slow timer in two different
   `MutuallyExclusiveCallbackGroup`s and spin the node with `MultiThreadedExecutor(num_threads=2)`.

   **Checkpoint:** `/obstacle_point` keeps its rate during the slow callback. Now explain: why is a *mutually
   exclusive* group still the right default for the subscription (hint: shared state)?

5. **Add it to the launch file** from module 3.

### Stretch

- Transform to `base_footprint` instead of `odom` and explain the difference you see in RViz.
- Publish a static transform `base_link -> fake_camera` from the launch file with `static_transform_publisher`
  and check it with `tf2_echo`.

Solution: `solutions/module_6/`.

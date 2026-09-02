# Module 7: Putting it together, bags and tests

## Theory

- Composing behaviours from topics, services and actions; state machines in a node
- `ros2 bag` record/play/info, replaying sensor data without the simulator
- Testing: plain `pytest` for logic, `launch_testing` for integration, `colcon test`

Lecture examples: `examples/ros2_examples/test/`.

## Exercise

Goal: a robot that wanders around the arena on its own, plus tests that prove the pieces work.

1. **Wander node.** _Slides: 05-services-and-actions (Communication strategies, Testing your nodes), 04-tools
   (rosbag)_ New node `wander` with two states, `DRIVING` and `TURNING`:
   - subscribe to `/obstacle_info`; when `blocked` and state is `DRIVING`, switch to `TURNING`,
   - call `enable_motion(false)` (async!), then send a `RotateToAngle` goal *away* from the obstacle
     (obstacle on the left -> turn right),
   - when the result arrives, call `enable_motion(true)` and go back to `DRIVING`.

   Everything happens in callbacks, so every service/action call must be `*_async` with `add_done_callback`.
   Keep the "which way to turn" decision in a plain function `choose_turn(angle) -> float`.

2. **System launch file** `wander.launch.py` that includes the module 3/6 launch file and adds
   `rotate_action_server` and `wander`. Add a `record` argument that starts
   `ros2 bag record /scan /odom /cmd_vel /obstacle_info` via `ExecuteProcess`.

   **Checkpoint:** the robot drives, stops before a pillar, turns 90 degrees, drives on. Let it run for a minute.

3. **Bags.** Record a minute of wandering, then:

   ```bash
   ros2 bag info /tmp/wander_bag
   # stop the simulation, then:
   ros2 bag play /tmp/wander_bag --topics /scan
   ros2 run turtlebot_py_controller laser_controller
   ```

   The controller works on recorded data with no simulator at all. Why is this useful in practice?

4. **Unit tests** in `test/test_logic.py`: `closest_obstacle` ignores invalid ranges and wraps the angle;
   `choose_turn` turns away from the obstacle. Run with `colcon test` and `colcon test-result --verbose`
   (remember `ranges` are `float32`, compare with `math.isclose`).

5. **Integration test** in `test/test_controller_launch.py` with `launch_testing`: start `laser_controller`,
   publish a fake `LaserScan`, assert that `/cmd_vel` is `0.1` when clear and `0.0` when blocked.

   **Checkpoint:** `colcon test --packages-select turtlebot_py_controller` reports 0 failures.

### Stretch

- Use `/obstacle_point` from module 6 to avoid turning back toward a pillar you just left.
- Make `wander` a lifecycle node (`rclpy.lifecycle.Node`) so it can be paused with `ros2 lifecycle set`.

Solution: `solutions/module_7/`.

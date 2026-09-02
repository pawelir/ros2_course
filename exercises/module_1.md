# Module 1: Exploring a running ROS 2 system

## Theory

- ROS 2 architecture: nodes, DDS, the ROS graph
- Nodes, topics, messages, quality of service
- CLI tools: `ros2 node`, `ros2 topic`, `ros2 interface`, `rqt_graph`
- Workspaces, packages, `colcon`, sourcing

## Exercise

Goal: get comfortable with the CLI by poking at the TurtleBot3 simulation. No code yet.

1. **Start the simulation.** Run the VS Code task `simulation` (`Ctrl+Shift+P` -> `Tasks: Run Task` -> `simulation`).
   Gazebo opens with a TurtleBot3 *burger* in a small arena. On a slow machine use `simulation (headless)` instead.

   From a terminal the same thing is:

   ```bash
   ros2 launch course_bringup sim.launch.py            # add gui:=false for headless
   ```

2. **Inspect the graph.** _Slides: 01-basic-concepts (Nodes, Topics, Messages), 04-tools (rqt_graph)_

   1. List the running nodes. You should see `/robot_state_publisher` and `/ros_gz_bridge`.
   2. Show details of `/ros_gz_bridge`: which topics does it publish and subscribe to?
   3. List all topics with their types (`ros2 topic list -t`).
   4. What is the message type of `/scan`? Print its definition with `ros2 interface show`.
      Find the fields `ranges`, `range_min`, `range_max`, `angle_increment`. What do they mean?
   5. Echo `/scan` once. How many values are in `ranges`? What does `inf` mean there?
   6. Measure the publish rate of `/scan` and `/odom` (`ros2 topic hz`). Which is faster and why?
   7. Open `rqt_graph`. Which node produces `/scan`? Where does `/cmd_vel` go?

   **Checkpoint:** you can explain, in one sentence each, what `/scan`, `/odom`, `/cmd_vel` and `/tf` carry.

3. **Drive the robot from the terminal.** _Slides: 01-basic-concepts (Topics – CLI, Messages)_

   `/cmd_vel` is of type `geometry_msgs/msg/TwistStamped` (not plain `Twist`, mind the header).
   Publish a forward velocity of 0.1 m/s:

   ```bash
   ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/TwistStamped "{twist: {linear: {x: 0.1}}}"
   ```

   Stop it with `Ctrl+C`, then make the robot spin in place. Watch `/odom` while it moves.

4. **Drive with the keyboard.** Run the `teleop` task, or:

   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
   ```

   Why is the `stamped` parameter needed? (Look at the error you get without it.)

5. **Record and replay.** Record 10 seconds of `/scan` and `/odom` into a bag while driving around, then stop the
   simulation and play the bag back. Verify with `ros2 topic hz /scan` that the data is "live" again.

   ```bash
   ros2 bag record -o /tmp/module1 /scan /odom
   ros2 bag info /tmp/module1
   ros2 bag play /tmp/module1
   ```

### Stretch

- Use `ros2 topic echo /scan --field ranges` and find the index of the smallest value. Which direction is that?
  (Hint: `angle_min` and `angle_increment`, index 0 is straight ahead.)
- Check the QoS of `/scan` with `ros2 topic info -v /scan`. Why is a sensor stream *best effort*?

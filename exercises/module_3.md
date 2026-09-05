# Module 3: Parameters, launch files, RViz

## Theory

- Parameters: declare, get, set, YAML files, `ros2 param`, set-parameter callbacks
- Launch files in Python: `Node`, `DeclareLaunchArgument`, `LaunchConfiguration`, `IncludeLaunchDescription`,
  conditions, `data_files` in `setup.py`
- RViz: fixed frame, displays, saving a config

Lecture examples: `examples/ros2_examples/ros2_examples/params/`, `examples/ros2_examples/launch/`.

## Exercise

Goal: no more magic numbers in the code, and one command that starts everything.

1. **Parameters.** _Slides: 03-rclpy (Parameters), 01-basic-concepts (Parameters – CLI)_

   Turn the constants of module 2 into declared parameters: `forward_speed` (default 0.15), `stop_distance` (0.5),
   `scan_topic` (`scan`), `cmd_vel_topic` (`cmd_vel`). Read them once in `__init__`.

   ```bash
   ros2 run turtlebot_py_controller laser_controller --ros-args -p stop_distance:=1.0
   ros2 param list /laser_controller
   ros2 param get /laser_controller stop_distance
   ```

2. **Change at runtime.** `ros2 param set /laser_controller stop_distance 1.0` succeeds, but the node ignores it. Why?
   Add `add_on_set_parameters_callback` and update the cached values there. Reject `forward_speed` outside
   `(0, 0.22]` (the burger's limit) with `SetParametersResult(successful=False, reason=...)`.

   **Checkpoint:** `ros2 param set /laser_controller forward_speed 5.0` prints your reason. Setting `0.2` makes the
   robot faster immediately.

3. **YAML config.** Create `config/laser_controller.yaml`:

   ```yaml
   laser_controller:
     ros__parameters:
       forward_speed: 0.12
       stop_distance: 0.4
   ```

   Install it via `data_files` in `setup.py` (the template already has the `glob('config/*.yaml')` line), rebuild, then
   run with `--ros-args --params-file <path>`. Find the installed path with `ros2 pkg prefix turtlebot_py_controller`.

4. **Launch file.** _Slides: 03-rclpy (Launch)_ Create `launch/laser_controller.launch.py` that:
   1. includes `course_bringup/sim.launch.py` (guarded by a `use_sim` argument, default `true`) and forwards a
      `gui` argument to it,
   2. starts `laser_controller` with the YAML file,
   3. has a `stop_distance` launch argument that overrides the YAML value,
   4. starts RViz with a config file (`use_rviz` argument).

   ```bash
   ros2 launch turtlebot_py_controller laser_controller.launch.py --show-args
   ros2 launch turtlebot_py_controller laser_controller.launch.py stop_distance:=0.8 use_rviz:=false
   ```

5. **RViz.** _Slides: 04-tools (RViz2)_ Start `rviz2`, set Fixed Frame to `odom`, add displays: `TF`,
   `LaserScan` on `/scan`, and `RobotModel` from topic `/robot_description`. For that last one set
   *Durability Policy* to **Transient Local**, or the robot never appears: the description is published
   once, latched, long before RViz starts listening.
   Save as `rviz/laser.rviz` in your package and point the launch file at it.

   **Checkpoint:** one command starts sim, controller and RViz; the laser points hug the walls; changing
   `stop_distance:=1.0` on the command line makes the robot stop earlier.

### Stretch

- Add a `world` launch argument and pass it down to the simulation include (`world:=turtlebot3_house` is fun).
- Make `scan_topic` a *read-only* parameter (`ParameterDescriptor(read_only=True)`). What happens on `ros2 param set`?

Solution: `solutions/module_3/`.

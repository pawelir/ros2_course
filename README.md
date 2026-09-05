# ROS 2 course (Jazzy, Python)

Slides plus hands-on exercises. Everything runs inside the provided dev container: ROS 2 Jazzy, Gazebo Harmonic and a
TurtleBot3 simulation.

## Setup

1. Install Docker and VS Code with the *Dev Containers* extension.
2. `git clone` this repo, open the folder in VS Code, accept *Reopen in Container*. First build takes a few minutes.
3. Open a terminal in the container and run the `simulation` task (`Ctrl+Shift+P` -> *Tasks: Run Task*).
   Gazebo appears with a TurtleBot3. If you have no display, use `simulation (headless)`.

Notes:

- Linux hosts need `xhost +local:` once for the GUI to show.
- On a slow laptop use `simulation (headless)` and RViz only. Gazebo renders in software by default; on a Linux host
  with a GPU, add `"--device=/dev/dri"` to `runArgs` in `devcontainer.json` for hardware acceleration.
- ROS environment variables (`ROS_DOMAIN_ID`, `ROS_AUTOMATIC_DISCOVERY_RANGE`, `TURTLEBOT3_MODEL`) are set once in
  `devcontainer.json` under `containerEnv`. Discovery is limited to the container's host, so students on one network
  do not see each other's robots. To talk to another machine, export `ROS_DOMAIN_ID` on your host before opening the
  container and change the discovery range to `SUBNET`.

Your own packages go into `src/`. Build from the repo root:

```bash
colcon build --symlink-install
source install/setup.bash
```

## Course map

| Module | Topic                    | Exercise                                      | Lecture examples     |
| ------ | ------------------------ | --------------------------------------------- | -------------------- |
| 1      | Nodes, topics, CLI       | explore the simulation, drive the robot       | -                    |
| 2      | Packages, pub/sub        | `laser_controller`: stop before obstacles     | `topics/`            |
| 3      | Parameters, launch, RViz | YAML config, one-command bringup              | `params/`, `launch/` |
| 4      | Interfaces, services     | `ObstacleInfo` msg, `SetSpeed` srv            | `services/`          |
| 5      | Actions                  | `RotateToAngle` action server + client        | `actions/`           |
| 6      | TF2, executors           | obstacle in `odom` frame, callback groups     | `tf2/`, `executors/` |
| 7      | Integration, bags, tests | autonomous wander, `pytest`, `launch_testing` | `test/`              |

## Layout

```text
.devcontainer/   Dockerfile + devcontainer.json (ROS 2 Jazzy desktop-full, TurtleBot3, Gazebo)
.vscode/         tasks: simulation, simulation (headless), teleop, build, test
exercises/       module_N.md, one per module: theory bullets, steps, checkpoints, stretch goals
examples/        ros2_examples: minimal runnable demos for the lectures; course_bringup: sim launch file
templates/       turtlebot_py_controller skeleton students copy into src/ in module 2
solutions/       finished turtlebot_py_controller (+ turtlebot_interfaces) after each module
slides/          lecture slides
```

`solutions/` and `templates/` contain `COLCON_IGNORE`, so only `examples/` and `src/` are built. To try a solution:

```bash
mkdir -p src && cp -r solutions/module_4/* src/ && colcon build --symlink-install && source install/setup.bash
```

## Facts about the simulation worth knowing

- Robot: TurtleBot3 *burger*, max 0.22 m/s, 2.84 rad/s.
- `/scan` (`sensor_msgs/LaserScan`, 5 Hz, frame `base_scan`, 360 rays, index 0 = straight ahead),
  `/odom` (50 Hz), `/cmd_vel` is `geometry_msgs/TwistStamped`.
- TF tree: `odom -> base_footprint -> base_link -> base_scan`.
- Nodes: `/robot_state_publisher`, `/ros_gz_bridge` (Gazebo <-> ROS bridge).

## Slides

Lecture slides are plain Markdown rendered with [Marp](https://marp.app), one file per lecture module
in `slides/`; one `---` per slide. Everything runs from `slides/`:

```bash
cd slides
npm ci                           # once
npm run preview                  # live-reload server at http://localhost:8080
npm run build                    # HTML + PDF + PPTX into slides/build/
python3 check_snippets.py        # verify code blocks against the packages; --fix rewrites line ranges
```

In VS Code install the *Marp for VS Code* extension for an inline preview.

| #   | File                                  | Content                                                                 |
| --- | ------------------------------------- | ----------------------------------------------------------------------- |
| 00  | `slides/00-introduction.md`           | Agenda, ROS history, ROS 1 vs ROS 2, distributions                      |
| 01  | `slides/01-basic-concepts.md`         | Nodes, topics, messages, parameters, CLI                                |
| 02  | `slides/02-workspace-and-packages.md` | Workspace, colcon, packages (`ament_python`)                            |
| 03  | `slides/03-rclpy.md`                  | rclpy: node, logging, pub/sub, parameters, launch, executors            |
| 04  | `slides/04-tools.md`                  | Gazebo Harmonic, RViz2, TF2, rqt, rosbag, URDF                          |
| 05  | `slides/05-services-and-actions.md`   | Services, actions, custom interfaces, communication strategies, testing |

Conventions:

- Code is always a fenced block, never a screenshot. Use `bash` for commands the student types,
  `console` for command + output, `python` / `yaml` / `xml` for source.
- Source snippets are copied **verbatim** from the packages in this repo. Every code slide carries an
  HTML comment naming the file and line range, e.g.
  `<!-- src: examples/ros2_examples/ros2_examples/topics/minimal_publisher.py#L13-L27 -->`.
  Methods lifted from inside a class are dedented by a uniform amount; nothing else changes.
  `slides/check_snippets.py` verifies every block (CI runs it on every push).
- Two columns: wrap in `<div class="cols">` with two child `<div>`s
  (`cols wide-left` / `cols wide-right` for 3:2 splits).
- Section dividers: `<!-- _class: divider -->`. Title slide: `<!-- _class: title -->`.
- Per-delivery values (`{{ CITY }}`, `{{ DATE }}`) live on the title slide only.
- Speaker notes go in an HTML comment at the end of the slide.
- A GitHub release builds a merged `ros2-course-jazzy.pdf` plus per-module PPTX and attaches them.

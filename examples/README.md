# Lecture examples

Two packages: `ros2_examples` (the demos below) and `course_bringup` (`sim.launch.py`, the TurtleBot3
simulation with a `gui:=false` switch used by the tasks and by every solution launch file).

One runnable script per concept, no simulation needed. Each file starts with a docstring
saying how to run it and what to check. Built together with the workspace (`colcon build`).

| Topic      | Files                                                                              | Show                                                             |
| ---------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Topics     | `topics/minimal_publisher.py`, `topics/minimal_subscriber.py`                      | node, publisher, timer, subscriber, `ros2 topic echo/hz`         |
| Parameters | `params/params_demo.py`, `config/params.yaml`                                      | declare, YAML, `ros2 param set`, validation callback             |
| Launch     | `launch/params.launch.py`, `launch/pubsub.launch.py`                               | arguments, YAML params, remapping, namespace, condition          |
| Services   | `services/add_two_ints_*.py`                                                       | server, async client, `ros2 service call`                        |
| Actions    | `actions/fibonacci_*.py`                                                           | goal/feedback/result, cancel, `ros2 action send_goal --feedback` |
| TF2        | `tf2/static_broadcaster.py`, `tf2/dynamic_broadcaster.py`, `tf2/frame_listener.py` | static vs dynamic TF, lookup, `tf2_echo`, `view_frames`          |
| Executors  | `executors/blocking_callback_bug.py`, `executors/multithreaded_fix.py`             | single vs multi-threaded executor, callback groups               |
| Testing    | `test/test_pure_logic.py`, `test/test_add_two_ints_launch.py`                      | pytest, launch_testing                                           |

Quick smoke test of everything: `colcon test --packages-select ros2_examples`.

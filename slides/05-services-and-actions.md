---
marp: true
theme: robotari
paginate: true
footer: "Robotari · ROS 2 Course (Jazzy)"
title: "ROS 2 Course – Services and actions"
---

<!-- _class: divider -->

# Services and actions
<small>Request/response communication, long-running tasks, custom interfaces, and choosing between them</small>

---

# ROS 2 Services

<div class="cols">
<div>

- **Request/response** communication model
- Called on demand, not continuously
- A **service server** advertises the service and computes the response
- A **service client** sends a request and waits for the response
- One server per service name; any number of clients
- Good for: queries, configuration, short commands ("reset odometry", "take a picture")

</div>
<div>

![w:520](assets/services.gif)

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Services/Understanding-ROS2-Services.html">docs.ros.org – Understanding services</a></p>

---

# ROS 2 Services – interface

<div class="cols">
<div>

A `.srv` file has two parts separated by `---`: **request** and **response**. Either may be empty.

`example_interfaces/srv/AddTwoInts`
```text
int64 a
int64 b
---
int64 sum
```

`std_srvs/srv/Trigger` – empty request
```text
---
bool success   # indicate successful run of triggered service
string message # informational, e.g. for error messages
```

</div>
<div>

`turtlesim/srv/Spawn`
```text
float32 x
float32 y
float32 theta
string name # Optional.  A unique name will be created and returned if this is empty
---
string name
```

Look up any definition:

```bash
ros2 interface show example_interfaces/srv/AddTwoInts
ros2 interface proto example_interfaces/srv/AddTwoInts
```

</div>
</div>

---

# ROS 2 Services – CLI

<div class="cols">
<div>

List the available services (with their types)
```bash
ros2 service list -t
```

Show the type of a service
```bash
ros2 service type <service_name>
```

Find all services of a type
```bash
ros2 service find <service_type>
```

</div>
<div>

Call a service from the command line
```bash
ros2 service call <service_name> <service_type> '<request>'
```

Example
```bash
ros2 service call /add_two_ints \
  example_interfaces/srv/AddTwoInts "{a: 2, b: 3}"
```

</div>
</div>

---

# ROS 2 Services – example

<style scoped>pre { font-size: 0.7em; }</style>
<div class="cols">
<div>

**Terminal 1** – run the server

```console
$ ros2 run ros2_examples add_two_ints_server
[INFO] [1788371106.349146155] [add_two_ints_server]: 2 + 3 = 5
```

**Terminal 2** – list and inspect

```console
$ ros2 service list -t | grep add_two_ints
/add_two_ints [example_interfaces/srv/AddTwoInts]

$ ros2 interface show example_interfaces/srv/AddTwoInts
int64 a
int64 b
---
int64 sum
```

</div>
<div>

**Terminal 2** – call it

```console
$ ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 2, b: 3}"
requester: making request: example_interfaces.srv.AddTwoInts_Request(a=2, b=3)

response:
example_interfaces.srv.AddTwoInts_Response(sum=5)
```

The request is YAML; use `ros2 interface proto` to get a template.

</div>
</div>

---

# Service server

<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/services/add_two_ints_server.py#L14-L23 -->
```python
class AddTwoIntsServer(Node):

    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.handle_request)

    def handle_request(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'{request.a} + {request.b} = {response.sum}')
        return response      # the response object must be returned
```

</div>
<div>

- `create_service(type, name, callback)`
- The callback receives the request and an empty response object
- Fill the response and **return it** – forgetting the `return` is the classic bug
- Keep it short: the callback blocks the executor (see module 3)

`main` is the usual init / spin / shutdown.

</div>
</div>

---

# Service client

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/services/add_two_ints_client.py#L14-L30 -->
```python
class AddTwoIntsClient(Node):

    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('waiting for /add_two_ints ...')

    def send_request(self, a: int, b: int) -> int:
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        # call_async returns a Future. Never use the blocking `call()` from inside a callback:
        # it would deadlock a single-threaded executor.
        future = self.cli.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        return future.result().sum
```

</div>
<div>

- `create_client(type, name)`; `wait_for_service` before the first call
- Build a `Request`, send it with `call_async` – you get a **Future**
- `spin_until_future_complete` is fine in `main`; inside a callback attach `future.add_done_callback(...)` instead

```console
$ ros2 run ros2_examples add_two_ints_client 4 5
[INFO] [1788371104.831930739] [add_two_ints_client]: Result: 4 + 5 = 9
```

</div>
</div>

---

# ROS 2 Actions

<div class="cols">
<div>

- Designed for **long-running tasks**: navigate to a pose, rotate by an angle, dock
- Three message parts: **goal**, **feedback** during execution, **result** at the end
- Can be **cancelled** by the client
- Built on top of topics and services: a goal service, a result service, a cancel service and a feedback topic – you never see them directly
- The server decides whether to accept a goal

</div>
<div>

![w:520](assets/actions.gif)

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.html">docs.ros.org – Understanding actions</a></p>

---

# ROS 2 Actions – interface

<div class="cols">
<div>

An `.action` file has three parts: **goal**, **result**, **feedback**

`example_interfaces/action/Fibonacci`
```text
# Goal
int32 order
---
# Result
int32[] sequence
---
# Feedback
int32[] sequence
```

</div>
<div>

Goal states seen by the client:

- **accepted** / **rejected** – the server's answer to a new goal
- **executing** – feedback is being published
- **succeeded** – result available
- **canceled** – the client asked to stop, the server complied
- **aborted** – the server gave up

```bash
ros2 interface show example_interfaces/action/Fibonacci
```

</div>
</div>

---

# ROS 2 Actions – CLI

<div class="cols">
<div>

List the available actions (with their types)
```bash
ros2 action list -t
```

Show servers, clients and type of an action
```bash
ros2 action info <action_name>
```

</div>
<div>

Send a goal
```bash
ros2 action send_goal <action_name> <action_type> '<goal>'
```

Send a goal and print the feedback
```bash
ros2 action send_goal /fibonacci \
  example_interfaces/action/Fibonacci "{order: 5}" --feedback
```

</div>
</div>

---

# ROS 2 Actions – example

<style scoped>pre { font-size: 0.62em; }</style>
<div class="cols">
<div>

**Terminal 1** – run the server

```console
$ ros2 run ros2_examples fibonacci_server
[INFO] [1788371116.305528227] [fibonacci_server]: Executing goal, order=5
[INFO] [1788371118.309484013] [fibonacci_server]: Result: [0, 1, 1, 2, 3, 5]
```

**Terminal 2** – list, then send a goal

```console
$ ros2 action list -t
/fibonacci [example_interfaces/action/Fibonacci]

$ ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 5}" --feedback
Waiting for an action server to become available...
Sending goal:
     order: 5

Goal accepted with ID: a6664085d52d4d6d8f1629089e2c9410
```

</div>
<div>

```console
Feedback:
    sequence:
- 0
- 1
- 1

...
Result:
    sequence:
- 0
- 1
- 1
- 2
- 3
- 5

Goal finished with status: SUCCEEDED
```

Press Ctrl+C in Terminal 2 to send a cancel request.

</div>
</div>

---

# Action server – goal and cancel callbacks

<style scoped>pre { font-size: 0.6em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/actions/fibonacci_server.py#L20-L40 -->
```python
def __init__(self):
    super().__init__('fibonacci_server')
    self._server = ActionServer(
        self, Fibonacci, 'fibonacci',
        execute_callback=self.execute,
        goal_callback=self.on_goal,
        cancel_callback=self.on_cancel,
        # Reentrant group + multithreaded executor so cancel requests are
        # processed while `execute` is still running.
        callback_group=ReentrantCallbackGroup(),
    )

def on_goal(self, goal_request) -> GoalResponse:
    if goal_request.order < 0 or goal_request.order > 50:
        self.get_logger().warn(f'Rejecting order {goal_request.order}')
        return GoalResponse.REJECT
    return GoalResponse.ACCEPT

def on_cancel(self, goal_handle) -> CancelResponse:
    self.get_logger().info('Cancel requested')
    return CancelResponse.ACCEPT
```

</div>
<div>

- `ActionServer(node, type, name, execute_callback, ...)`
- `goal_callback` validates the request: **ACCEPT** or **REJECT**
- `cancel_callback` decides whether a cancel request is honoured
- A **reentrant** callback group plus a `MultiThreadedExecutor` in `main` let cancel requests arrive while `execute` is running

</div>
</div>

---

# Action server – execute callback

<style scoped>pre { font-size: 0.66em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/actions/fibonacci_server.py#L42-L61 -->
```python
def execute(self, goal_handle):
    self.get_logger().info(f'Executing goal, order={goal_handle.request.order}')
    feedback = Fibonacci.Feedback()
    feedback.sequence = [0, 1]

    for i in range(1, goal_handle.request.order):
        if goal_handle.is_cancel_requested:
            goal_handle.canceled()
            self.get_logger().info('Goal canceled')
            return Fibonacci.Result(sequence=feedback.sequence)

        feedback.sequence.append(feedback.sequence[i] + feedback.sequence[i - 1])
        goal_handle.publish_feedback(feedback)
        time.sleep(0.5)      # simulate long-running work

    goal_handle.succeed()
    result = Fibonacci.Result()
    result.sequence = feedback.sequence
    self.get_logger().info(f'Result: {list(result.sequence)}')
    return result
```

</div>
<div>

- Runs once per accepted goal; `goal_handle.request` is the goal
- Do the work step by step: check `is_cancel_requested`, publish feedback, continue
- Finish with exactly one of `succeed()`, `canceled()` or `abort()`
- Return the `Result` – it is delivered to the client

</div>
</div>

---

# Action client – send a goal

<style scoped>pre { font-size: 0.7em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/actions/fibonacci_client.py#L15-L27 -->
```python
class FibonacciClient(Node):

    def __init__(self):
        super().__init__('fibonacci_client')
        self._client = ActionClient(self, Fibonacci, 'fibonacci')

    def send_goal(self, order: int):
        self._client.wait_for_server()
        goal = Fibonacci.Goal()
        goal.order = order
        # Step 1: send the goal, wait until the server accepts/rejects it
        send_future = self._client.send_goal_async(goal, feedback_callback=self.on_feedback)
        send_future.add_done_callback(self.on_goal_response)
```

</div>
<div>

- `ActionClient(node, type, name)`; `wait_for_server` before the first goal
- `send_goal_async` returns a Future for the server's accept/reject decision
- The feedback callback is registered when sending the goal
- Everything is asynchronous: register callbacks, then spin

```bash
ros2 run ros2_examples fibonacci_server
ros2 run ros2_examples fibonacci_client 10
```

</div>
</div>

---

# Action client – response, feedback, result

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/actions/fibonacci_client.py#L29-L45 -->
```python
def on_goal_response(self, future):
    goal_handle = future.result()
    if not goal_handle.accepted:
        self.get_logger().error('Goal rejected')
        rclpy.shutdown()
        return
    self.get_logger().info('Goal accepted')
    # Step 2: wait for the result
    goal_handle.get_result_async().add_done_callback(self.on_result)

def on_feedback(self, feedback_msg):
    self.get_logger().info(f'Feedback: {list(feedback_msg.feedback.sequence)}')

def on_result(self, future):
    result = future.result().result
    self.get_logger().info(f'Result: {list(result.sequence)}')
    rclpy.shutdown()
```

</div>
<div>

- Step 2 happens in the goal-response callback: ask the goal handle for the result Future
- `goal_handle.cancel_goal_async()` would request a cancel
- The result callback shuts down; `rclpy.spin` in `main` then returns

```console
$ ros2 run ros2_examples fibonacci_client 5
[INFO] [...] [fibonacci_client]: Goal accepted
[INFO] [...] [fibonacci_client]: Feedback: [0, 1, 1]
[INFO] [...] [fibonacci_client]: Feedback: [0, 1, 1, 2]
[INFO] [...] [fibonacci_client]: Feedback: [0, 1, 1, 2, 3]
[INFO] [...] [fibonacci_client]: Feedback: [0, 1, 1, 2, 3, 5]
[INFO] [...] [fibonacci_client]: Result: [0, 1, 1, 2, 3, 5]
```

</div>
</div>

---

# Custom interfaces

<style scoped>pre { font-size: 0.62em; }</style>
<div class="cols">
<div>

- Prefer standard interfaces (`std_msgs`, `geometry_msgs`, `sensor_msgs`, `std_srvs`, `example_interfaces`) – tools and other nodes already understand them
- When nothing fits, define your own in a dedicated **interface package**
- Interface packages are `ament_cmake`, even in a Python project – the generators are CMake based
- Naming: `PascalCase` files, `snake_case` fields; comments become documentation in `ros2 interface show`

<!-- src: solutions/module_4/turtlebot_interfaces/msg/ObstacleInfo.msg#L1-L5 -->
```text
# Closest obstacle seen by the laser scanner.
std_msgs/Header header
float32 distance        # [m] smallest valid range
float32 angle           # [rad] bearing of that range in the scan frame (0 = straight ahead)
bool blocked            # true if distance < stop_distance
```

</div>
<div>

<!-- src: solutions/module_4/turtlebot_interfaces/srv/SetSpeed.srv#L1-L5 -->
```text
# Change the controller's cruise speed at runtime.
float32 speed           # [m/s]
---
bool success
string message
```

<!-- src: solutions/module_4/turtlebot_interfaces/action/RotateToAngle.action#L1-L7 -->
```text
# Rotate the robot in place by a relative angle (used from module 5 on).
float32 angle            # [rad] relative rotation, positive = counter-clockwise, |angle| <= pi
float32 angular_speed    # [rad/s] > 0, capped by the server
---
float32 final_yaw        # [rad] absolute yaw from odometry when done
---
float32 remaining        # [rad] how much is left
```

</div>
</div>

---

# Custom interfaces – the package

<style scoped>pre { font-size: 0.62em; }</style>
<div class="cols">
<div>

`CMakeLists.txt`

<!-- src: solutions/module_4/turtlebot_interfaces/CMakeLists.txt#L1-L17 -->
```cmake
cmake_minimum_required(VERSION 3.8)
project(turtlebot_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObstacleInfo.msg"
  "srv/SetSpeed.srv"
  "action/RotateToAngle.action"
  DEPENDENCIES std_msgs geometry_msgs
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

</div>
<div>

`package.xml`

<!-- src: solutions/module_4/turtlebot_interfaces/package.xml#L10-L17 -->
```xml
  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <depend>std_msgs</depend>
  <depend>geometry_msgs</depend>

  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>
```

```bash
ros2 pkg create --build-type ament_cmake turtlebot_interfaces \
  --dependencies std_msgs geometry_msgs
colcon build --packages-select turtlebot_interfaces
source install/setup.bash        # in every terminal!
ros2 interface show turtlebot_interfaces/srv/SetSpeed
```

Python code then imports them like any other interface: `from turtlebot_interfaces.srv import SetSpeed`

</div>
</div>

---

# Communication strategies

| | Topics | Services | Actions |
|---|---|---|---|
| Pattern | publish / subscribe | request / response | goal / feedback / result |
| Direction | one-way, many-to-many | two-way, one server | two-way, one server |
| Duration | continuous stream | short, returns at once | long, seconds to minutes |
| Cancel | – | – | yes |
| Progress | – | – | feedback topic |
| Use for | sensor data, robot state, commands at a rate | queries, configuration, quick triggers | navigation, manipulation, docking, calibration |

- **Default to topics.** Reach for a service when you need an answer; for an action when the work takes time and may be interrupted
- Never block a callback waiting for a service or action – use the async API or a separate callback group
- Own a topic's contract: message type, frame, rate and QoS

---

# Testing your nodes

<style scoped>pre { font-size: 0.66em; }</style>
<div class="cols">
<div>

Keep logic out of callbacks and test it with plain **pytest** – no ROS runtime needed:

<!-- src: examples/ros2_examples/test/test_pure_logic.py#L8-L17 -->
```python
from ros2_examples.tf2.static_broadcaster import quaternion_from_yaw


def test_zero_yaw_is_identity():
    assert quaternion_from_yaw(0.0) == (0.0, 0.0, 0.0, 1.0)


def test_quaternion_is_unit_length():
    x, y, z, w = quaternion_from_yaw(1.234)
    assert math.isclose(x * x + y * y + z * z + w * w, 1.0, abs_tol=1e-9)
```

```bash
colcon test --packages-select ros2_examples
colcon test-result --verbose
```

</div>
<div>

Integration tests with **launch_testing**: start real nodes, talk to them through ROS:

<!-- src: examples/ros2_examples/test/test_add_two_ints_launch.py#L37-L43 -->
```python
def test_sum(self):
    client = self.node.create_client(AddTwoInts, 'add_two_ints')
    self.assertTrue(client.wait_for_service(timeout_sec=10.0), 'service not available')
    future = client.call_async(AddTwoInts.Request(a=20, b=22))
    rclpy.spin_until_future_complete(self.node, future, timeout_sec=5.0)
    self.assertIsNotNone(future.result())
    self.assertEqual(future.result().sum, 42)
```

- `generate_test_description()` launches the server under test
- The test class creates its own node and calls the service like any client
- Both kinds are run by `colcon test`

</div>
</div>

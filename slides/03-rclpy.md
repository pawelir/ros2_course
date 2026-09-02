---
marp: true
theme: robotari
paginate: true
footer: "Robotari · ROS 2 Course (Jazzy)"
title: "ROS 2 Course – rclpy"
---

<!-- _class: divider -->

# ROS 2 Python client library (rclpy)
<small>Writing nodes: init and spin, logging, publishers and subscribers, parameters, launch, executors</small>

---

# Client libraries

<div class="cols wide-left">
<div>

- `rclpy` (Python) and `rclcpp` (C++) sit on the same C library, `rcl`
- Same concepts and almost the same API – every pattern shown here has a 1:1 C++ counterpart
- Everything is built on the `Node` class:
  - `create_publisher`, `create_subscription`, `create_timer`
  - `create_service`, `create_client`, `ActionServer`, `ActionClient`
  - `declare_parameter`, `get_parameter`
  - `get_logger`, `get_clock`
- An **executor** runs the callbacks – `rclpy.spin(node)` is the default one

</div>
<div>

The examples in this module are in `examples/ros2_examples` and run without the simulation:

```bash
ros2 run ros2_examples minimal_publisher
ros2 run ros2_examples params_demo
ros2 launch ros2_examples pubsub.launch.py
```

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/p/rclpy/">docs.ros.org – rclpy API</a></p>

---

# Init and spin

<div class="cols">
<div>

<!-- src: examples/ros2_examples/ros2_examples/topics/minimal_publisher.py#L30-L42 -->
```python
def main(args=None):
    rclpy.init(args=args)
    node = MinimalPublisher()
    try:
        rclpy.spin(node)          # blocks; runs callbacks until Ctrl+C
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
```

</div>
<div>

1. `rclpy.init` – initialise the client library, parse `--ros-args`
2. Create the node instance
3. `rclpy.spin` – process callbacks until shutdown or Ctrl+C
4. Shut down. `ExternalShutdownException` is how `ros2 launch` stops a node

Every node in the course follows this skeleton – only the class in step 2 changes.

`main` is what `console_scripts` in `setup.py` points at.

</div>
</div>

---

# Logging

<div class="cols">
<div>

- Use the node's logger, never `print`: logs are timestamped, carry the node name, and are also published on `/rosout`
- Severities: `debug`, `info`, `warn`, `error`, `fatal`
- Variants: `throttle_duration_sec`, `once=True`, `skip_first=True`

Throttling in a high-rate callback:

<!-- src: solutions/module_2/turtlebot_py_controller/turtlebot_py_controller/laser_controller.py#L42-L45 -->
```python
# throttle_duration_sec avoids flooding the terminal at scan rate
self.get_logger().info(
    f'closest obstacle: {closest:.2f} m -> {"STOP" if blocked else "go"}',
    throttle_duration_sec=1.0)
```

</div>
<div>

```console
$ ros2 run ros2_examples minimal_publisher
[INFO] [1788371141.613206927] [minimal_publisher]: Publishing: "Hello ROS 2: 0"
[INFO] [1788371142.103044878] [minimal_publisher]: Publishing: "Hello ROS 2: 1"
[INFO] [1788371142.603131682] [minimal_publisher]: Publishing: "Hello ROS 2: 2"
```

Change the level without touching code:

```bash
ros2 run ros2_examples minimal_publisher \
  --ros-args --log-level minimal_publisher:=debug
```

Browse all nodes' logs in `rqt_console` (module 4).

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Logging.html">docs.ros.org – About logging</a></p>

---

# Topic publisher

<style scoped>pre { font-size: 0.7em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/topics/minimal_publisher.py#L7-L27 -->
```python
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        # (msg type, topic name, queue size)
        self.publisher_ = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS 2: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1
```

</div>
<div>

- Import `rclpy`, `Node` and the message type
- The node is a class inheriting from `Node`; the constructor sets the node name
- `create_publisher(type, topic, queue size)`
- `create_timer(period in s, callback)` – the only way to "loop" in a node
- The callback fills a message and publishes it
- Nothing runs until `rclpy.spin` in `main`

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html">docs.ros.org – Simple publisher and subscriber (Python)</a></p>

---

# Topic subscriber

<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/topics/minimal_subscriber.py#L7-L21 -->
```python
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String, 'chatter', self.listener_callback, 10)

    def listener_callback(self, msg: String):
        self.get_logger().info(f'I heard: "{msg.data}"')
```

</div>
<div>

- `create_subscription(type, topic, callback, queue size)`
- The callback receives one message object; fields match `ros2 interface show`
- Keep the returned subscription in `self.` – otherwise it is garbage-collected and nothing arrives
- Callbacks must be quick: the executor runs them one at a time

</div>
</div>

<div class="note">

Try it: run `minimal_subscriber` in one terminal, then `ros2 topic pub /chatter std_msgs/msg/String "{data: hi}"` in another.

</div>

---

# Your task in module 2

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: templates/turtlebot_py_controller/turtlebot_py_controller/laser_controller.py#L12-L25 -->
```python
class LaserController(Node):

    def __init__(self):
        super().__init__('laser_controller')
        # TODO: create a subscription to /scan (queue size 10) with self.on_scan as callback
        # TODO: create a publisher of TwistStamped on /cmd_vel
        self.get_logger().info('laser_controller started')

    def on_scan(self, msg):
        # TODO: compute the smallest *valid* distance in msg.ranges
        #       (ignore inf/nan and values outside [range_min, range_max])
        # TODO: log it
        # TODO: publish forward velocity, or zero if the obstacle is closer than 0.5 m
        pass
```

</div>
<div>

The template in `templates/turtlebot_py_controller` combines everything so far:

- a subscriber to the LiDAR (`sensor_msgs/msg/LaserScan`)
- a publisher of velocity commands (`geometry_msgs/msg/TwistStamped`)
- logging of the closest obstacle

Inspect the message before coding:

```bash
ros2 interface show sensor_msgs/msg/LaserScan
```

</div>
</div>

<!--
Jazzy TurtleBot3 listens to TwistStamped on /cmd_vel (Twist in Humble).
The reference solution lives in solutions/module_2 – don't show it before the lab.
-->

---

# Parameters – declare and read

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/params/params_demo.py#L18-L35 -->
```python
class ParamsDemo(Node):

    def __init__(self):
        super().__init__('params_demo')

        # Declaring gives the parameter a type and a default. Undeclared params are rejected.
        self.declare_parameter('greeting', 'Hello')
        self.declare_parameter(
            'rate_hz', 1.0,
            ParameterDescriptor(description='Timer frequency in Hz, must be > 0'))
        self.declare_parameter('names', ['world'])

        # Read once at startup
        rate = self.get_parameter('rate_hz').value
        self.timer = self.create_timer(1.0 / rate, self.tick)

        # Called *before* a parameter is changed; return successful=False to reject.
        self.add_on_set_parameters_callback(self.validate_params)
```

</div>
<div>

- `declare_parameter(name, default)` – the default fixes the **type**
- Optional `ParameterDescriptor` shows up in `ros2 param describe`
- `get_parameter(name).value` – read it where you need it
- Values come from, in order of priority: code default → YAML file → `--ros-args -p` / launch

Reading in every callback makes `ros2 param set` take effect immediately.

</div>
</div>

---

# Parameters – validate changes

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/params/params_demo.py#L37-L51 -->
```python
def validate_params(self, params: list[Parameter]) -> SetParametersResult:
    for p in params:
        if p.name == 'rate_hz':
            if p.value <= 0.0:
                return SetParametersResult(successful=False, reason='rate_hz must be > 0')
            # Re-create the timer with the new period
            self.timer.cancel()
            self.timer = self.create_timer(1.0 / p.value, self.tick)
    return SetParametersResult(successful=True)

def tick(self):
    # Reading every tick means `ros2 param set greeting` takes effect immediately.
    greeting = self.get_parameter('greeting').value
    names = self.get_parameter('names').value
    self.get_logger().info(f'{greeting}, {", ".join(names)}!')
```

</div>
<div>

- The callback runs **before** the value is stored
- Return `successful=False` with a reason to reject the change
- This is also the place to react: here the timer is re-created with the new period

```console
$ ros2 param set /params_demo rate_hz -1.0
Setting parameter failed: rate_hz must be > 0
```

</div>
</div>

---

# Parameters – YAML files

<div class="cols">
<div>

Parameter file: node name → `ros__parameters` → values

<!-- src: examples/ros2_examples/config/params.yaml#L1-L6 -->
```yaml
# Node name -> ros__parameters -> values. Loaded by params.launch.py.
params_demo:
  ros__parameters:
    greeting: "Good morning"
    rate_hz: 2.0
    names: ["Alice", "Bob"]
```

Types must match the declared defaults: `2.0` is a double, `2` would be rejected for `rate_hz`.

</div>
<div>

Pass parameters on the command line…

```bash
ros2 run ros2_examples params_demo \
  --ros-args -p rate_hz:=5.0 -p greeting:=Hi
```

…or from a file

```bash
ros2 run ros2_examples params_demo \
  --ros-args --params-file config/params.yaml
```

Dump the current values in the same format

```bash
ros2 param dump /params_demo
```

</div>
</div>

---

# Launch

<div class="cols">
<div>

- One command starts and configures a whole system: many nodes, their parameters, remappings and namespaces
- Written in **Python** (most flexible), XML or YAML
- Launch files can include other launch files – the simulation, the robot driver, your nodes
- Installed to `share/<package>/launch` via `data_files` in `setup.py`

</div>
<div>

Run a launch file
```bash
ros2 launch <package_name> <file.launch.py>
```

Show its arguments
```bash
ros2 launch <package_name> <file.launch.py> --show-args
```

Set an argument
```bash
ros2 launch ros2_examples params.launch.py greeting:=Hey
```

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Launch/Launch-Main.html">docs.ros.org – Launch</a></p>

---

# Launch – arguments and parameters

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/launch/params.launch.py#L16-L33 -->
```python
def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('ros2_examples'), 'config', 'params.yaml')

    greeting_arg = DeclareLaunchArgument(
        'greeting', default_value='Hello from launch',
        description='Overrides the greeting parameter from the YAML file')

    node = Node(
        package='ros2_examples',
        executable='params_demo',
        name='params_demo',
        output='screen',
        # Later entries win: the launch argument overrides the YAML value.
        parameters=[config, {'greeting': LaunchConfiguration('greeting')}],
    )

    return LaunchDescription([greeting_arg, node])
```

</div>
<div>

- `generate_launch_description()` is the entry point ROS looks for
- `get_package_share_directory` finds installed files – never hard-code paths
- `DeclareLaunchArgument` + `LaunchConfiguration` expose a `name:=value` option
- `Node(...)` describes one process: package, executable, name, parameters
- `parameters=[...]` mixes YAML files and dicts; later entries win

</div>
</div>

---

# Launch – namespaces, remapping, conditions

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/launch/pubsub.launch.py#L15-L29 -->
```python
def generate_launch_description():
    with_listener = DeclareLaunchArgument('with_listener', default_value='true')

    talker = Node(
        package='ros2_examples', executable='minimal_publisher',
        namespace='demo', name='talker', output='screen',
        remappings=[('chatter', 'greetings')],
    )
    listener = Node(
        package='ros2_examples', executable='minimal_subscriber',
        namespace='demo', name='listener', output='screen',
        remappings=[('chatter', 'greetings')],
        condition=IfCondition(LaunchConfiguration('with_listener')),
    )
    return LaunchDescription([with_listener, talker, listener])
```

</div>
<div>

- `namespace` prefixes node and topic names: `/demo/talker`, `/demo/greetings`
- `remappings` renames a topic without changing code – the same node can be reused
- `condition` starts a node only when the argument is true

```bash
ros2 launch ros2_examples pubsub.launch.py
ros2 topic list       # /demo/greetings
ros2 launch ros2_examples pubsub.launch.py with_listener:=false
```

</div>
</div>

---

# Executors – the problem

<style scoped>pre { font-size: 0.7em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/executors/blocking_callback_bug.py#L19-L33 -->
```python
class BlockingNode(Node):

    def __init__(self):
        super().__init__('blocking_node')
        self.create_timer(0.5, self.heartbeat)
        self.create_service(AddTwoInts, 'slow_add', self.slow_add)

    def heartbeat(self):
        self.get_logger().info('heartbeat')

    def slow_add(self, request, response):
        self.get_logger().info('slow_add: working for 3 s ...')
        time.sleep(3.0)                       # blocks the whole executor
        response.sum = request.a + request.b
        return response
```

</div>
<div>

- `rclpy.spin` uses a **SingleThreadedExecutor**: one callback at a time
- Anything that blocks – `time.sleep`, a long computation, a blocking service call – stalls every other callback of the node

```bash
ros2 run ros2_examples blocking_callback_bug
ros2 service call /slow_add \
  example_interfaces/srv/AddTwoInts "{a: 1, b: 2}"
```

The heartbeat log stops for 3 s.

</div>
</div>

---

# Executors – the fix

<style scoped>pre { font-size: 0.66em; }</style>
<div class="cols wide-left">
<div>

<!-- src: examples/ros2_examples/ros2_examples/executors/multithreaded_fix.py#L24-L30 -->
```python
def __init__(self):
    super().__init__('non_blocking_node')
    self.fast_group = MutuallyExclusiveCallbackGroup()
    self.slow_group = MutuallyExclusiveCallbackGroup()

    self.create_timer(0.5, self.heartbeat, callback_group=self.fast_group)
    self.create_service(AddTwoInts, 'slow_add', self.slow_add, callback_group=self.slow_group)
```

<!-- src: examples/ros2_examples/ros2_examples/executors/multithreaded_fix.py#L42-L48 -->
```python
def main(args=None):
    rclpy.init(args=args)
    node = NonBlockingNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
```

</div>
<div>

- **MultiThreadedExecutor** runs callbacks from different groups in parallel
- `MutuallyExclusiveCallbackGroup` – callbacks in the group never overlap; safe to share state without locks (the node default)
- `ReentrantCallbackGroup` – callbacks may run in parallel, even with themselves
- Put the slow work in its own group so it cannot block the rest

Now the heartbeat keeps ticking while `slow_add` sleeps.

</div>
</div>

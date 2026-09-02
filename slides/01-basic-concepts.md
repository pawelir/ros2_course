---
marp: true
theme: robotari
paginate: true
footer: "Robotari · ROS 2 Course (Jazzy)"
title: "ROS 2 Course – Basic concepts"
---

<!-- _class: divider -->

# ROS 2 basic concepts
<small>How a ROS 2 system works, and how to work with it from the command line</small>

---

# Philosophy

- **Peer-to-peer** – nodes run and communicate independently; there is no central master
- **Distributed** – processes on different machines communicate over the network
- **Multi-lingual** – first-class C++ (`rclcpp`) and Python (`rclpy`); community clients for Rust and others
- **Lightweight** – ROS is a thin layer; algorithms live in standalone libraries wrapped by ROS interfaces
- **Open source** – the core and most of the ecosystem are Apache 2.0 / BSD licensed

---

# Architecture

<div class="cols wide-right">
<div>

- **User code** – your nodes
- **Client library** – `rclcpp`, `rclpy`, on the common `rcl` C library
- **RMW** – middleware interface; abstracts the transport
- **Middleware** – DDS (Fast DDS, Cyclone, Connext) or Zenoh
- **OS** – Linux, Windows, RHEL

Swap the middleware without touching code:

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

</div>
<div>

![w:520 center](assets/ros2-architecture.jpg)

</div>
</div>

<!--
Note: Jazzy's default RMW is Fast DDS. Zenoh (rmw_zenoh_cpp) became a Tier 1
option in Kilted; still worth mentioning here as the direction of travel.
-->

---

# Installation and environment

Install on Ubuntu 24.04 from the ROS 2 apt repository
[docs.ros.org/en/jazzy/Installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

```bash
source /opt/ros/jazzy/setup.bash                        # this shell only
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc    # every new shell
printenv | grep -i ROS                                  # check
```

```console
ROS_VERSION=2
ROS_PYTHON_VERSION=3
ROS_DISTRO=jazzy
ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET
```

<div class="note">

`ROS_LOCALHOST_ONLY` is deprecated since Jazzy – use `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` instead. `ROS_DOMAIN_ID` separates groups of machines sharing a network.

</div>

---

# ROS 2 Nodes

<div class="cols">
<div>

- A node is a single-purpose executable
- Nodes are organised in packages
- Nodes communicate with each other through topics, services and actions
- One process can host many nodes

</div>
<div>

![w:520](assets/nodes.gif)

</div>
</div>

<p class="ref">Reference: <a href="https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html">docs.ros.org – Understanding nodes</a></p>

---

# ROS 2 Nodes – CLI

Run an executable from a package
```bash
ros2 run <package_name> <executable_name>
```

List all active nodes
```bash
ros2 node list
```

Show information about a node
```bash
ros2 node info <node_name>
```

---

# ROS 2 Nodes – example

<style scoped>pre { font-size: 0.68em; }</style>
<div class="cols">
<div>

**Terminal 1** – run the minimal publisher

```console
$ ros2 run examples_rclcpp_minimal_publisher publisher_member_function
[INFO] [1716061633.169] [minimal_publisher]: Publishing: 'Hello, world! 0'
[INFO] [1716061633.669] [minimal_publisher]: Publishing: 'Hello, world! 1'
[INFO] [1716061634.169] [minimal_publisher]: Publishing: 'Hello, world! 2'
```

**Terminal 2** – list active nodes

```console
$ ros2 node list
/minimal_publisher
```

</div>
<div>

**Terminal 2** – inspect the node

```console
$ ros2 node info /minimal_publisher
/minimal_publisher
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /topic: std_msgs/msg/String
  Service Servers:
    /minimal_publisher/describe_parameters: ...
    /minimal_publisher/get_parameters: ...
    /minimal_publisher/set_parameters: ...
  Service Clients:
  Action Servers:
  Action Clients:
```

</div>
</div>

---

# ROS 2 Topics

<div class="cols">
<div>

- The basic communication mechanism between nodes
- A topic is a named channel for a stream of messages
- Publish/subscribe, one-way, asynchronous
- Many publishers and many subscribers per topic
- Ideal for continuous data: sensor readings, robot state

</div>
<div>

![w:520](assets/topics.gif)

</div>
</div>

---

# ROS 2 Topics – CLI

<div class="cols">
<div>

List all active topics
```bash
ros2 topic list
```

Show type, publisher and subscriber count
```bash
ros2 topic info <topic_name>
```

Print the messages being published
```bash
ros2 topic echo <topic_name>
```

</div>
<div>

Publish a message from the command line
```bash
ros2 topic pub <topic_name> <msg_type> '<args>'
```

Measure the publishing rate
```bash
ros2 topic hz <topic_name>
```

Show verbose QoS information
```bash
ros2 topic info -v <topic_name>
```

</div>
</div>

---

# ROS 2 Topics – example

With `minimal_publisher` running in Terminal 1:

<div class="cols">
<div>

```console
$ ros2 topic list
/parameter_events
/rosout
/topic

$ ros2 topic info /topic
Type: std_msgs/msg/String
Publisher count: 1
Subscription count: 0

$ ros2 topic echo /topic
data: Hello, world! 1507
---
data: Hello, world! 1508
---
```

</div>
<div>

```console
$ ros2 topic pub /topic std_msgs/msg/String \
    "data: 'My own message'"
publisher: beginning loop
publishing #1: std_msgs.msg.String(data='My own message')
publishing #2: std_msgs.msg.String(data='My own message')

$ ros2 topic hz /topic
average rate: 2.000
    min: 0.500s max: 0.500s std dev: 0.00008s window: 4
```

</div>
</div>

---

# ROS 2 Messages

<div class="cols">
<div>

- A message is the data structure carried by a topic
- Composed of primitive fields (`int32`, `float64`, `string`, arrays…) and other messages
- Large libraries of standard messages: `std_msgs`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`
- You can define your own in a package

</div>
<div>

`geometry_msgs/msg/Vector3`
```text
float64 x
float64 y
float64 z
```

`geometry_msgs/msg/Twist`
```text
Vector3 linear
Vector3 angular
```

</div>
</div>

---

# ROS 2 Messages – CLI

List all installed interfaces (messages, services, actions)
```bash
ros2 interface list
```

Show an interface definition
```bash
ros2 interface show <package_name>/<interface_type>/<interface_name>
```

Show a prototype you can paste into `ros2 topic pub`
```bash
ros2 interface proto <package_name>/<interface_type>/<interface_name>
```

---

# ROS 2 Messages – example

<style scoped>pre { font-size: 0.7em; }</style>
<div class="cols">
<div>

```console
$ ros2 interface list | grep geometry_msgs/msg
    geometry_msgs/msg/Accel
    geometry_msgs/msg/Pose
    geometry_msgs/msg/Twist
    geometry_msgs/msg/Vector3
    ...

$ ros2 interface show geometry_msgs/msg/Twist
# This expresses velocity in free space
# broken into its linear and angular parts.

Vector3  linear
        float64 x
        float64 y
        float64 z
Vector3  angular
        float64 x
        float64 y
        float64 z
```

</div>
<div>

```console
$ ros2 interface proto geometry_msgs/msg/Twist
"linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0
"
```

Combine with `ros2 topic pub`:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.5}}"
```

</div>
</div>

---

# ROS 2 Parameters

<div class="cols">
<div>

- Belong to an individual node
- Configure a node without changing code
- Can be changed at runtime (the node decides whether to accept)
- Typed: bool, int, double, string, and arrays of those
- Set from launch files or YAML config files

</div>
<div>

`turtlesim` parameters as YAML

```yaml
/turtlesim:
  ros__parameters:
    background_b: 255
    background_g: 86
    background_r: 150
    use_sim_time: false
```

Load at startup:
```bash
ros2 run turtlesim turtlesim_node \
  --ros-args --params-file turtlesim.yaml
```

</div>
</div>

---

# ROS 2 Parameters – CLI

<div class="cols">
<div>

List parameters of all nodes
```bash
ros2 param list
```

List parameters of one node
```bash
ros2 param list <node_name>
```

Get a value
```bash
ros2 param get <node_name> <parameter_name>
```

</div>
<div>

Set a value
```bash
ros2 param set <node_name> <parameter_name> <value>
```

Dump all parameters of a node to YAML
```bash
ros2 param dump <node_name>
```

Load parameters from a YAML file
```bash
ros2 param load <node_name> <file.yaml>
```

</div>
</div>

---

# ROS 2 Parameters – example

<style scoped>pre { font-size: 0.64em; }</style>
With `ros2 run turtlesim turtlesim_node` running in Terminal 1. The window turns green the moment the parameter is set – no restart needed.

```console
$ ros2 param list /turtlesim
  background_b
  background_g
  background_r
  qos_overrides./parameter_events.publisher.depth
  qos_overrides./parameter_events.publisher.reliability
  ...
  use_sim_time

$ ros2 param get /turtlesim background_b
Integer value is: 255

$ ros2 param set /turtlesim background_b 100
Set parameter successful

$ ros2 param get /turtlesim background_b
Integer value is: 100
```

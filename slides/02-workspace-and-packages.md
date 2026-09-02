---
marp: true
theme: robotari
paginate: true
footer: "Robotari · ROS 2 Course (Jazzy)"
title: "ROS 2 Course – Workspace and packages"
---

<!-- _class: divider -->

# Workspace and packages
<small>Where the code lives, how colcon builds it, and what a package is made of</small>

---

# ROS 2 workspace

<div class="cols">
<div>

A workspace is a directory with a fixed layout, managed by `colcon`:

- **src** – source code of your packages. The only directory you edit
- **build** – intermediate files of the build
- **install** – the result: executables, launch files, configs, `setup.bash`
- **log** – output of every colcon invocation

</div>
<div>

```text
ros2_ws/
├── src/
│   ├── ros2_examples/
│   └── turtlebot_py_controller/
├── build/
├── install/
│   └── setup.bash
└── log/
```

</div>
</div>

<div class="note">

`build/`, `install/` and `log/` are generated – never commit them. Deleting them and rebuilding is the standard way to fix a broken build.

</div>

---

# ROS 2 workspace – CLI

Create a workspace and add packages to `src`
```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/<user>/<repository>.git
```

Install the system dependencies declared in the packages' `package.xml`
```bash
cd ~/ros2_ws
rosdep install -i --from-path src --rosdistro jazzy -y
```

Source the **underlay** (ROS installation) and then your **overlay** (this workspace)
```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

---

# Course workspace

<div class="cols">
<div>

The dev container is a ready workspace at `/workspaces/ros2_course`

- `examples/` is built automatically
- `templates/` and `solutions/` carry a `COLCON_IGNORE` file – colcon skips them
- Your own packages go to `src/`

Start module 2 by copying the template:

<!-- src: templates/turtlebot_py_controller/README.md#L6-L6 -->
```bash
cp -r /workspaces/ros2_course/templates/turtlebot_py_controller /workspaces/ros2_course/src/
```

</div>
<div>

What the container adds to every new shell:

<!-- src: .devcontainer/post_create.sh#L10-L12 -->
```bash
source /opt/ros/jazzy/setup.bash
[ -f /workspaces/ros2_course/install/setup.bash ] && source /workspaces/ros2_course/install/setup.bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash 2>/dev/null || true
```

Underlay first, overlay second – always in that order.

</div>
</div>

---

# colcon build system

<div class="cols">
<div>

- Command-line tool that builds all packages found under `src/`
- Resolves the build order from the dependencies in `package.xml`
- Supports several build types: `ament_python`, `ament_cmake`, plain `cmake`
- Runs the tests and collects the results
- Creates the `build/`, `install/`, `log/` layout

</div>
<div>

<div class="note">

**Always run colcon from the root of the workspace**, never from inside `src/` or a package.

</div>

```console
$ cd /workspaces/ros2_course && colcon build --symlink-install
Starting >>> ros2_examples
Finished <<< ros2_examples [0.93s]

Summary: 1 package finished [1.02s]
```

</div>
</div>

<p class="ref">Reference: <a href="https://colcon.readthedocs.io">colcon.readthedocs.io</a></p>

---

# colcon – CLI

<div class="cols">
<div>

Build every package in the workspace
```bash
colcon build
```

Build one package only
```bash
colcon build --packages-select <package_name>
```

Build a package and everything it depends on
```bash
colcon build --packages-up-to <package_name>
```

</div>
<div>

Symlink instead of copying: edit Python and launch files without rebuilding
```bash
colcon build --symlink-install
```

Run the tests and show the results
```bash
colcon test && colcon test-result --verbose
```

List the packages colcon can see
```bash
colcon list
```

</div>
</div>

<div class="note">

After a build, `source install/setup.bash` in every terminal that should see the new packages. New executables or data files require a rebuild even with `--symlink-install`.

</div>

---

# ROS 2 package

<div class="cols wide-left">
<div>

- The organisational unit of ROS 2 code: one node or a family of related nodes
- Unit of installing, sharing and releasing code
- Two flavours: **ament_python** (this course) and **ament_cmake** (C++)

A Python package contains:

- `package.xml` – metadata and dependencies
- `setup.py`, `setup.cfg` – how to install it
- `<package_name>/` – the Python module with your nodes
- `resource/<package_name>` – marker file for the ROS index
- `launch/`, `config/`, `rviz/`, `test/` – by convention

</div>
<div>

```text
turtlebot_py_controller/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── turtlebot_py_controller
├── turtlebot_py_controller/
│   ├── __init__.py
│   └── laser_controller.py
├── launch/
├── config/
└── rviz/
```

</div>
</div>

---

# ROS 2 package – package.xml

<style scoped>pre { font-size: 0.58em; }</style>
<div class="cols wide-left">
<div>

<!-- src: templates/turtlebot_py_controller/package.xml#L3-L27 -->
```xml
<package format="3">
  <name>turtlebot_py_controller</name>
  <version>0.1.0</version>
  <description>Course package: laser-based TurtleBot3 controller, built up module by module.</description>
  <maintainer email="student@example.com">student</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>std_srvs</depend>
  <depend>tf2_ros</depend>

  <exec_depend>turtlebot3_gazebo</exec_depend>
  <exec_depend>rviz2</exec_depend>

  <test_depend>python3-pytest</test_depend>
  <test_depend>launch_testing</test_depend>
  <test_depend>launch_testing_ros</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

</div>
<div>

Basic properties

- name, version, description
- maintainer, license

Dependencies

- `depend` – needed to build and to run
- `exec_depend` – only at run time
- `test_depend` – only for tests

`rosdep` reads these and installs the matching apt packages

The `build_type` tells colcon how to build

</div>
</div>

---

# ROS 2 package – setup.py

<style scoped>pre { font-size: 0.66em; }</style>
<div class="cols wide-left">
<div>

Install launch files, configs and RViz layouts into `share/<package>`:

<!-- src: templates/turtlebot_py_controller/setup.py#L12-L18 -->
```python
data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
],
```

Register executables: `<executable> = <module>:<function>`

<!-- src: examples/ros2_examples/setup.py#L25-L29 -->
```python
entry_points={
    'console_scripts': [
        # topics
        'minimal_publisher = ros2_examples.topics.minimal_publisher:main',
        'minimal_subscriber = ros2_examples.topics.minimal_subscriber:main',
```

</div>
<div>

- Standard Python `setuptools`; ROS only adds conventions
- Anything not listed in `data_files` is **not installed** – a missing launch file is usually this
- Each `console_scripts` entry becomes a `ros2 run` executable

`setup.cfg` puts the scripts where `ros2 run` looks:

<!-- src: examples/ros2_examples/setup.cfg#L1-L4 -->
```ini
[develop]
script_dir=$base/lib/ros2_examples
[install]
install_scripts=$base/lib/ros2_examples
```

</div>
</div>

---

# ROS 2 package – CLI

<div class="cols">
<div>

Create a new package (run inside `src/`)
```bash
ros2 pkg create <package_name> --build-type ament_python \
  --license Apache-2.0 --dependencies rclpy sensor_msgs
```

`--node-name <name>` also generates a first node and its `console_scripts` entry

List installed packages
```bash
ros2 pkg list
```

</div>
<div>

Show the `package.xml` of a package
```bash
ros2 pkg xml <package_name>
```

List the executables of a package
```bash
ros2 pkg executables <package_name>
```

Show where a package is installed
```bash
ros2 pkg prefix <package_name>
```

</div>
</div>

---

# ROS 2 package – example

<style scoped>pre { font-size: 0.62em; }</style>
<div class="cols">
<div>

```console
$ cd /workspaces/ros2_course/src
$ ros2 pkg create my_package --build-type ament_python \
    --license Apache-2.0 --dependencies rclpy sensor_msgs
package name: my_package
package format: 3
version: 0.0.0
description: TODO: Package description
maintainer: ['pawel <pawel@example.com>']
licenses: ['Apache-2.0']
build type: ament_python
dependencies: ['rclpy', 'sensor_msgs']
creating folder ./my_package
creating ./my_package/package.xml
creating source folder
creating folder ./my_package/my_package
creating ./my_package/setup.py
creating ./my_package/setup.cfg
...
```

</div>
<div>

The generated skeleton:

```console
$ find my_package -type f | sort
my_package/LICENSE
my_package/my_package/__init__.py
my_package/package.xml
my_package/resource/my_package
my_package/setup.cfg
my_package/setup.py
my_package/test/test_copyright.py
my_package/test/test_flake8.py
my_package/test/test_pep257.py
```

Then add your node to `my_package/`, register it in `setup.py` and build:

```bash
cd /workspaces/ros2_course
colcon build --symlink-install --packages-select my_package
source install/setup.bash
ros2 pkg executables my_package
```

</div>
</div>

---

# From source to `ros2 run`

<div class="cols wide-left">
<div>

The loop you will repeat all course long:

1. Edit code in `src/<package>/`
2. `colcon build --symlink-install` from the workspace root
3. `source install/setup.bash` in every terminal that runs the code
4. `ros2 run <package> <executable>` or `ros2 launch <package> <file>`

With `--symlink-install`, step 2 can be skipped after editing an existing Python or launch file – the installed file is a link to your source.

</div>
<div>

**Common pitfalls**

- *"Package not found"* – you did not source `install/setup.bash`, or the build failed
- *"No executable found"* – missing entry in `console_scripts`
- Launch file not found – missing `data_files` entry in `setup.py`
- Building from inside `src/` – colcon creates a second workspace there

</div>
</div>

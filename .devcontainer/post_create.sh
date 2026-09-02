#!/usr/bin/env bash
# Runs once after the container is created: sets up shell sourcing and builds the examples.
set -e

WS=/workspaces/ros2_course

cat >> ~/.bashrc <<'BASHRC'

# --- ROS 2 course ---
source /opt/ros/jazzy/setup.bash
[ -f /workspaces/ros2_course/install/setup.bash ] && source /workspaces/ros2_course/install/setup.bash
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash 2>/dev/null || true
BASHRC

source /opt/ros/jazzy/setup.bash
cd "$WS"
# Only packages under examples/ are built; solutions/ and templates/ carry COLCON_IGNORE.
colcon build --symlink-install
echo "Done. Open a new terminal, then run the 'simulation' task (Ctrl+Shift+P -> Tasks: Run Task)."

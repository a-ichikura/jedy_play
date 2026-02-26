# jedy_play (external)

`jedy_play` (external branch) provides a **Python Robot Interface** for the Jedy robot.
It is intended to be imported by higher-level orchestration packages (e.g., `techrie_demo`) to send joint trajectories to the robot.

## What this package provides

- `jedy_play.jedy_interface.IJedyROSRobotInterface`
  - Subclass of `kxr_controller.kxr_interface.KXRROSRobotInterface`
  - Defines controller dictionaries for:
    - `larm_controller` (7 DoF)
    - `rarm_controller` (7 DoF)
    - `head_controller` (2 DoF)
    - `fullbody_controller` (optional)

The controller names/actions follow the standard `FollowJointTrajectory` pattern:
`<controller>/follow_joint_trajectory`.

## Workspace requirement (important)

`techrie_demo` imports this package with:

```python
from jedy_play.jedy_interface import IJedyROSRobotInterface
```

Therefore, `jedy_play` must be visible in the same ROS environment as `techrie_demo`.
The simplest setup is to place both repositories under the **same catkin workspace** (`src/`) and build once.

## Install / Build

```bash
cd ~/tmp_ws/src
# clone both repositories
# git clone .../jedy_play.git
# git clone .../jsk_demos.git (contains techrie_demo)

cd ~/tmp_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
source devel/setup.bash
```

## Quick check

```bash
rosrun jedy_play smoke_import.py
```

Expected output: it prints `IJedyROSRobotInterface` without ImportError.

## How it is used from techrie_demo

`techrie_demo/nodes/hw/robot_behavior.py` creates a robot interface like:

```python
ri = IJedyROSRobotInterface(robot_model, namespace=None, controller_timeout=10)
```

- `robot_model` is typically a `skrobot` URDF robot model.
- The interface sends trajectories to the controllers listed in `default_controller()`.

## Notes

- This package does **not** bring up the robot hardware by itself.
  Robot-side controller nodes must be running (provided by `kxr_controller` stack) so that the action servers exist.
- If you rename controller namespaces, update `jedy_interface.py` accordingly.
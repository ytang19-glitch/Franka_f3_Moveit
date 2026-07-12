# Requirements

## Hardware

- Franka FR3 robot
- Ubuntu 24.04
- ROS 2 Jazzy
- Franka ROS 2
- MoveIt 2
- libfranka (over 0.18.0)
- FCI enabled on the robot

---

## Required ROS 2 packages

```bash
sudo apt update

sudo apt install \
    ros-jazzy-moveit \
    ros-jazzy-moveit-py \
    python3-scipy
```

(Optional)

```bash
sudo apt install \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro
```

---

## Required Franka packages

The following packages should already exist in your workspace:

```text
franka_ros2
franka_description
franka_fr3_moveit_config
franka_hardware
franka_robot_state_broadcaster
franka_example_controllers
```

Verify:

```bash
ros2 pkg list | grep franka
```

---

## Workspace

```text
~/franka_ros2_ws
```

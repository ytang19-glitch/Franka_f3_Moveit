# Requirements

This project has been tested on **Ubuntu 24.04** with **ROS 2 Jazzy**.

---

## Hardware Requirements

```text
- Franka FR3 robot
- Ubuntu 24.04 workstation
- Ethernet connection
- Franka Control Interface (FCI) enabled
```

---

## Software Requirements

```text
- ROS 2 Jazzy
- MoveItPy
- libfranka (>= 0.18.0)
- Franka ROS 2
- python3-scipy
```

---

## Workspace

The project assumes the following ROS 2 workspace:

```text
~/franka_ros2_ws
```

---

## Required ROS 2 Packages

Update the package index:

```bash
sudo apt update
```

Install the required ROS 2 packages:

```bash
sudo apt install \
    ros-jazzy-moveit \
    ros-jazzy-moveit-py \
    python3-scipy
```

Create the ROS 2 Python package:

```bash
ros2 pkg create ...
```

### Optional Packages

```bash
sudo apt install \
    ros-jazzy-rviz2 \
    ros-jazzy-xacro
```

---

## Required Franka Packages

The following packages should already exist in the ROS 2 workspace:

```text
franka_ros2
franka_description
franka_fr3_moveit_config
franka_hardware
franka_robot_state_broadcaster
franka_example_controllers
```

Verify the installation:

```bash
ros2 pkg list | grep franka
```

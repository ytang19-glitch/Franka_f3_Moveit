# July 10 — Creating a Custom ROS 2 Python Package


### Goal

Convert the temporary Cartesian MoveIt script into a proper ROS 2 Python package.

### Reasoning

A standalone Python script is not enough because MoveIt requires many parameters:

```text
robot_description
robot_description_semantic
robot_description_kinematics
joint_limits
planning_pipelines
trajectory_execution
controller configuration
```

These should be loaded through a launch file.

### Result

A new ROS 2 Python package was created:

```text
fr3_moveit_python
```

Its purpose is to contain:

```text
cartesian_move.py
cartesian_move.launch.py
custom Cartesian motion logic
official FR3 MoveIt configuration loading
```

### Decision

The package should reuse the official `franka_fr3_moveit_config` instead of redefining the robot model and controller setup manually.

---

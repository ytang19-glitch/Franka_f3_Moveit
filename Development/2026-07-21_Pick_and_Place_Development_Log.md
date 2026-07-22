# July 20 — Pick and Place Development Log


### Previous Goal:
Develop a reusable Franka FR3 pick-and-place framework based on MoveItPy and ROS2.

#### Current Goal : Debugging and test code 

### Test

#### Step 1: Gripper Hardware Verification

Purpose:
Verify Franka gripper action interface before integrating with pick-and-place.

Test command:
```bash
ros2 run fr3_moveit_python gripper_control
```
Final result from Troubleshooting.md:
```bash
- ROS2 Python packages execute code from the install space, not directly from src.
- After changing package structure, rebuild and source the workspace.
- Standalone ROS2 nodes and reusable Python classes should be separated.
- Always verify hardware interfaces before debugging application-level code.
- setup.py entry points must match the actual Python architecture.
```

#### Step 2: Check motion.py

Purpose:
`motion.py` is the robot arm motion abstraction layer.
Its responsibility is to hide the complexity of MoveItPy, planning scene, IK, and trajectory execution.

It provides simple motion APIs for higher-level tasks.

```python
arm.move_to_pose(target_pose)
arm.move_relative(
    dx=0,
    dy=0,
    dz=-0.05

Rebuild packages after changes of python file
```bash
colcon build \
--packages-select fr3_moveit_python \
--symlink-install
```

---
#### Step 3: Basic MoveItPy Workflow

Purpose:

This example demonstrates the basic workflow of MoveItPy. The process consists of four main steps:
- Initialize the ROS 2 node and MoveItPy.
- Load a planning component (robot planning group).
- Generate a motion plan.
- Execute the planned traject

Workflow
```bash
InitialWorkflowize ROS 2
        │
        ▼
Create MoveItPy Object
        │
        ▼
Load Planning Component
(e.g. panda_arm / fr3_arm)
        │
        ▼
Set Goal State
        │
        ▼
Generate Motion Plan
        │
        ▼
Execute Trajectory
```

Relative Links:
```bash
https://docs.ros.org/en/jazzy/p/moveit_py/__README.html
```
---


Purpose

Explain the entire software architecture.
In moveit, cartesian path is not easy for cartesian motion due to its character on limited trajectory
Eg: Only one axis motion can be calculated 



```bash
Python Script
      │
      ▼
MoveItPy
      │
      ▼
Planning Scene
      │
      ▼
IK Solver
      │
      ▼
OMPL Planner
      │
      ▼
Joint Trajectory
      │
      ▼
fr3_arm_controller
      │
      ▼
ros2_control
      │
      ▼
Franka Hardware
      │
      ▼
```
FR3









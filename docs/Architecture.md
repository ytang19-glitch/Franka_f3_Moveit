## FR3 MoveIt Cartesian Motion & Pick-and-Place Architecture
### Purpose

This project demonstrates how to use MoveIt 2 + ROS 2 to control the Franka FR3 robot for Cartesian motion and pick-and-place tasks.

MoveIt Cartesian planning has limitations because it requires finding valid joint solutions along a Cartesian path. For simple motions (e.g., moving only along one axis such as Z direction), Cartesian interpolation is feasible, but complex trajectories may require additional planning methods such as OMPL.

---

## Software Architecture
## Cartesian Motion Pipeline
### Purpose

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
    FR3
```

---
### Pick-and-Place Architecture
The arm motion and gripper control are independent systems. MoveIt handles arm trajectory planning, while the Franka gripper uses its own action interface

```bash

              pick_and_place.py
                       |
        +--------------+--------------+
        |                             |
        ↓                             ↓

    MoveIt 2                    Franka Gripper
        |                             |
        ↓                             ↓

/execute_trajectory          /franka_gripper/move

        |                             |

   FR3 Arm Controller          Franka Hand

        |
        ↓

       FR3 Robot
```
---

## The structure of 3_moveit_python and purpose of each file

```bash
fr3_moveit_python/
│
├── cartesian_move.py
│   # Standalone Cartesian motion demo
│   # Purpose:
│   # - Test MoveItPy Cartesian planning
│   # - Move FR3 TCP by dx/dy/dz
│   # Example:
│   # ros2 launch fr3_moveit_python cartesian_move.launch.py dz:=-0.05 execute:=true
│
│
├── motion.py
│   # Reusable MoveItPy motion library
│   # Contains:
│   # - MotionController class
│   # - Cartesian motion functions
│   # - move_up()
│   # - move_down()
│   # - move_forward()
│   # - move_backward()
│   #
│   # Used by:
│   # - cartesian_pickplace.py
│   # - pick_place.py
│
│
├── cartesian_pickplace.py
│   # Cartesian pick/place motion interface
│   # Purpose:
│   # - Combine multiple Cartesian motions
│   #
│   # Example sequence:
│   # 1. Move above object
│   # 2. Move down
│   # 3. Grasp
│   # 4. Move up
│   # 5. Move to place position
│   #
│   # Uses:
│   # motion.py
│   # gripper_control.py
│
│
├── gripper_control.py
│   # Franka gripper control
│   #
│   # Two modes:
│   #
│   # (1) Standalone test mode:
│   #     Verify gripper action server
│   #
│   #     Example:
│   #     ros2 run fr3_moveit_python gripper_control
│   #
│   #
│   # (2) Reusable library mode:
│   #     Provide:
│   #       open_gripper()
│   #       close_gripper()
│   #
│   #     Used by:
│   #       pick_place.py
│
│
├── pick_place.py
│   # Final application layer
│   #
│   # Task logic:
│   #
│   #       Move above object
│   #              |
│   #              v
│   #       Cartesian descend
│   #              |
│   #              v
│   #       Close gripper
│   #              |
│   #              v
│   #       Lift object
│   #              |
│   #              v
│   #       Cartesian move to place
│   #              |
│   #              v
│   #       Open gripper
│   #
│   # Uses:
│   #       motion.py
│   #       gripper_control.py
│
│
├── setup.py
│   # ROS2 Python package entry points
│   # Example:
│   # cartesian_move
│   # gripper_control
│   # pick_place
│
│
├── package.xml
│   # ROS2 dependencies
│
│
└── launch/
    │
    └── cartesian_move.launch.py
        # Launch MoveIt + run Cartesian demo
```

---

## Design Concept

The project follows a layered architecture:

```bash
Application Layer
        |
        v
Motion Library
        |
        v
MoveIt 2 Interface
        |
        v
ROS2 Controllers
        |
        v
Robot Hardware

```






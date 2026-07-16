## Cartesian motion
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

### pick and place

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





```






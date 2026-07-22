# July 15 — Explore Potential Extension Motion ( gripper control)


### Goal
Explore gripper control as a possible extension for future pick-and-place development.

The purpose was to test whether the Franka gripper action interface can be controlled through the custom fr3_moveit_python package.

### Test

#### Step 1 — Launch MoveIt with Gripper Support

First, launch the official Franka MoveIt configuration:
```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  robot_ip:=172.16.0.2
```
Then launch MoveIt with gripper support enabled:
```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  robot_ip:=172.16.0.2 \
  use_gripper:=true
```

#### Step 2 — Edit Gripper Control File

Edit the gripper control script:
```bash
nano ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/gripper_control.py
```

#### Step 3 — Edit setup.py

Edit the package setup file:
```bash
nano ~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```
The goal was to make sure gripper_control.py is registered as a ROS 2 executable.

#### Step 4 — Check Gripper Action Server

Check whether the gripper action server is available:
```bash
ros2 action info /fr3/fr3_gripper/gripper_action
```

#### Step 5 — Rebuild the Package

After changing Python files or setup.py, rebuild the package:
```bash
colcon build --packages-select fr3_moveit_python
source install/setup.bash
```

#### Step 6 — Verify Package Setup

Check the package setup file:
```bash
gedit ~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```
Confirm that the executable entry point matches the Python file structure.

#### Step 7 — Run Gripper Test Node

Run the gripper control node:
```bash
ros2 run fr3_moveit_python gripper_control
```

### Result

The gripper control test was used to verify the gripper interface before integrating it into the pick-and-place pipeline.

Detailed debugging notes are recorded in:
```bash
Troubleshooting.md
```

### Next Step

After testing gripper_control.py, the next development task is:

Edit and test pick_place.py

The goal is to gradually combine:
```bash
Arm motion
    +
Gripper open / close
    +
Pick-and-place sequence
```

### Conclusion

The July 15 work focused on preparing gripper control as a future extension.

The main technical lesson was:
```bash
Before integrating the gripper into pick-and-place logic, the gripper action interface should be tested independently.
```

---

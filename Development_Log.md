## Development Log

### Project: Franka FR3 MoveIt Cartesian Motion Demo

This log records the main experiments, results, and technical decisions made while developing Cartesian motion control for the Franka FR3 using `franka_ros2` and MoveIt 2.

---

### July 7 — Official Franka ROS 2 Controller Test

### Goal

Verify that the official `franka_ros2` package can communicate with the real FR3 hardware before writing any custom motion code.

### Test

The official example controller was launched:

```bash
ros2 launch franka_bringup example.launch.py \
  controller_names:=joint_position_example_controller \
  robot_ips:=172.16.0.2 \
  namespace:=fr3
```

Then the controllers and joint state topics were checked:

```bash
ros2 control list_controllers -c /fr3/controller_manager
ros2 topic list | grep joint
ros2 topic echo /fr3/joint_states --once
```

### Observation

The robot published joint states, and the controller manager was working.

However, `joint_position_example_controller` did not expose a normal command topic.

```bash
ros2 topic info /fr3/joint_position_example_controller/commands
```

Result:

```text
Unknown topic
```

### Conclusion

This is expected. The official `joint_position_example_controller` is mainly a demo/test controller.

It verifies:

```text
ROS 2 Control → franka_hardware → libfranka → FCI → FR3
```

but it is not intended for custom user-defined motion.

### Decision

Use the official controller only for system verification.
Test a trajectory controller next for custom motion.

---

### July 8 — Testing `joint_trajectory_controller`

### Goal

Test whether a standard ROS 2 `JointTrajectoryController` can be used for custom joint-space motion.

### Test

A `joint_trajectory_controller` was added to `controllers.yaml` and configured for the seven FR3 joints:

```text
fr3_joint1
fr3_joint2
fr3_joint3
fr3_joint4
fr3_joint5
fr3_joint6
fr3_joint7
```

The controller was launched through `franka_bringup`, and a `trajectory_msgs/msg/JointTrajectory` command was tested.

### Observation

The controller could be loaded, and the command interface could be checked with:

```bash
ros2 control list_hardware_interfaces -c /fr3/controller_manager
ros2 control list_controllers -c /fr3/controller_manager
```

However, direct trajectory control was not the cleanest or most reliable approach for the final Cartesian motion target.

### Conclusion

A generic trajectory controller is useful for testing, but it is not the best final method for Cartesian motion on the FR3.

### Decision

Move to the official MoveIt-based pipeline instead of manually controlling trajectories.

---

### July 9 — Choosing MoveIt as the Main Motion Layer

### Goal

Find the proper software layer for point-to-point and Cartesian robot motion.

### Reasoning

A Cartesian command such as:

```text
Move the TCP downward by 1 cm
```

requires more than a raw controller command. It needs:

```text
current robot state
end-effector pose
inverse kinematics
joint limits
collision checking
trajectory generation
controller execution
```

These are MoveIt responsibilities.

### Test

MoveIt was tested with fake hardware first:

```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  use_fake_hardware:=true
```

Then real hardware was prepared:

```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  robot_ip:=172.16.0.2 \
  use_fake_hardware:=false
```

### Conclusion

MoveIt is the correct layer for Cartesian motion.

The intended pipeline became:

```text
MoveIt
  ↓
ros2_control
  ↓
franka_ros2
  ↓
franka_hardware
  ↓
libfranka / FCI
  ↓
FR3
```

### Decision

Use MoveIt and `moveit_py` for scripted Cartesian motion.

---

### July 10 — Creating a Custom ROS 2 Python Package

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

### July 11 — Inspecting Official Franka MoveIt Configuration

### Goal

Understand what the official Franka MoveIt launch file loads and reuse the same configuration in the custom launch file.

### Test

The official launch file was inspected:

```bash
sed -n '1,260p' \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch/moveit.launch.py"
```

Important configuration keywords were checked:

```bash
grep -R -n \
"MoveItConfigsBuilder\|robot_description\|robot_description_semantic" \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch"
```

### Finding

MoveIt requires:

```text
robot_description
robot_description_semantic
robot_description_kinematics
joint_limits
planning_pipelines
trajectory_execution
```

The official Franka MoveIt setup normally uses:

```text
fr3_arm_controller
```

This controller uses a trajectory interface connected to an effort-based hardware command interface.

### Control Understanding

MoveIt does not send raw torque or raw effort commands.

The actual logic is:

```text
Cartesian target
  ↓
MoveIt planning / IK
  ↓
joint trajectory
  ↓
fr3_arm_controller
  ↓
effort command interface
  ↓
FR3
```

Therefore, the hardware command interface should not be commanded directly for Cartesian motion.

### Conclusion

The custom launch file should load the official FR3 MoveIt configuration and only add the custom Python Cartesian motion node.

---

### Current Status

By July 11:

```text
Official Franka ROS 2 controller verified
Joint states verified
Controller manager verified
Generic trajectory controller tested
MoveIt selected as final motion layer
MoveIt fake hardware tested
MoveIt real hardware prepared
Custom fr3_moveit_python package created
Official FR3 MoveIt configuration inspected
Cartesian MoveItPy node under development
```

---

### Key Decisions

1. Use `joint_position_example_controller` only for official system verification.
2. Do not use it for custom motion because it has no user command topic.
3. Do not directly command the hardware effort interface.
4. Use MoveIt for Cartesian planning and trajectory generation.
5. Reuse the official `franka_fr3_moveit_config`.
6. Use a custom launch file only to connect the official MoveIt config with the custom Python node.

---

### Next Steps

```text
Finalize cartesian_move.py
Finalize cartesian_move.launch.py
Build fr3_moveit_python
Test planning with execute:=false
Verify FollowJointTrajectory action server
Add delay if MoveItPy action client connects too early
Test small Cartesian motion first, e.g. dz:=-0.005
```

### July 13 — Organize the github file 

Update:
```bash
launch
requirement
setup.py
correct README.md
```

### July 14 — Add to existing package

```bash
cd ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python
touch gripper_control.py
touch pick_place.py
```

setup.py

entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
        'gripper_control = fr3_moveit_python.gripper_control:main',
    ],
},



### July 15 — Explore Potential Extension Motion ( gripper control)

1.Run and test gripper_control.py

Ready state:

Launch moveit:
```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py   robot_ip:=172.16.0.2

ros2 launch franka_fr3_moveit_config moveit.launch.py \
robot_ip:=172.16.0.2 \
use_gripper:=true
```
Edit Gripper control file
```
nano ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/gripper_control.py
```
Edit Setup file :
```bash
 nano ~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```
Check state:

1.Test the gripper 
```bash
ros2 action info /fr3/fr3_gripper/gripper_action
```
2. Rebuild the specific package created
```bash
colcon build --packages-select fr3_moveit_python
source install/setup.bash
```
3.Vertify the integrality of setup file
```bash
gedit ~/franka_ros2_ws/src/Franka_f3_Moveit/setup.py
```
4.Try to make robot moved
```bash
ros2 run fr3_moveit_python gripper_control
```
Test gripper_control.py
Details are shown in toublrshooting.md

2.Edit and test pickandplace.py



### July 16 — Pick and place (test gripper)

(1) Logic of pick and place
First try: open
logic:
```bash
cartesian + gripper  close + cartesian + joint motion + cartesian + gripper release
```
(2) 
#### Original version (cartesian_move.py)

Build the engine every time if we want to drive.
```bash
Drive to school--Build engine--Install wheels--Install steering--Drive--Every trip repeats the same work.---Refactored version
```
#### (cartesian_pickplace.py)
 already have a car.
```bash
Drive to school--Start engine--Drive
```
The engine is reusable. motion.py is the engine.

```bash
fr3_moveit_python/
│
├── cartesian_move.py          # original demo (keep)
│
├── motion.py                  # new reusable MoveItPy class
│
├── cartesian_pickplace.py     # pick/place Cartesian interface
│
├── gripper_control.py
│ (1) Standalone test mode → verify hardware/action server works.
│ (2) Reusable library mode → use the same class inside pick_place.py.
│
└── pick_place.py              # final task
```

Open the new window:
```bash
source /opt/ros/jazzy/setup.bash
source ~/franka_ros2_ws/install/setup.bash
```
(3) Debugging the hardware
Debugging:
```bash
ros2 run fr3_moveit_python gripper_control
```

After close the gripper:

```bash
ros2 action send_goal \
/franka_gripper/move \
franka_msgs/action/Move \
"{width: 0.00, speed: 0.05}"
```

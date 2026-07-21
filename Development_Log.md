## Development Log

### Project: Franka FR3 MoveIt Cartesian Motion Demo

This log records the main experiments, results, and technical decisions made while developing Cartesian motion control for the Franka FR3 using `franka_ros2` and MoveIt 2.

---

Open a new window:
```bash
source /opt/ros/jazzy/setup.bash
source ~/franka_ros2_ws/install/setup.bash
```




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

---
### July 13 — Organize the github file 

Update:
```bash
launch
requirement
setup.py
correct README.md
```

---
### July 14 — Add to existing package

```bash
cd ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python
touch gripper_control.py
touch pick_place.py
```

setup.py:
```bash
entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
        'gripper_control = fr3_moveit_python.gripper_control:main',
    ],
},
```

---
### July 15 — Explore Potential Extension Motion ( gripper control)

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

### July 16 — Pick and place (test gripper)

### July 16 — Cartesian Motion Refactoring Log

### Goal

Refactor `cartesian_move.py` so that one file supports two purposes:

1. **Standalone Cartesian motion test**
2. **Reusable Cartesian motion module**

The reusable Cartesian logic remains inside `cartesian_move.py`. Therefore, a separate `cartesian_motion.py` file is not required.

The file structure is:

```text
cartesian_move.py
│
├── CartesianMotion class
│   └── Reusable Cartesian motion methods
│
└── main()
    └── Standalone Cartesian motion test
```

The reusable class provides methods such as:

```python
motion.move_relative(dx=0.0, dy=0.0, dz=-0.05)
motion.move_down(0.05)
motion.move_up(0.05)
```

The `main()` function is only used when `cartesian_move.py` is launched as a standalone application.

---

### Test

#### Standalone Test

Run `cartesian_move.py` directly through the launch file:

```bash
ros2 launch fr3_moveit_python \
  cartesian_move.launch.py \
  dz:=-0.05 \
  execute:=true
```

The standalone execution flow is:

```text
main()
  ↓
Create CartesianMotion
  ↓
Read dx, dy, and dz
  ↓
Plan Cartesian motion
  ↓
Execute the trajectory
```

#### Reusable Module Test

Import the Cartesian motion class into another file:

```python
from fr3_moveit_python.cartesian_move import CartesianMotion

motion = CartesianMotion()

motion.move_down(0.05)
motion.move_up(0.05)
```

Example use in `pick_place.py`:

```python
motion.move_down(approach_distance)
gripper.close()
motion.move_up(lift_distance)
```

The reusable methods should return success or failure instead of terminating the complete Python process.

---

### Conclusion

`cartesian_move.py` now covers two functions:

```text
cartesian_move.py
    ├── Standalone Cartesian motion test
    └── Reusable Cartesian motion module
```

The `CartesianMotion` class contains reusable planning and execution logic.

The `main()` function provides the standalone test interface.

This avoids duplicating Cartesian motion code while still allowing the motion to be tested independently and reused by `pick_place.py`.

---

### July 20 — Pick and Place Development Log

### Previous Goal:
Develop a reusable Franka FR3 pick-and-place framework based on MoveItPy and ROS2.

#### Current Goal : Debugging and test code 

### Test

### Step 1: Gripper Hardware Verification

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

### Step 2: Check motion.py

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

### Step 3: Basic MoveItPy Workflow

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

### July 20 — MoveItPy Arm Execution Mistakes Log

### Topic
Franka FR3 arm execution using **MoveItPy**, **OMPL**, and `fr3_arm_controller`.
Gripper integration is postponed.  
This log focuses only on the FR3 arm motion pipeline.

### Goal
Verify that a planned trajectory from MoveItPy can be executed on the real Franka FR3 arm.
Target execution chain:

```text
MoveItPy
    ↓
OMPL planning
    ↓
MoveIt trajectory execution
    ↓
FollowJointTrajectory action
    ↓
fr3_arm_controller
    ↓
ros2_control
    ↓
franka_hardware
    ↓
libfranka / FCI
    ↓
Franka FR3
```
### Mistakes

#### Mistake 1 — Wrong Current State Usage
Problem:
 get the live robot state from RobotModel.

Error
AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'
Fix

RobotModel only describes the robot model.
The current robot state should be handled through the MoveItPy planning component.

#### Mistake 2 — Wrong Goal State Format
Problem:
The goal joint positions were passed in an unsupported MoveItPy format.

Fix:
Use a RobotState object and set joint group positions with a numpy.ndarray.

Concept:
```bash
RobotState
    ↓
set_joint_group_positions()
    ↓
set_goal_state()
```
---
#### Mistake 3 — Misdiagnosing Execution Failure as Hardware Failure
Problem:

MoveItPy planning succeeded, but execution failed:
```bash
Goal request rejected
Goal was rejected by server
Completed trajectory execution with status ABORTED
```
At first, this looked like a controller or hardware issue.

Verification

The following items were checked:
```bash
- fr3_arm_controller active                         
- FollowJointTrajectory action server available     
- MoveIt action client connected                    
- FR3 effort interfaces claimed                     
- /joint_states publishing FR3 joints               
```
A direct FollowJointTrajectory command was tested.

Result:
```bash
Goal successfully reached
Goal finished with status: SUCCEEDED
Conclusion
```
The FR3 controller, FCI connection, hardware interface, and real robot execution path were working.

The problem was on the MoveIt configuration side.

#### Mistake 4 — Wrong OMPL Plugin Parameter
Problem:

The custom launch file used the wrong OMPL plugin parameter name.

Wrong:
```bash
planning_plugins
```
Correct:
```bash
planning_plugin
```
Error:
Planning plugin name is empty or not defined in namespace 'ompl'
Fix

Use the correct singular parameter:

planning_plugin: ompl_interface/OMPLPlanner

#### Mistake 5 — Missing Planning Adapters for Time Sequence
Problem

MoveIt could generate a geometric path, but the trajectory was not properly prepared for real controller execution.

Planning success alone does not guarantee valid trajectory timing.

The controller needs:

time_from_start
velocity
acceleration
valid trajectory timing
Fix

Add planning response adapters, especially:
```
default_planning_response_adapters/AddTimeOptimalParameterization
```
Purpose

AddTimeOptimalParameterization converts the geometric path into a time-parameterized trajectory.

Without this adapter, fr3_arm_controller may reject the goal even when OMPL planning succeeds.

#### Mistake 6 — Missing Velocity and Acceleration Scaling
Problem:

The launch file did not define:
```bash
max_velocity_scaling_factor
max_acceleration_scaling_factor
```
Fix:

Add safe velocity and acceleration scaling parameters for real robot execution.

Example values:
```bash
max_velocity_scaling_factor: 0.05
max_acceleration_scaling_factor: 0.05
Mistake 7 — Misleading Execution Output
```
Problem:
```bash
The script printed: Execution finished
```
even when MoveIt reported:

Completed trajectory execution with status ABORTED
Fix:

Only print execution success after checking the actual execution result.

#### Final Fix Summary:

The critical fixes were:
```bash
Correct MoveItPy API usage
Correct OMPL plugin parameter
Add planning request adapters
Add planning response adapters
Add time-parameterization adapter
Add velocity and acceleration scaling
Verify controller using direct FollowJointTrajectory action
```
### Result

After fixing the MoveItPy usage and custom launch configuration, the full execution pipeline succeeded.

Successful result:
```bash
Calling Planner 'OMPL'
Goal request accepted
Controller 'fr3_arm_controller' successfully finished
Completed trajectory execution with status SUCCEEDED
```
Final Lesson:
```bash
Planning success does not guarantee execution success.

For real Franka FR3 execution, both must be correct:

MoveItPy planning logic +
MoveIt launch / OMPL plugin / adapter configuration

The main problem was not the robot hardware.

The main problem was incomplete MoveIt launch configuration, especially:

planning_plugin +
AddTimeOptimalParameterization
```
Current Status:
MoveItPy arm planning working                      
fr3_arm_controller verified                        
Direct FollowJointTrajectory test succeeded        
OMPL plugin configuration fixed                    
Trajectory time-parameterization added             
MoveItPy arm execution succeeded                   
Gripper integration postponed           

### Next Actions:
```bash
1. Clean up the custom MoveIt launch file.
2. Keep direct FollowJointTrajectory command as a hardware test.
3. Refactor reusable arm motion logic into motion.py.
4. Keep high-level task logic separate from reusable motion APIs.
5. Add Cartesian approach and retreat motion for the arm.
6. Test small safe arm motions first.
7. Update Troubleshooting.md with the OMPL plugin and adapter issue.
```

















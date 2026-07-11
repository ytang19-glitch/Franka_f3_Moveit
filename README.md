# Franka_f3_Moveit


# Franka FR3 MoveIt Cartesian Motion Demo

## Date

July 11

## Goal

This project tests Cartesian motion control for the Franka FR3 robot **without Docker**.

The target demo is simple:

```text
Move the FR3 end-effector downward by 1 cm using MoveIt
```

The purpose is to verify that the MoveIt pipeline can communicate correctly with the Franka ROS 2 controller and execute a Cartesian trajectory on the robot.

---

## System Overview

The control flow is:

```text
Python Cartesian command
        ↓
MoveIt
        ↓
Inverse kinematics / planning
        ↓
Joint trajectory
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

This is different from directly commanding the hardware interface.

---

## Why Not Directly Use `command_interface`?

The Franka controller uses a low-level hardware command interface, such as `effort`.

However, a Cartesian command like:

```text
Move end-effector down by 1 cm
```

is not a direct joint effort command.

To execute this motion safely, the system needs:

* current robot joint states
* current end-effector pose
* inverse kinematics
* joint limits
* velocity and acceleration limits
* collision checking
* trajectory generation
* controller execution

These are handled by **MoveIt**, not directly by the hardware `command_interface`.

Therefore, the correct pipeline is:

```text
Cartesian pose target
        ↓
MoveIt computes joint trajectory
        ↓
JointTrajectoryController executes trajectory
        ↓
Controller outputs effort command
        ↓
Robot moves
```

The `command_interface` is only the low-level interface used by the controller.
It is not the correct level for directly sending Cartesian motion commands.

---

## Why Create a Custom Launch File and Python Node?

The official Franka MoveIt launch file starts the MoveIt system and loads the required robot configuration.

However, for a custom Cartesian demo, we need our own launch file to:

1. load the correct Franka FR3 MoveIt configuration
2. start the required MoveIt nodes
3. make sure `robot_description` and `robot_description_semantic` are available
4. connect MoveIt to the correct controller
5. start our custom Python Cartesian motion node

So the custom files are used for:

```text
custom launch file  → start MoveIt + load config + start demo node
Python file         → send Cartesian motion request
```

---

## Check Official Franka MoveIt Configuration

Before writing the custom launch file, inspect the official Franka MoveIt launch file.

### Print the official MoveIt launch file

```bash
sed -n '1,260p' \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch/moveit.launch.py"
```

Explanation:

```text
sed        stream editor
-n         do not print everything automatically
'1,260p'   print lines 1 to 260
ros2 pkg prefix franka_fr3_moveit_config
           find the installed path of the package
```

---

## Check Whether Official Launch Uses `MoveItConfigsBuilder`

```bash
grep -R -n \
"MoveItConfigsBuilder\|robot_description\|robot_description_semantic\|trajectory_execution\|to_moveit_configs" \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch"
```

This command checks whether the official Franka MoveIt launch file loads:

```python
.robot_description()
.robot_description_semantic()
.robot_description_kinematics()
.joint_limits()
.planning_pipelines()
.trajectory_execution()
.to_moveit_configs()
```

These parameters are required by MoveIt.

---

## Important MoveIt Configuration Items

MoveIt usually needs the following configuration:

```python
.robot_description()
.robot_description_semantic()
.robot_description_kinematics()
.joint_limits()
.planning_pipelines()
.trajectory_execution()
.to_moveit_configs()
```

Meaning:

| Config item                    | Meaning                                                  |
| ------------------------------ | -------------------------------------------------------- |
| `robot_description`            | URDF robot model                                         |
| `robot_description_semantic`   | SRDF semantic model, planning groups                     |
| `robot_description_kinematics` | IK solver configuration                                  |
| `joint_limits`                 | joint velocity, acceleration, and position limits        |
| `planning_pipelines`           | planning algorithms such as OMPL                         |
| `trajectory_execution`         | controller connection for executing planned trajectories |

Without these parameters, MoveIt may start but cannot correctly plan or execute robot motion.

---

## Check Franka Controller Configuration

Go to the Franka MoveIt config package:

```bash
cd ~/franka_ros2_ws/src/franka_ros2/franka_fr3_moveit_config/config
```

Then check the controller configuration, for example:

```bash
ls
```

Look for files related to:

```text
fr3_ros_controllers.yaml
ros2_controllers.yaml
moveit_controllers.yaml
```

The official Franka MoveIt configuration normally uses:

```text
fr3_arm_controller
```

This controller is usually a `JointTrajectoryController`.

The command interface may be:

```text
effort
```

This means MoveIt sends a desired joint trajectory, and the controller tracks the trajectory through effort control.

Simplified control logic:

```text
effort = Kp(position_error) + Kd(velocity_error) + Ki(integral_error)
```

or:

```text
τ = Kp(q_desired - q_actual)
  + Kd(qd_desired - qd_actual)
  + Ki∫(q_error dt)
```

So MoveIt does not directly send torque for Cartesian motion.
MoveIt sends a joint trajectory, and the controller converts tracking error into effort command.

---

## Check Joint Topics

List joint-related topics:

```bash
ros2 topic list | grep joint
```

Echo joint states:

```bash
ros2 topic echo /joint_states
```

Expected result:

```text
/joint_states should publish current FR3 joint positions and velocities
```

If `/joint_states` is missing, MoveIt cannot know the current robot state.

---

## Check Controllers

Check loaded controllers:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

Check hardware interfaces:

```bash
ros2 control list_hardware_interfaces -c /fr3/controller_manager
```

If there is no namespace, try:

```bash
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

Expected controller:

```text
fr3_arm_controller
```

Expected state:

```text
active
```

---

## Expected Motion Pipeline

For the 1 cm downward Cartesian motion:

```text
1. Python node gets current end-effector pose
2. Python node creates a new target pose 1 cm lower
3. MoveIt computes Cartesian path
4. MoveIt converts Cartesian path into joint trajectory
5. fr3_arm_controller receives joint trajectory
6. Controller tracks the trajectory
7. Robot moves down by approximately 1 cm
```

---

## Common Problems

### 1. `robot_description` missing

Check:

```bash
ros2 param list | grep robot_description
```

or:

```bash
ros2 topic list | grep robot_description
```

If missing, the MoveIt launch file is not loading the URDF correctly.

---

### 2. `robot_description_semantic` missing

This means the SRDF was not loaded.

MoveIt may fail because it does not know the planning group, such as:

```text
fr3_arm
```

---

### 3. `/joint_states` missing

MoveIt cannot plan if it does not know the current robot state.

Check:

```bash
ros2 topic echo /joint_states
```

---

### 4. Controller not active

Check:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

The controller should be:

```text
fr3_arm_controller    active
```

If it is inactive, MoveIt may plan successfully but fail during execution.

---

### 5. Wrong controller interface assumption

Do not assume Cartesian motion can be executed by directly publishing to the effort command interface.

Correct logic:

```text
Cartesian motion
    → MoveIt
    → joint trajectory
    → JointTrajectoryController
    → effort command interface
```

---

## Summary

The reason for creating a custom launch file and Python file is:

```text
MoveIt needs a complete robot configuration and controller connection.
Cartesian motion is a high-level motion planning task.
The hardware command interface is only the low-level controller output.
```

Therefore, the correct method is:

```text
Use official Franka MoveIt configuration
+ custom launch file
+ custom Python Cartesian motion node
```

Not:

```text
Directly command hardware interface
```

This makes the motion safer, more structured, and compatible with the official Franka ROS 2 MoveIt pipeline.

### July 11th : 

```bash
nano ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/cartesian_move.py
nano ~/franka_ros2_ws/src/fr3_moveit_python/launch/cartesian_move.launch.py
nano ~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```

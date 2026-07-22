
# Franka FR3 MoveIt Cartesian Motion Demo

## Table of Contents

- [Overview](#overview)
- [Goal](#goal)
- [Part I — ROS 2 Package](#part-i--ros-2-package)
- [Part II — Motion Planning & Control](#part-ii--motion-planning--control)
- [Part III — Verification & Execution](#part-iii--verification--execution)
- [Part IV — Miscellaneous](#part-iv--miscellaneous)

---

# Overview

This project demonstrates Cartesian motion control for the **Franka FR3** robot using **MoveItPy** on **native Ubuntu 24.04** with **ROS 2 Jazzy**.

It documents the complete development process, including package creation, MoveIt configuration, motion planning, controller verification, execution, and debugging on real hardware.

---

# Goal


This project tests Cartesian motion control for the Franka FR3 robot **without Docker**.

The target demo is simple:

```text
Move the FR3 end-effector downward by x cm using MoveIt
```

The purpose is to verify that the MoveIt pipeline can communicate correctly with the Franka ROS 2 controller and execute a Cartesian trajectory on the robot.

---

## Step 1 ; Ros2 Package

### Creating the `fr3_moveit_python` Package

#### 1. Create a ROS 2 Python package

Go to your ROS2 workspace:

```bash
cd ~/franka_ros2_ws/src
```

Create a new Python package:

```bash
ros2 pkg create fr3_moveit_python \
    --build-type ament_python \
    --dependencies \
        rclpy \
        geometry_msgs \
        moveit_ros_planning_interface
```

The package structure becomes:

```text
fr3_moveit_python/
├── fr3_moveit_python/
│   └── __init__.py
├── resource/
├── test/
├── package.xml
└── setup.py
```

---

#### 2. Create the motion script

Create the Python node:

```bash
nano \
~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/cartesian_move.py
```

This node is responsible for:

- Initialize MoveItPy
- Read the current TCP pose
- Apply a relative Cartesian displacement
- Plan a trajectory
- Optionally execute the trajectory

---

#### 3. Create the launch file

Create the launch directory:

```bash
mkdir -p \
~/franka_ros2_ws/src/fr3_moveit_python/launch
```

Create the launch file:

```bash
nano \
~/franka_ros2_ws/src/fr3_moveit_python/launch/cartesian_move.launch.py
```

The launch file loads the official MoveIt configuration and passes all required parameters to the Python node.

---

#### 4. Modify `setup.py`

Open:

```bash
nano \
~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```

Update it so that:

- `cartesian_move.py` is installed as a ROS2 executable
- `cartesian_move.launch.py` is installed into the package

---

#### 5. Build the package

Go to the workspace:

```bash
cd ~/franka_ros2_ws
```

Source ROS2:

```bash
source /opt/ros/jazzy/setup.bash
```

Build:

```bash
colcon build \
    --symlink-install \
    --packages-select fr3_moveit_python
```

Source the workspace:

```bash
source ~/franka_ros2_ws/install/setup.bash
```

---

#### 6. Verify the installation

Check the executable:

```bash
ros2 pkg executables fr3_moveit_python
```

Expected:

```text
fr3_moveit_python cartesian_move
```

Check the installed launch file:

```bash
ls \
~/franka_ros2_ws/install/fr3_moveit_python/share/fr3_moveit_python/launch/
```

Expected:

```text
cartesian_move.launch.py
```

---

#### 7. Run the package

Run the official moveit file:
```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py   robot_ip:=172.16.0.2
```

Planning only:

```bash
ros2 launch fr3_moveit_python \
    cartesian_move.launch.py \
    dz:=-0.005 \
    execute:=false
```

Execute on the robot:

```bash
ros2 launch fr3_moveit_python \
    cartesian_move.launch.py \
    dz:=-0.05 \
    execute:=true
```

---

## Part II — Motion Planning & Control

### Summary

The Cartesian motion demo uses MoveIt as the high-level planning layer between the Python command and the Franka hardware

---
## Part IV — Miscellaneous

### Misc 1 ; Workflow

```text
Create ROS2 package
        │
        ▼
Create cartesian_move.py
        │
        ▼
Create cartesian_move.launch.py
        │
        ▼
Modify setup.py
        │
        ▼
Build the package
        │
        ▼
Source the workspace
        │
        ▼
Launch the Cartesian motion node
```

### Misc 2 ; System Overview

The control flow is:

```text
Python MoveItPy node
        ↓
MoveIt planning component
        ↓
Robot model + current state + planning scene
        ↓
IK / collision checking / planner
        ↓
RobotTrajectory
        ↓
MoveIt trajectory execution manager
        ↓
/fr3_arm_controller/follow_joint_trajectory
        ↓
fr3_arm_controller
        ↓
ros2_control
        ↓
franka_hardware
        ↓
libfranka
        ↓
FCI communication
        ↓
Franka control box
        ↓
FR3 joints
```

This is different from directly commanding the hardware interface.


### Misc 3: Check Franka Controller Configuration

Go to the Franka MoveIt config package:

```bash
cd ~/franka_ros2_ws/src/franka_fr3_moveit_config/config
ls
```

FInd:

```text
- fr3_ros_controllers.yaml
- fr3_controllers.yaml
- fr3_joint_limits.yaml
- ompl_planning.yaml
- kinematics.yaml
```

In "fr3_ros_controllers.yaml"

```text
fr3_arm_controller
JointTrajectoryController`.
The command interface is effort

```

This means MoveIt sends a desired joint trajectory, and the controller tracks the trajectory through effort control.(PID)

Simplified control logic:

```text
effort = Kp(position_error) + Kd(velocity_error) + Ki(integral_error)
```

or:
```text
τ = Kp(q_desired - q_actual)+ Kd(qd_desired - qd_actual) + Ki∫(q_error dt)
```

So MoveIt does not directly send torque for Cartesian motion.
MoveIt sends a joint trajectory, and the controller converts tracking error into effort command.

---

#### Check Joint Topics

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

#### Check Controllers

Check loaded controllers:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

Check hardware interfaces:

```bash
ros2 control list_hardware_interfaces -c /fr3/controller_manager
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

### Expected Motion Pipeline

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
## Control Architecture
#### Why Not Directly Use `command_interface`?

The Franka controller uses a low-level hardware command interface, such as `effort`.

However, a Cartesian command like:

```text
Move end-effector down by 1 cm
```

is not a direct joint effort command.

To execute this motion safely, the system needs:
```text
- current robot joint states
- current end-effector pose
- inverse kinematics
- joint limits
- velocity and acceleration limits
- collision checking
- trajectory generation
- controller execution
```
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

#### Why Create a Custom Launch File and Python Node?

The official Franka MoveIt launch file starts the MoveIt system and loads the required robot configuration.

However, for a custom Cartesian demo, we need our own launch file to:

1. load the correct Franka FR3 MoveIt configuration (launch file)
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

#### Check Official Franka MoveIt Configuration

Before writing the custom launch file, inspect the official Franka MoveIt launch file.

##### Find the official MoveIt launch file

```bash
cd ~/franka_ros2_ws/src/franka_fr3_moveit_config/launch
nano ~/franka_ros2_ws/src/franka_fr3_moveit_config/launch/moveit.launch.py
```

---

##### Check Whether Official Launch Uses `MoveItConfigsBuilder`

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

##### Important MoveIt Configuration Items

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

### Common Problems

#### 1. `robot_description` missing

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

#### 2. `robot_description_semantic` missing

This means the SRDF was not loaded.

MoveIt may fail because it does not know the planning group, such as:

```text
fr3_arm
```

---

#### 3. `/joint_states` missing

MoveIt cannot plan if it does not know the current robot state.

Check:

```bash
ros2 topic echo /joint_states
```

---

#### 4. Controller not active

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

#### 5. Wrong controller interface assumption

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

### Summary

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

## Part III — Verification & Execution

### Experiment before actual running

```bash
nano ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/cartesian_move.py
nano ~/franka_ros2_ws/src/fr3_moveit_python/launch/cartesian_move.launch.py
nano ~/franka_ros2_ws/src/fr3_moveit_python/setup.py
```

The package provides:

- Relative Cartesian pose motion
- MoveItPy planning
- Optional trajectory execution
- Official FR3 MoveIt configuration

---

#### Planning test

Run planning without executing the robot.

```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py \
    dz:=-0.05 \
    execute:=false
```

Verified:

- Robot model loaded successfully
- SRDF loaded successfully
- OMPL planner initialized
- Current TCP pose obtained
- Relative Cartesian target generated
- Planning completed successfully

---

#### Verify controller

Check the available trajectory action.

```bash
ros2 action list -t | grep FollowJointTrajectory
```

Expected output:

```text
/fr3_arm_controller/follow_joint_trajectory
```

---

#### Verify Action Server

```bash
ros2 action info /fr3_arm_controller/follow_joint_trajectory
```

Expected:

```text
Action servers: 1
```

---

#### Verify controller status

```bash
ros2 control list_controllers
```

Expected:

```text
fr3_arm_controller             active
joint_state_broadcaster        active
franka_robot_state_broadcaster active
```

---

#### Execution issue

Planning succeeds, but execution reports

```text
Action client not connected to action server
```

Although the controller and Action Server are active, MoveItPy attempts to execute immediately after startup.

The Action Client may not have completed DDS discovery before the execution request is sent.

```bash
        time.sleep(1.0)
        flush_and_exit(0)
```

---

#### Current workaround

Before

```python
moveit.execute(...)
```

add a short delay

```python
time.sleep(5.0)
```

to allow the Action Client to connect to

```text
/fr3_arm_controller/follow_joint_trajectory
```

before sending the trajectory.

---

#### Current Progress

- Built a custom MoveItPy package
- Loaded the official FR3 MoveIt configuration
- Implemented relative Cartesian pose planning
- Successfully generated trajectories
- Verified controller and Action Server
- Debugging Action Client connection timing before execution

#### Repository Structure

```text
FR3 MoveIt Python
│
├── README.md                 ← Project overview
├── Software Architecture.md  ← Software design
├── Requirements.md           ← Hardware & software requirements
├── Development_Log.md        ← Development history
│
├── launch/                   ← ROS2 launch files
├── fr3_moveit_python/        ← Application source code
├── docs/                     ← Detailed documentation
├── resource/                 ← ROS2 package resources
├── test/                     ← Unit tests
│
├── package.xml               ← ROS2 package metadata
└── setup.py                  ← Package installation
```


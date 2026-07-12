## Development_Log
## Project: Franka FR3 MoveIt Cartesian Motion Demo

This file records the development process for controlling the Franka FR3 robot using the official `franka_ros2` package and MoveIt 2.

The final goal is to execute a small Cartesian motion, such as moving the FR3 end-effector downward by a few millimeters or centimeters, using the official Franka ROS 2 and MoveIt pipeline.

The development process follows this order:

```text
Official franka_ros2 controller test
        ↓
Joint state and controller verification
        ↓
Custom joint trajectory controller test
        ↓
MoveIt fake hardware test
        ↓
MoveIt real hardware test
        ↓
Custom MoveIt Python package
        ↓
Cartesian motion with MoveItPy
```

---

# July 7: Testing the Official Franka ROS 2 Example Controller

## Goal

The goal for July 7 was to verify that the official `franka_ros2` package can communicate with the FR3 robot before creating any custom motion code.

At this stage, the main question was:

```text
Can the official Franka ROS 2 package connect to the real FR3 hardware correctly?
```

Before testing MoveIt or custom motion scripts, the official example controller should work first. If the official example controller fails, then the problem is likely related to robot connection, FCI, network configuration, controller manager, or package installation.

---

## Test Conditions

The following conditions were required before launching the official example controller:

```text
FR3 powered on
FCI activated in Franka Desk
Host PC connected to the C2 Ethernet port
Host PC configured in the robot subnet
Robot IP: 172.16.0.2
Namespace: fr3
No other client connected to the robot
```

One important note is that only one client should connect to the robot through FCI at the same time. For example, if Docker `franky_ros` is already connected, the official ROS 2 controller may fail to connect.

---

## Action 1: Launch the Official Example Controller

The official Franka example controller was launched with:

```bash
ros2 launch franka_bringup example.launch.py \
  controller_names:=joint_position_example_controller \
  robot_ips:=172.16.0.2 \
  namespace:=fr3
```

Because different versions of `franka_ros2` may use different launch argument names, the launch arguments should be checked with:

```bash
ros2 launch franka_bringup example.launch.py --show-args
```

The possible argument names are:

```text
robot_ip
robot_ips
```

In this test, the version being used accepted:

```text
robot_ips:=172.16.0.2
```

---

## Action 2: Verify Controller Status

After launching the example controller, the controller list was checked:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

Expected output:

```text
joint_position_example_controller          active
joint_state_broadcaster                    active
franka_robot_state_broadcaster             active
```

This output means:

```text
controller_manager is running
joint_position_example_controller is loaded
joint_state_broadcaster is active
franka_robot_state_broadcaster is active
ROS 2 control can communicate with FR3
```

---

## Action 3: Verify Robot Joint State Topics

The joint-related topics were checked:

```bash
ros2 topic list | grep joint
```

Typical output:

```text
/fr3/joint_states
/fr3/franka/joint_states
/fr3/franka_gripper/joint_states
/fr3/dynamic_joint_states
```

Then the current joint configuration was read:

```bash
ros2 topic echo /fr3/joint_states --once
```

This step is important because it confirms that the robot is publishing real joint states. If `/fr3/joint_states` is missing, then MoveIt cannot know the current robot state later.

---

## Observation

The official example controller could be launched, and joint state topics were available.

However, the controller did not expose a normal command topic.

For example:

```bash
ros2 topic info /fr3/joint_position_example_controller/commands
```

Result:

```text
Unknown topic
```

At first this looked like a problem, but it is actually expected.

---

## Analysis

The `joint_position_example_controller` is not designed as a user-commanded controller. It is mainly an official demonstration and verification controller.

Its purpose is to verify that:

```text
ROS 2 control can talk to the FR3
libfranka works
FCI communication is active
hardware interface initializes correctly
controllers can be loaded
the robot can execute a built-in example motion
```

It is not intended for custom point-to-point commands.

Therefore, the lack of a command topic is normal.

---

## Result of July 7

The official example controller is useful for system verification, but it is not suitable for custom motion control.

Summary:

| Controller                          | Result                                 |
| ----------------------------------- | -------------------------------------- |
| `joint_position_example_controller` | Works as official test/demo controller |
| Command topic                       | Not available                          |
| Custom user motion                  | Not supported directly                 |
| Robot state topics                  | Available                              |
| Controller manager                  | Working                                |

---

## Next Step

Since the official example controller cannot accept custom user commands, the next step is to test a standard trajectory controller:

```text
joint_trajectory_controller/JointTrajectoryController
```

The goal is to determine whether custom joint-space trajectories can be sent directly to the robot.

---

# July 8: Testing `joint_trajectory_controller`

## Goal

The goal for July 8 was to test whether a standard ROS 2 `JointTrajectoryController` can be used for user-defined joint-space point-to-point motion.

The main question was:

```text
Can I send my own joint trajectory command to the FR3 through ros2_control?
```

The official `joint_position_example_controller` was useful for verifying the connection, but it could not accept custom motion commands.

---

## Action 1: Check Available Controller Types

The available controller types were checked with:

```bash
ros2 control list_controller_types -c /fr3/controller_manager
```

This command was used to verify whether the following controller type was available:

```text
joint_trajectory_controller/JointTrajectoryController
```

If this controller type is missing, the package needs to be installed.

---

## Action 2: Install Controller Package

If the controller package was not available, it was installed with:

```bash
sudo apt install ros-jazzy-joint-trajectory-controller
```

---

## Action 3: Edit `controllers.yaml`

The controller configuration file was opened:

```bash
nano ~/franka_ros2_ws/src/franka_bringup/config/controllers.yaml
```

The controller type was added to the top controller list:

```yaml
joint_trajectory_controller:
  type: joint_trajectory_controller/JointTrajectoryController
```

Then the controller parameter block was added:

```yaml
/**:
  joint_trajectory_controller:
    ros__parameters:
      joints:
        - fr3_joint1
        - fr3_joint2
        - fr3_joint3
        - fr3_joint4
        - fr3_joint5
        - fr3_joint6
        - fr3_joint7

      command_interfaces:
        - position

      state_interfaces:
        - position
        - velocity

      allow_partial_joints_goal: false
      open_loop_control: false
```

At this stage, the intended command interface was:

```text
position
```

The controller should receive joint position targets and generate a trajectory for the seven FR3 joints.

---

## Action 4: Rebuild the Workspace

After editing the controller configuration, the workspace was rebuilt:

```bash
cd ~/franka_ros2_ws
colcon build --symlink-install
source install/setup.bash
```

This step is required because the controller configuration is part of the ROS 2 workspace.

---

## Action 5: Launch the Trajectory Controller

The trajectory controller was launched with:

```bash
ros2 launch franka_bringup example.launch.py \
  controller_names:=joint_trajectory_controller \
  robot_ips:=172.16.0.2 \
  namespace:=fr3
```

---

## Action 6: Check Controller and Hardware Status

The controller status was checked:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

The hardware interfaces were checked:

```bash
ros2 control list_hardware_interfaces -c /fr3/controller_manager
```

The hardware components were checked:

```bash
ros2 control list_hardware_components -c /fr3/controller_manager
```

The important thing to observe was whether the required command interface was shown as:

```text
claimed
```

If an interface is `claimed`, it means the controller has taken control of that hardware interface.

---

## Action 7: Send a Joint Trajectory Command

A point-to-point joint trajectory command was sent:

```bash
ros2 topic pub --once /fr3/joint_trajectory_controller/joint_trajectory trajectory_msgs/msg/JointTrajectory \
"{joint_names: ['fr3_joint1', 'fr3_joint2', 'fr3_joint3', 'fr3_joint4', 'fr3_joint5', 'fr3_joint6', 'fr3_joint7'], points: [{positions: [0.06, -0.49, 0.28, -2.07, 0.0, 1.55, -2.27], time_from_start: {sec: 3, nanosec: 0}}]}"
```

If the topic name is uncertain, it can be checked with:

```bash
ros2 topic list | grep trajectory
```

---

## Observation

The trajectory controller could be loaded, and the command topic/action interface could be checked.

However, the direct joint trajectory workflow was not stable enough for the intended point-to-point motion. The controller could be loaded, but the execution behavior was not the final desired solution.

---

## Analysis

Directly adding a generic `joint_trajectory_controller` is not always the best method for FR3 motion because the official Franka MoveIt configuration may use its own controller setup.

The FR3 MoveIt configuration normally uses:

```text
fr3_arm_controller
```

This controller is connected to the official MoveIt pipeline.

Therefore, instead of manually creating a new trajectory controller, it is better to use the controller expected by the official Franka MoveIt configuration.

---

## Result of July 8

The `joint_trajectory_controller` test showed that custom trajectory control is possible in theory, but directly using this controller was not the most reliable or official path for the target Cartesian motion.

Summary:

| Item                     | Result                         |
| ------------------------ | ------------------------------ |
| Controller package       | Installed / checked            |
| Controller type          | Available                      |
| Custom controller config | Added                          |
| Joint trajectory command | Tested                         |
| Final suitability        | Not ideal for Cartesian motion |

---

## Next Step

The next step is to introduce MoveIt 2.

Reason:

```text
Cartesian motion requires planning, inverse kinematics, joint limits, and trajectory execution.
MoveIt is designed for this level of motion planning.
```

---

# July 9: Moving Toward the Official MoveIt Pipeline

## Goal

The goal for July 9 was to find the proper official software pathway for moving the FR3 robot.

The main question was:

```text
Should custom motion be sent directly through ros2_control, or should it go through MoveIt?
```

---

## Current Status Before MoveIt

The system status was:

```text
franka_ros2 can connect to FR3
controller_manager is available
joint_trajectory_controller can be loaded
trajectory action server exists
goal can be received
execution may fail or controller may deactivate
```

This showed that the low-level ROS 2 control side was partially working, but the full custom motion path was not stable enough.

---

## Decision

The decision was to use MoveIt 2 as the main motion planning layer.

The reason is that MoveIt handles:

```text
robot model
planning scene
inverse kinematics
joint limits
collision checking
trajectory generation
trajectory execution
controller connection
```

This is exactly what is needed for point-to-point and Cartesian motion.

---

## MoveIt Workflow

The expected workflow is:

```text
MoveIt
    ↓
Trajectory planning
    ↓
ros2_control
    ↓
franka_ros2
    ↓
franka_hardware
    ↓
libfranka / FCI
    ↓
FR3 hardware
```

This means MoveIt does not replace `franka_ros2`.

Instead:

```text
MoveIt plans the motion.
franka_ros2 executes the motion through ros2_control.
libfranka communicates with the FR3 hardware.
```

---

## Action 1: Install MoveIt

MoveIt was installed with:

```bash
sudo apt update
sudo apt install ros-jazzy-moveit
```

The ROS 2 environment was sourced:

```bash
source /opt/ros/jazzy/setup.bash
```

MoveIt installation was verified with:

```bash
ros2 pkg list | grep moveit
```

---

## Action 2: Test MoveIt with Fake Hardware

MoveIt was first launched with fake hardware:

```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  use_fake_hardware:=true
```

This test does not require the real robot.

The purpose is to verify that:

```text
FR3 robot model loads
SRDF loads
planning group is available
RViz MoveIt plugin works
planner can generate a trajectory
fake controller can execute the planned motion
```

In RViz, the test process is:

```text
Move the robot target
Plan
Execute
```

---

## Observation from Fake Hardware Test

The fake hardware test is useful because it separates MoveIt configuration problems from real robot hardware problems.

If fake hardware fails, the problem is likely in:

```text
MoveIt configuration
URDF
SRDF
planning group
controller config
RViz setup
```

If fake hardware works but real hardware fails, the problem is more likely in:

```text
robot connection
FCI
controller manager
hardware interface
trajectory execution
```

---

## Action 3: Test MoveIt with Real Hardware

MoveIt was launched with the real robot:

```bash
ros2 launch franka_fr3_moveit_config moveit.launch.py \
  robot_ip:=172.16.0.2 \
  use_fake_hardware:=false
```

Before executing any motion, the controllers should be checked:

```bash
ros2 control list_controllers
```

Expected controller:

```text
fr3_arm_controller    active
```

---

## Demo 1: Joint Space Motion in RViz

The first MoveIt demo was joint-space motion.

In RViz:

```text
Drag Joint1 / Joint2 / ... / Joint7
Click Plan
Click Execute
```

Expected result:

```text
Robot moves from one joint configuration to another joint configuration.
```

This verifies that the basic MoveIt planning and execution pipeline works.

---

## Demo 2: Cartesian Motion in RViz

The second demo was Cartesian motion.

Cartesian motion means:

```text
The end-effector should move along a Cartesian path, such as a straight line.
```

Example target:

```text
Move the TCP downward by 1 cm.
```

MoveIt should calculate inverse kinematics automatically.

However, Cartesian planning can fail if:

```text
target pose is unreachable
path causes collision
robot is near singularity
joint limits are exceeded
planning group or end-effector link is wrong
```

---

## Action 4: Start Python MoveIt Testing

Python-based MoveIt control was prepared.

Required package:

```bash
sudo apt install python3-scipy
```

MoveIt Python package search:

```bash
apt search ros-jazzy-moveit-py
```

Install MoveItPy if needed:

```bash
sudo apt install ros-jazzy-moveit-py
```

Verify Python import:

```bash
source /opt/ros/jazzy/setup.bash
python3 -c "import moveit_py; print('moveit_py OK')"
```

Create a temporary script directory:

```bash
mkdir -p ~/fr3_moveit_scripts
nano ~/fr3_moveit_scripts/move_down_1cm.py
```

Run the script:

```bash
source /opt/ros/jazzy/setup.bash
source ~/franka_ros2_ws/install/setup.bash
python3 ~/fr3_moveit_scripts/move_down_1cm.py
```

---

## Action 5: Check the End-Effector Link

The end-effector link should be checked from the SRDF:

```bash
ros2 param get /move_group robot_description_semantic | grep -i end_effector
```

This helps confirm which link MoveIt considers to be the TCP or end-effector.

---

## Result of July 9

MoveIt became the selected solution for both joint-space and Cartesian motion.

Summary:

| Item                                 | Result                        |
| ------------------------------------ | ----------------------------- |
| Direct `joint_trajectory_controller` | Not selected as final method  |
| MoveIt fake hardware                 | Used for configuration test   |
| MoveIt real hardware                 | Used for robot execution test |
| Cartesian motion                     | Should be handled by MoveIt   |
| Python interface                     | MoveItPy selected             |

---

## Next Step

The next step is to convert the temporary Python script into a proper ROS 2 package.

Reason:

```text
MoveItPy needs many parameters.
A ROS 2 launch file is the correct way to load the official FR3 MoveIt configuration and pass it to the Python node.
```

---

# July 10: Creating a ROS 2 Python Package for Cartesian Motion

## Goal

The goal for July 10 was to convert the standalone Cartesian MoveIt script into a proper ROS 2 Python package.

The main question was:

```text
How can I run the Cartesian MoveIt script with the correct robot_description, SRDF, kinematics, planning pipeline, and controller parameters?
```

A standalone Python script may not automatically receive all required MoveIt parameters. Therefore, a ROS 2 package and launch file are needed.

---

## Reason for Creating a Package

MoveItPy requires many parameters, including:

```text
robot_description
robot_description_semantic
robot_description_kinematics
joint_limits
planning_pipelines
trajectory_execution
controller configuration
```

These parameters are usually loaded by a launch file.

Therefore, the custom Cartesian motion code should be organized as:

```text
fr3_moveit_python package
        ↓
cartesian_move.py
        ↓
cartesian_move.launch.py
        ↓
official franka_fr3_moveit_config
        ↓
MoveItPy node receives correct parameters
```

---

## Action 1: Install Required Python Dependency

```bash
sudo apt install python3-scipy
```

This package may be required by MoveItPy or motion planning-related Python code.

---

## Action 2: Create the ROS 2 Python Package

Go to the workspace source directory:

```bash
cd ~/franka_ros2_ws/src
```

Create the package:

```bash
ros2 pkg create fr3_moveit_python \
  --build-type ament_python \
  --dependencies rclpy geometry_msgs moveit_ros_planning_interface
```

This creates the basic package structure:

```text
fr3_moveit_python/
├── fr3_moveit_python/
│   └── __init__.py
├── resource/
├── test/
├── package.xml
├── setup.cfg
└── setup.py
```

---

## Action 3: Copy the Cartesian Motion Script

The temporary script was copied into the package:

```bash
cp ~/fr3_moveit_scripts/move_down_1cm.py \
~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/
```

The script should later be renamed or organized as:

```text
cartesian_move.py
move_down_1cm.py
move_to_pose.py
```

---

## Action 4: Create the Launch Directory

```bash
mkdir -p ~/franka_ros2_ws/src/fr3_moveit_python/launch
```

The custom launch file should be placed here:

```text
~/franka_ros2_ws/src/fr3_moveit_python/launch/cartesian_move.launch.py
```

or:

```text
~/franka_ros2_ws/src/fr3_moveit_python/launch/move_down_1cm_launch.py
```

---

## Action 5: Update `setup.py`

The `setup.py` file needs to install:

```text
Python executable
launch file
package resource file
```

The executable entry point should look like:

```python
entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
    ],
},
```

The launch file should also be installed through `data_files`.

---

## Action 6: Build the Package

```bash
cd ~/franka_ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select fr3_moveit_python
source install/setup.bash
```

---

## Action 7: Verify the Package Installation

Check the package executable:

```bash
ros2 pkg executables fr3_moveit_python
```

Expected output:

```text
fr3_moveit_python cartesian_move
```

Check the launch file installation:

```bash
ls ~/franka_ros2_ws/install/fr3_moveit_python/share/fr3_moveit_python/launch/
```

Expected output:

```text
cartesian_move.launch.py
```

---

## Result of July 10

A custom ROS 2 Python package was created for Cartesian motion testing.

Summary:

| Item         | Result                                                  |
| ------------ | ------------------------------------------------------- |
| Package name | `fr3_moveit_python`                                     |
| Build type   | `ament_python`                                          |
| Main script  | `cartesian_move.py` or `move_down_1cm.py`               |
| Launch file  | `cartesian_move.launch.py` or `move_down_1cm_launch.py` |
| Purpose      | Run MoveIt Cartesian motion with full configuration     |

---

## Next Step

The next step is to inspect the official Franka MoveIt launch file and reuse its configuration in the custom launch file.

---

# July 11: Checking Official Franka MoveIt Configuration for Cartesian Motion

## Goal

The goal for July 11 was to inspect the official Franka MoveIt configuration and understand which parameters must be loaded into the custom Cartesian launch file.

The main question was:

```text
What configuration does the official franka_fr3_moveit_config launch file load, and how can I reuse it?
```

This step is important because the custom Python node should not manually guess the robot model, SRDF, kinematics, controller, or planning pipeline. It should reuse the official configuration.

---

## Action 1: Inspect the Official MoveIt Launch File

The official MoveIt launch file was printed:

```bash
sed -n '1,260p' \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch/moveit.launch.py"
```

Command explanation:

```text
sed
    Stream editor.

-n
    Do not print every line automatically.

'1,260p'
    Print only lines 1 through 260.

ros2 pkg prefix franka_fr3_moveit_config
    Shows where the installed franka_fr3_moveit_config package is located.
```

This command helps understand how the official launch file starts MoveIt and which parameters it loads.

---

## Action 2: Search for Important MoveIt Configuration Keywords

The launch directory was searched:

```bash
grep -R -n \
"MoveItConfigsBuilder\|robot_description\|robot_description_semantic" \
"$(ros2 pkg prefix franka_fr3_moveit_config)/share/franka_fr3_moveit_config/launch"
```

This command checks whether the official launch file uses:

```text
MoveItConfigsBuilder
robot_description
robot_description_semantic
```

These are important because MoveIt needs the URDF and SRDF to plan motion.

---

## Action 3: Identify Required MoveIt Parameters

The required MoveIt configuration is:

```python
.robot_description()
.robot_description_semantic()
.robot_description_kinematics()
.joint_limits()
.planning_pipelines()
.trajectory_execution()
.to_moveit_configs()
```

Each item has a specific purpose:

| Configuration                    | Purpose                                                  |
| -------------------------------- | -------------------------------------------------------- |
| `robot_description()`            | Loads the URDF robot model                               |
| `robot_description_semantic()`   | Loads the SRDF semantic model                            |
| `robot_description_kinematics()` | Loads the IK solver configuration                        |
| `joint_limits()`                 | Loads joint velocity and acceleration limits             |
| `planning_pipelines()`           | Loads planning pipelines such as OMPL                    |
| `trajectory_execution()`         | Loads controller execution parameters                    |
| `to_moveit_configs()`            | Converts all loaded configuration into MoveIt parameters |

---

## Action 4: Check Controller Configuration Files

The Franka MoveIt configuration folder was checked:

```bash
cd ~/franka_ros2_ws/src/franka_ros2/franka_fr3_moveit_config/config
```

Important correction:

```text
Use franka_fr3_moveit_config.
Do not use franka_fr2_moveit_config.
```

Then the files were listed:

```bash
ls
```

Relevant controller files may include:

```text
fr3_ros_controllers.yaml
ros2_controllers.yaml
moveit_controllers.yaml
```

---

## Action 5: Understand the Official Controller

The official Franka MoveIt configuration normally uses:

```text
fr3_arm_controller
```

This controller is usually an effort-interface `JointTrajectoryController`.

This is important because it means the controller does not simply accept raw Cartesian commands.

Instead, the pipeline is:

```text
MoveIt computes a joint trajectory.
fr3_arm_controller receives the joint trajectory.
The controller tracks the trajectory.
The hardware command interface outputs effort.
```

---

## Action 6: Understand Effort Interface Control

The official `fr3_arm_controller` is not a simple position-interface controller.

It is usually connected to an effort command interface.

Simplified control logic:

```text
τ = Kp(q_desired - q_actual)
  + Kd(qd_desired - qd_actual)
  + Ki∫(q_error dt)
```

Where:

```text
τ          = effort / torque-like command
q_desired  = desired joint position
q_actual   = actual joint position
qd_desired = desired joint velocity
qd_actual  = actual joint velocity
```

This means:

```text
MoveIt output is not direct torque.
MoveIt output is a joint trajectory.
The controller converts tracking error into effort.
```

---

## Action 7: Check Joint State Topics

Joint-related topics were checked:

```bash
ros2 topic list | grep joint
```

For a non-namespaced setup:

```bash
ros2 topic echo /joint_states
```

For the `fr3` namespace:

```bash
ros2 topic echo /fr3/joint_states
```

Expected result:

```text
The joint state topic should publish current FR3 joint positions and velocities.
```

This is required because MoveIt needs the current robot state before planning.

---

## Action 8: Check Controllers and Hardware Interfaces

Controllers were checked:

```bash
ros2 control list_controllers -c /fr3/controller_manager
```

Hardware interfaces were checked:

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

## Main Technical Conclusion

The main conclusion from July 11 is:

```text
Do not directly command the hardware command interface for Cartesian motion.
```

Reason:

```text
The hardware command interface is too low-level.
Cartesian motion is a high-level planning problem.
```

A Cartesian command such as:

```text
Move the TCP downward by 1 cm.
```

requires:

```text
current end-effector pose
inverse kinematics
joint limits
velocity limits
acceleration limits
trajectory generation
controller execution
```

These are handled by MoveIt, not directly by the hardware command interface.

---

## Correct Motion Pipeline

The correct pipeline is:

```text
Python Cartesian command
    ↓
MoveItPy
    ↓
MoveIt configuration
    ↓
IK and planning
    ↓
Joint trajectory
    ↓
fr3_arm_controller
    ↓
effort command interface
    ↓
franka_hardware
    ↓
libfranka / FCI
    ↓
FR3 robot
```

---

## Incorrect Motion Pipeline

The incorrect approach is:

```text
Python script
    ↓
Directly command effort interface
    ↓
FR3 robot
```

This approach is not suitable because effort commands are low-level controller outputs, not high-level Cartesian motion requests.

---

## Result of July 11

The official Franka MoveIt configuration was selected as the base for the custom Cartesian motion package.

Summary:

| Item                        | Result                                |
| --------------------------- | ------------------------------------- |
| Official MoveIt launch file | Inspected                             |
| `MoveItConfigsBuilder`      | Checked                               |
| URDF / SRDF loading         | Required                              |
| Kinematics config           | Required                              |
| Joint limits                | Required                              |
| Planning pipeline           | Required                              |
| Trajectory execution config | Required                              |
| Controller                  | `fr3_arm_controller`                  |
| Command interface           | Effort                                |
| Final motion method         | MoveItPy + official FR3 MoveIt config |

---

# Current Progress Summary

By July 11, the project had reached the following stage:

```text
Official ROS 2 controller test completed.
Joint states verified.
Controller manager verified.
Generic joint trajectory controller tested.
MoveIt selected as the correct motion planning layer.
MoveIt fake hardware tested.
MoveIt real hardware prepared.
Custom ROS 2 Python package created.
Cartesian MoveItPy script prepared.
Custom launch file planned.
Official FR3 MoveIt configuration inspected.
```

The current project structure is planned as:

```text
Franka_FR3_MoveIt/
├── README.md
├── Requirements.md
├── Development_Log.md
├── docs/
│   ├── Architecture.md
│   ├── Code_OMPL.md
│   └── Troubleshooting.md
├── fr3_moveit_python/
│   ├── __init__.py
│   ├── cartesian_move.py
│   ├── move_down_1cm.py
│   └── move_to_pose.py
├── launch/
│   ├── cartesian_move.launch.py
│   ├── move_down_1cm_launch.py
│   └── fr3_moveit_demo.launch.py
├── resource/
│   └── fr3_moveit_python
├── test/
├── package.xml
├── setup.py
└── setup.cfg
```

---

# Next Tasks

The next tasks are:

```text
1. Finalize cartesian_move.py.
2. Finalize cartesian_move.launch.py.
3. Make sure the launch file loads the official FR3 MoveIt configuration.
4. Build the fr3_moveit_python package.
5. Test planning only with execute:=false.
6. Verify /fr3_arm_controller/follow_joint_trajectory action server.
7. Add a short delay before execution if the MoveItPy action client is not connected yet.
8. Test small Cartesian motion first, such as dz:=-0.005.
9. Increase motion only after the small test is stable.
```

Recommended first real hardware test:

```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py \
  dz:=-0.005 \
  execute:=false
```

Then, only after planning is verified:

```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py \
  dz:=-0.005 \
  execute:=true
```

---

# Engineering Notes

## Why the Official Example Controller Was Tested First

The official example controller is the best first test because it removes custom code from the debugging process.

If the official controller works, then the robot connection, FCI, `libfranka`, and controller manager are probably correct.

If the official controller does not work, then writing custom MoveIt code will not solve the problem.

---

## Why MoveIt Was Chosen

MoveIt was chosen because Cartesian motion requires high-level motion planning.

A command like:

```text
Move TCP downward by 1 cm.
```

is not directly a joint command and not directly an effort command.

MoveIt converts this high-level Cartesian goal into a safe joint trajectory.

---

## Why a Custom Launch File Is Needed

The custom Python node needs the same configuration as the official MoveIt launch file.

This includes:

```text
URDF
SRDF
kinematics
joint limits
planning pipeline
trajectory execution
controller information
```

Without these parameters, the Python node may start but cannot plan or execute correctly.

---

## Why Direct Hardware Interface Command Is Not Used

The hardware command interface is only the final low-level control layer.

For FR3 Cartesian motion, the proper route is:

```text
MoveIt → controller → hardware interface
```

not:

```text
Python → hardware interface
```

This makes the motion safer and more compatible with the official Franka ROS 2 pipeline.


## Troubleshooting Guide

This document covers common issues when building and running the **Franka FR3 MoveIt Cartesian Motion Demo** on **native Ubuntu 24.04 with ROS 2 Jazzy**.


## 1. ROS 2 Environment Not Sourced

### Problem

Commands cannot find ROS 2 packages.

Example:

ros2: command not found

or:

Package 'fr3_moveit_python' not found

## Cause

ROS 2 environment is not loaded.

## Solution

Source ROS 2:

```bash
source /opt/ros/jazzy/setup.bash

Source workspace:

source ~/franka_ros2_ws/install/setup.bash
```
To automatically source:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```
2. Workspace Build Failed
Problem
colcon build fails.
Example:

Failed <<< fr3_moveit_python
Possible Causes
Missing dependencies
Incorrect package structure
Python syntax error
Wrong ROS 2 package format
Solution

Install dependencies:

```bash
cd ~/franka_ros2_ws

rosdep install \
--from-paths src \
--ignore-src \
-r -y
```
Clean build:
```bash
rm -rf build install log
```
Rebuild:
```bash
colcon build --symlink-install
```
3. Python Package Structure Incorrect
Problem: ROS 2 cannot find the Python node.

Make sure:
```bash
chmod +x fr3_moveit_python/cartesian_move.py
```
4. Python Node Not Installed as ROS 2 Executable
Problem
Command:
```bash
ros2 pkg executables fr3_moveit_python
```
does not show:
```bash
cartesian_move
Cause
```
Missing entry_points in setup.py.

Solution

Add:
```bash
entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
    ],
},
```
Rebuild:
```bash
colcon build --symlink-install
```
5. Launch File Not Installed
Problem

Running:
```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py
```
returns:

file not found
Cause

Launch file is not included in package installation.

Solution

Check setup.py:
```bash
data_files=[
(
'share/fr3_moveit_python/launch',
[
'launch/cartesian_move.launch.py'
]
)
]
```
Rebuild:
```bash
colcon build --symlink-install
```
Verify:

ls install/fr3_moveit_python/share/fr3_moveit_python/launch

6. MoveIt Package Not Found
Error:
Package 'franka_fr3_moveit_config' not found
Cause:

Official Franka MoveIt package is not built or sourced.

Solution

Check:
```bash
ros2 pkg list | grep franka_fr3_moveit_config
```
Build:
```bash
colcon build \
--packages-select franka_fr3_moveit_config
```
Source:
```bash
source install/setup.bash
```
7. Missing MoveItPy Dependency
Problem:
- Python error:
- ModuleNotFoundError:
- No module named moveit
Cause:
MoveIt 2 Python interface is missing.

Solution
Install:
```bash
sudo apt install \
ros-jazzy-moveit
```
Check:
```bash
ros2 pkg list | grep moveit
```
8. robot_description Not Loaded
Problem

MoveIt starts but cannot load robot model.

Example: Robot model loading failed
Cause:
Official Franka MoveIt configuration is not loaded correctly.

Check:
```bash
ros2 param list | grep robot_description
```
Solution
```bash
The launch file must load:

.robot_description()
```
from: franka_fr3_moveit_config

9. robot_description_semantic Missing
Problem

Error:
```bash

Planning group fr3_arm does not exist
Cause
```
SRDF is not loaded.

Solution
```bash
Ensure:

.robot_description_semantic()
```
is included.

The SRDF defines:
```bash
planning group
end effector
collision information
```
10. Controller Manager Not Available
Problem:

Error:
```
Could not contact service:
/controller_manager/list_controllers
```
Cause: Franka hardware interface is not running.

Check:
```bash
ros2 node list
```
Expected:
```bash
/fr3/controller_manager
```
Solution:

Launch Franka hardware:
```bash
ros2 launch franka_bringup ...
```
11. Controller Not Active
Problem

Planning works but execution fails.

Check:
```bash
ros2 control list_controllers
```
Expected:
```bash
fr3_arm_controller active
joint_state_broadcaster active
franka_robot_state_broadcaster active
```
Solution: Activate controller

```bash
ros2 control set_controller_state \
fr3_arm_controller active
```
12. /joint_states Missing
Problem: MoveIt cannot plan.
Check:
```bash
ros2 topic echo /joint_states
```
Cause:

Joint state broadcaster is not running.

Solution

Start:

joint_state_broadcaster

and verify:
```bash
ros2 topic list | grep joint
```
13. libfranka Connection Timeout
Problem
```bash
https://frankarobotics.github.io/docs/troubleshooting.html#running-a-libfranka-executable-fails-with-connection-timeout
```
Error:

```bash
libfranka: Connection timeout
Possible Causes
Wrong robot IP
Ethernet configuration incorrect
Robot not connected
FCI disabled
```
Check:
ping <robot_ip>

Example:
```
ping 192.168.0.1
```
PC should have:

192.168.0.x
14. Ethernet Configuration Problem
Problem

Robot cannot communicate with PC.

Check network:
```bash
ip a
```
Find Ethernet interface:

enp0s31f6

Assign static IP if needed:

Example:

PC:
192.168.0.10

Robot:
192.168.0.1
15. MoveIt Planning Works but Execution Fails
Problem

Output:

Planning successful
Action client not connected
Cause

DDS discovery delay.

Solution

Add delay before execution:
```bash
time.sleep(5)

moveit.execute()
```

16. Cartesian Motion Planning Failed (Moveit)
Problem:
```bash
Cartesian path fraction = 0
Possible Causes
Target unreachable
Wrong TCP link
Collision
Large displacement
```
Solution

Test small movement:
dz:=-0.005
```bash
ros2 launch fr3_moveit_python   cartesian_move.launch.py   dz:=-0.005   execute:=true
```
before:
dz:=-0.05
```bash
ros2 launch fr3_moveit_python   cartesian_move.launch.py   dz:=-0.05   execute:=true
```

17. Wrong ROS 2 Distribution
Problem: Compilation errors related to:
```bash
hardware_interface
controller_manager
```
Cause:

Package versions do not match ROS distribution.

Required:
```bash
Ubuntu 24.04
ROS 2 Jazzy
Franka ROS 2 Jazzy branch
```
Check:
```bash
echo $ROS_DISTRO
```
Expected:

jazzy

18. Clean Rebuild After Configuration Changes

When changing:
```bash
launch files
setup.py
package.xml
MoveIt configuration
```
perform:
```bash

cd ~/franka_ros2_ws

rm -rf build install log

colcon build --symlink-install

source install/setup.bash
```
Debug Checklist

Before running:
```bash
ros2 launch fr3_moveit_python \
cartesian_move.launch.py \
dz:=-0.01 \
execute:=true
```
Verify:
```bash
 ROS 2 Jazzy sourced
 Workspace sourced
 Package builds successfully
 Franka MoveIt config available
 Robot connected through Ethernet
 FCI enabled
 /joint_states publishing
 Controllers active
 MoveIt planning successful
 Small Cartesian motion tested first

```

July 16th: 

Quesion:

ros2 run fr3_moveit_python gripper_control
:No executable found


ros2 pkg executables fr3_moveit_python
fr3_moveit_python cartesian_move

Step 1: Check your setup.py

Open:

cd ~/franka_ros2_ws/src/fr3_moveit_python

gedit setup.py

Step 1: Check your setup.py

Open:

cd ~/franka_ros2_ws/src/fr3_moveit_python

gedit setup.py

Find:

entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
    ],
},

Change it to:

entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
        'gripper_control = fr3_moveit_python.gripper_control:main',
    ],
},

Save.

Step 2: Verify file name

Check:

ls ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python

You should see:

__init__.py
cartesian_move.py
gripper_control.py

Step 3: Rebuild only your package

Go to workspace:

cd ~/franka_ros2_ws

Build:

colcon build --packages-select fr3_moveit_python

You should see:

Finished <<< fr3_moveit_python

Step 4: Source the new installation

Important:

source install/setup.bash

or:

source ~/franka_ros2_ws/install/setup.bash
tep 5: Check again

Run:

ros2 pkg executables fr3_moveit_python

Expected:

fr3_moveit_python cartesian_move
fr3_moveit_python gripper_control
Step 6: Run your gripper

Before running, check the action exists:

ros2 action list | grep gripper

Expected:

/fr3_gripper/gripper_action

Then:

ros2 run fr3_moveit_python gripper_control



ros2 action info /fr3_gripper/gripper_action


Expected to see:

Action: franka_msgs/action/Grasp
or:
Action: franka_msgs/action/Move

Actual:

Action: /fr3_gripper/gripper_action
Action clients: 1
    /moveit_simple_controller_manager
That means:

/fr3_gripper/gripper_action exists in the ROS graph
but nobody is actually providing the action server
MoveIt is only acting as an action client

Due to:
 ros2 action info /franka_gripper/move
Action: /franka_gripper/move
Action clients: 0
Action servers: 1
    /franka_gripper
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 action info /franka_gripper/grasp
Action: /franka_gripper/grasp
Action clients: 0
Action servers: 1
    /franka_gripper
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 action info /franka_gripper/move
Action: /franka_gripper/move
Action clients: 0
Action servers: 1
    /franka_gripper

THus
 from control_msgs.action import GripperCommand >>>  from franka_msgs.action import Move




ros2 run fr3_moveit_python gripper_control
AttributeError: 'Move_Result' object has no attribute 'current_width'
[ros2run]: Process exited with failure 1

In ROS 2 actions, the structure is:

Goal
---
Result
---
Feedback


```bash
ros2 interface show franka_msgs/action/Move
float64 width  # [m]
float64 speed  # [m/s]
---
bool success
string error
---
float64 current_width # [m]
```

float64 current_width is feedback, not result.


e incorrectly does:

result.current_width
but result only contains:

bool success
string error
he important part:

AttributeError: 'Move_Result' object has no attribute 'current_width'

means your installed franka_msgs/action/Move does not contain current_width in the result message, even though your earlier:

ros2 interface show franka_msgs/action/Move

showed:

float64 width
float64 speed
---
bool success
string error
---
float64 current_width

In ROS 2 actions, the structure is:

Goal
---
Result
---
Feedback

The last section:

float64 current_width

is feedback, not result.

Your code incorrectly does:

result.current_width

but result only contains:

bool success
string error
Fix your code

Replace:

if result.success:

    self.get_logger().info(
        f"Gripper reached {result.current_width:.3f} m"
    )

with:

if result.success:

    self.get_logger().info(
        "Gripper motion completed successfully."
    )

else:

    self.get_logger().error(
        result.error
    )
If you want to display current width

You need to use feedback.

Change:

future = self.client.send_goal_async(goal)

to:

future = self.client.send_goal_async(
    goal,
    feedback_callback=self.feedback_callback
)

Add this function inside your class:

def feedback_callback(self, feedback_msg):

    feedback = feedback_msg.feedback

    self.get_logger().info(
        f"Current width: {feedback.current_width:.3f} m"
    )

Now you will see:

Current width: 0.073 m
Current width: 0.041 m
Current width: 0.012 m

during motion.

Then rebuild
cd ~/franka_ros2_ws

colcon build --packages-select fr3_moveit_python

source install/setup.bash

Run:

ros2 run fr3_moveit_python gripper_control

Expected:

[INFO] Connected to Franka gripper.
[INFO] Gripper goal accepted
[INFO] Gripper motion completed successfully.



```bash
import rclpy
from rclpy.node import Node


class RobotMotion(Node):

    def __init__(self):
        super().__init__("robot_motion")
        print("Robot node started")


def main():

    rclpy.init()

    robot = RobotMotion()

    rclpy.spin(robot)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
```
```bash
Python file
│
├── import libraries
│
├── define classes
│       |
│       └── RobotMotion
│
└── main()
        |
        ├── initialize ROS2
        ├── create robot node
        ├── run robot
        └── shutdown
```

---


### July 19th — Troubleshooting Log

### Issue:
'GripperController' object has no attribute 'open_gripper'

### Symptom:

Running pick-place related code produced:

AttributeError:

'GripperController' object has no attribute 'open_gripper'

However, the function existed in the source file.


### Investigation:
### Step 1: Check installed package version

Command:
```bash
grep -n "open_gripper" \
~/franka_ros2_ws/install/fr3_moveit_python/lib/python3.12/site-packages/fr3_moveit_python/gripper_control.py
```

Output:
```bash
110:    def open_gripper(self):
142:    gripper.open_gripper()
```

### Step 2: Compare source workspace

Command:
```bash
grep -n "def open_gripper" \
~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/gripper_control.py
```
Output:

110:    def open_gripper:

Conclusion:

The function existed in both:
```bash
src/      and       install/
```
Therefore, the issue was not missing code.

### Root Cause Analysis

### Cause 1: Mixed workspace / wrong environment

Possible reasons:
```bash
- Multiple ROS2 workspaces exist.
- Terminal sourced another workspace.
- ROS executed an old installed package.
- Workspace was not sourced after rebuilding.
```
Verification:

```bash
ros2 pkg prefix fr3_moveit_python
ros2 pkg executables fr3_moveit_python
which python3
echo $PYTHONPATH
```
Send message:
```bash
ros2 action send_goal \
/franka_gripper/move \
franka_msgs/action/Move \
"{width: 0.00, speed: 0.05}"
```
Result: Action server confirmed working.

Final Debugging Procedure
1. Verify hardware interface
```bash
ros2 action list
```
3. Test official gripper command
```bash
ros2 action send_goal \
/franka_gripper/move \
franka_msgs/action/Move \
"{width: 0.00, speed: 0.05}"
```
5. Verify package location
```bash
ros2 pkg prefix fr3_moveit_python
```
7. Verify executable registration
```bash
ros2 pkg executables fr3_moveit_python
```
9. Check Python entry point
```bash
cat setup.py ( franka_ros2_ws/fr3_moveit_python/setup.py
```
Confirm:
```bash
gripper_control =
fr3_moveit_python.gripper_control:main
```
6. Rebuild workspace
```bash
colcon build --symlink-install
source install/setup.bash
```
7. Run test node
```bash
ros2 run fr3_moveit_python gripper_control
```

---


Question:
Could not find parameter robot_description_semantic

Original code:

```bash
def main():
    rclpy.init()

    moveit = MoveItPy(
        node_name="pick_place"
    )

    arm = moveit.get_planning_component(
        "fr3_arm"
    )

    robot_model = moveit.get_robot_model()

    robot_state = RobotState(
        robot_model
    )

    arm.set_start_state(
        robot_state
    )
```


 moveit = MoveItPy(
[pick_place-1] RuntimeError: Unable to configure planning scene monitor)

Cause:
the wrong way for moveit.py

Example: 

```bash
import rclpy
from moveit.planning import MoveItPy

# Initialize ROS 2
rclpy.init()

# Instantiate MoveItPy for the current ROS 2 node/context
moveit_py = MoveItPy(node_name="moveit_py_example")

# Get the planning component for a pre-defined manipulator arm (e.g., "panda_arm")
panda_arm = moveit_py.get_planning_component("panda_arm")

# Plan to a joint space goal
panda_arm.set_goal_state(configuration_name="ready")
plan_result = panda_arm.plan()

# Execute the planned trajectory if planning was successful
if plan_result:
    moveit_py.execute(plan_result.trajectory)

rclpy.shutdown()
```

## July 20th:

TypeError: set_goal_state(): incompatible function arguments

 
    # ==========================
    # OMPL
    # ==========================

    ompl_yaml = load_yaml(
        "franka_fr3_moveit_config",
        "config/ompl_planning.yaml",
    )

    ompl = {
        "planning_plugins": [
            "ompl_interface/OMPLPlanner",
        ]
    }
    ompl.update(ompl_yaml)

----

## July 20th — MoveItPy Execution Pipeline Debugging Log

### Issue

MoveItPy could successfully generate a motion plan, but trajectory execution was initially rejected by `fr3_arm_controller`.

Main failure:

```text
Goal request rejected
Goal was rejected by server
Completed trajectory execution with status ABORTED
```

The problem was not mainly in the high-level task logic.  
The debugging focus was the connection between:

```text
MoveItPy
    ↓
OMPL planner
    ↓
MoveIt trajectory execution
    ↓
FollowJointTrajectory action
    ↓
fr3_arm_controller
    ↓
Franka FR3
```

---

### Background

The intended execution pipeline was:

```text
MoveItPy
    ↓
OMPL planning
    ↓
Joint trajectory
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

The system environment was:

```text
ROS 2 Jazzy
MoveIt 2
MoveItPy
franka_ros2
Franka FR3
OMPL
JointTrajectoryController
```

---

### Symptom 1 — MoveItPy API Usage Error

The first issue was caused by incompatible MoveItPy API usage.

Observed error:

```text
TypeError: set_start_state(): incompatible function arguments
```

The start state was originally passed with an incompatible argument format.

The corrected approach was to use the planning component's current state interface:

```text
Use current robot state through the planning component.
Do not directly call get_current_state() from RobotModel.
```

---

### Symptom 2 — Goal State Format Error

A second API error occurred when setting the goal state.

Observed error:

```text
TypeError: set_goal_state(): incompatible function arguments
```

The issue was caused by passing joint targets in an unsupported format.

The corrected approach was:

```text
Create a RobotState.
Set joint group positions using a NumPy array.
Pass the RobotState as the goal state.
```

Important note:

```text
set_joint_group_positions() requires numpy.ndarray.
```

---

### Symptom 3 — RobotModel Current State Error

Another error appeared:

```text
AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'
```

Root cause:

```text
RobotModel only describes the robot model.
It does not provide the live current robot state.
```

Resolution:

```text
Use the PlanningComponent current-state method instead of reading current state from RobotModel.
```

---

### Investigation 1 — Controller Status

Command:

```bash
ros2 control list_controllers
```

Result:

```text
fr3_arm_controller             joint_trajectory_controller/JointTrajectoryController       active
joint_state_broadcaster        joint_state_broadcaster/JointStateBroadcaster               active
franka_robot_state_broadcaster franka_robot_state_broadcaster/FrankaRobotStateBroadcaster  active
```

Conclusion:

```text
fr3_arm_controller was active.
```

Therefore, the failure was not caused by an inactive controller.

---

### Investigation 2 — FollowJointTrajectory Action Server

Command:

```bash
ros2 action list -t | grep FollowJointTrajectory
```

Result:

```text
/fr3_arm_controller/follow_joint_trajectory [control_msgs/action/FollowJointTrajectory]
```

Command:

```bash
ros2 action info /fr3_arm_controller/follow_joint_trajectory
```

Result:

```text
Action clients: 1
    /moveit_simple_controller_manager

Action servers: 1
    /fr3_arm_controller
```

Conclusion:

```text
MoveIt could see the FollowJointTrajectory action server.
```

Therefore, the failure was not caused by a missing action server.

---

### Investigation 3 — Controller Interfaces

Command:

```bash
ros2 param get /fr3_arm_controller command_interfaces
ros2 param get /fr3_arm_controller state_interfaces
```

Result:

```text
String values are: ['effort']
String values are: ['position', 'velocity']
```

Conclusion:

```text
fr3_arm_controller uses effort command interface and position/velocity state interfaces.
```

This matched the expected Franka MoveIt controller configuration.

---

### Investigation 4 — Hardware Interfaces

Command:

```bash
ros2 control list_hardware_interfaces
```

Important result:

```text
fr3_joint1/effort [available] [claimed]
fr3_joint2/effort [available] [claimed]
fr3_joint3/effort [available] [claimed]
fr3_joint4/effort [available] [claimed]
fr3_joint5/effort [available] [claimed]
fr3_joint6/effort [available] [claimed]
fr3_joint7/effort [available] [claimed]
```

Conclusion:

```text
The arm controller successfully claimed all seven FR3 effort interfaces.
```

Therefore, the controller had access to the required hardware command interfaces.

---

### Investigation 5 — Joint State Topic

Command:

```bash
ros2 topic echo /joint_states --once
```

Result:

```text
name:
- fr3_joint1
- fr3_joint2
- fr3_joint3
- fr3_joint4
- fr3_joint5
- fr3_joint6
- fr3_joint7
- fr3_finger_joint1
- fr3_finger_joint2
```

Conclusion:

```text
/joint_states contained all required FR3 arm joints.
```

Therefore, MoveIt had access to the current robot state.

---

### Investigation 6 — Direct Controller Action Test

A direct action goal was sent to `fr3_arm_controller`.

Command:

```bash
ros2 action send_goal /fr3_arm_controller/follow_joint_trajectory \
control_msgs/action/FollowJointTrajectory \
"{trajectory: {joint_names: ['fr3_joint1', 'fr3_joint2', 'fr3_joint3', 'fr3_joint4', 'fr3_joint5', 'fr3_joint6', 'fr3_joint7'], points: [{positions: [-0.125, -0.114, 0.340, -1.512, -0.050, 1.434, -2.302], velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 5, nanosec: 0}}]}}"
```

Result:

```text
Goal successfully reached!
Goal finished with status: SUCCEEDED
```

Conclusion:

```text
fr3_arm_controller, action server, hardware interface, FCI connection, and real robot execution path were working correctly.
```

This isolated the issue to the MoveItPy launch/planning configuration rather than the robot controller or hardware.

---

### Root Cause Analysis

The direct controller action succeeded, but MoveItPy trajectory execution was rejected.

Therefore, the issue was not caused by:

```text
controller inactive
missing action server
wrong joint names
missing joint states
unclaimed hardware interface
FCI failure
robot hardware failure
```

The issue was caused by incomplete MoveIt planning and execution configuration in the custom launch file.

The earlier warning was:

```text
No planning request adapter names specified.
No planning response adapter names specified.
```

This indicated that the planning pipeline was not fully configured.

MoveIt could generate a geometric plan, but the trajectory was not correctly prepared for controller execution.

---

### Launch File Fix

The custom launch file was updated to explicitly define:

```text
OMPL planning plugin
planning request adapters
planning response adapters
start state bound checking
velocity scaling
acceleration scaling
controller configuration
trajectory execution configuration
```

Important correction:

```text
Use planning_plugin, not planning_plugins.
```

The incorrect plural form caused MoveIt to report:

```text
Planning plugin name is empty or not defined in namespace 'ompl'
```

Correct OMPL configuration structure:

```python
ompl_yaml = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)

ompl = {}
ompl.update(ompl_yaml)

ompl.update({
    "planning_plugin": "ompl_interface/OMPLPlanner",

    "request_adapters": (
        "default_planning_request_adapters/ResolveConstraintFrames "
        "default_planning_request_adapters/ValidateWorkspaceBounds "
        "default_planning_request_adapters/CheckStartStateBounds "
        "default_planning_request_adapters/CheckStartStateCollision"
    ),

    "response_adapters": (
        "default_planning_response_adapters/AddTimeOptimalParameterization "
        "default_planning_response_adapters/ValidateSolution "
        "default_planning_response_adapters/DisplayMotionPath"
    ),

    "start_state_max_bounds_error": 0.1,
})
```

Plan request parameters were also completed:

```python
"plan_request_params": {
    "planning_pipeline": "ompl",
    "planner_id": "RRTConnectkConfigDefault",
    "planning_time": 5.0,
    "max_velocity_scaling_factor": 0.05,
    "max_acceleration_scaling_factor": 0.05,
}
```

---

### Final Result

After fixing the MoveItPy API usage and the custom launch configuration, trajectory execution succeeded.

Final successful behavior:

```text
Calling Planner 'OMPL'
Goal request accepted
Controller 'fr3_arm_controller' successfully finished
Completed trajectory execution with status SUCCEEDED
```

This confirmed the full execution pipeline:

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

---

### Current Project Status

Verified components:

```text
FR3 hardware connection                    
Franka FCI                                 
ROS 2 Jazzy environment                    
MoveIt 2 configuration                     
MoveItPy API usage                         
OMPL planner loading                       
fr3_arm planning group                     
Joint trajectory generation                
FollowJointTrajectory action connection    
fr3_arm_controller execution              
Effort interface control                   
Real robot motion execution                
```

---

### Technical Conclusion

The main technical conclusion is:

```text
Planning success does not guarantee execution success.
```

For real robot execution, the following must all be valid:

```text
MoveItPy API usage
planning group
current robot state
OMPL planning pipeline
planning adapters
trajectory timing
controller configuration
FollowJointTrajectory action server
claimed hardware interfaces
real robot FCI connection
```

The final fix was not mainly in the high-level task script.

The critical fix was in the custom MoveIt launch configuration.

---

### Next Actions

```text
1. Clean up the custom launch file.
2. Keep direct FollowJointTrajectory action command as a hardware verification test.
3. Move reusable arm motion logic into motion.py.
4. Keep high-level pick-and-place task logic separate from reusable motion APIs.
5. Add gripper open/close sequence.
6. Add Cartesian approach and retreat motion.
7. Test pick-and-place with small safe motions first.
8. Update Troubleshooting.md with this debugging chain.
```

---

### July 21 — MoveItPy Arm Execution Mistakes Log

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
### Mistake 1 — Wrong Current State Usage
Problem:
 get the live robot state from RobotModel.

Error
AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'
Fix

RobotModel only describes the robot model.
The current robot state should be handled through the MoveItPy planning component.

### Mistake 2 — Wrong Goal State Format
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
### Mistake 3 — Misdiagnosing Execution Failure as Hardware Failure
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

### Mistake 4 — Wrong OMPL Plugin Parameter
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

### Mistake 5 — Missing Planning Adapters for Time Sequence
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

### Mistake 6 — Missing Velocity and Acceleration Scaling
Problem:

The launch file did not define:

max_velocity_scaling_factor
max_acceleration_scaling_factor
Fix

Add safe velocity and acceleration scaling parameters for real robot execution.

Example values:
```bash
max_velocity_scaling_factor: 0.05
max_acceleration_scaling_factor: 0.05
Mistake 7 — Misleading Execution Output
```
Problem

The script printed:

Execution finished

even when MoveIt reported:

Completed trajectory execution with status ABORTED
Fix

Only print execution success after checking the actual execution result.

Final Fix Summary

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
Final Result

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

Next Actions:
```bash
1. Clean up the custom MoveIt launch file.
2. Keep direct FollowJointTrajectory command as a hardware test.
3. Refactor reusable arm motion logic into motion.py.
4. Keep high-level task logic separate from reusable motion APIs.
5. Add Cartesian approach and retreat motion for the arm.
6. Test small safe arm motions first.
7. Update Troubleshooting.md with the OMPL plugin and adapter issue.
```

### July 20 — MoveItPy Arm Execution Development Log

### Goal

Verify that the Franka FR3 arm can execute a planned trajectory through **MoveItPy**, **OMPL**, and `fr3_arm_controller`.

Gripper integration is postponed.  
Today focuses only on the arm execution pipeline.

---

### Tested Pipeline

```text
MoveItPy
    ↓
OMPL planner
    ↓
Joint trajectory
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
Initial Problem

MoveItPy could generate a plan, but execution was rejected by the controller.

Goal request rejected
Goal was rejected by server
Completed trajectory execution with status ABORTED

This means:

Planning succeeded, but trajectory execution failed.
Verification

The robot-side execution pipeline was checked first.

Verified results:

- fr3_arm_controller active                         
- FollowJointTrajectory action server available     
- MoveIt action client connected                    
- FR3 effort command interfaces claimed             
- /joint_states publishing FR3 joints               
- Direct FollowJointTrajectory command succeeded    

A direct action command to fr3_arm_controller succeeded, proving that the controller, FCI, hardware interface, and real robot were working.

Therefore, the issue was not the robot hardware.

Root Cause

The main issue was in the custom MoveIt launch configuration.

The OMPL planning plugin and planning adapters were not configured correctly.

Main plugin bug:
```bash
planning_plugins    wrong
planning_plugin     correct
```
The wrong parameter caused:

Planning plugin name is empty or not defined in namespace 'ompl'
Adapter / Time Sequence Fix

MoveIt planning success only means OMPL found a geometric path.

For real controller execution, the trajectory also needs a valid time sequence:

time_from_start
velocity
acceleration
trajectory timing

This requires planning response adapters.

Important adapter:

default_planning_response_adapters/AddTimeOptimalParameterization

Purpose:

AddTimeOptimalParameterization converts the planned path into a time-parameterized trajectory.

Without this adapter, MoveIt may generate a path, but fr3_arm_controller can reject the goal because the trajectory is not properly timed.

Launch Configuration Fix

The custom launch file was updated to include:

OMPL planning plugin
request adapters
response adapters
velocity scaling
acceleration scaling
controller configuration
trajectory execution configuration

Key configuration:
```bash
ompl.update({
    "planning_plugin": "ompl_interface/OMPLPlanner",

    "request_adapters": (
        "default_planning_request_adapters/ResolveConstraintFrames "
        "default_planning_request_adapters/ValidateWorkspaceBounds "
        "default_planning_request_adapters/CheckStartStateBounds "
        "default_planning_request_adapters/CheckStartStateCollision"
    ),

    "response_adapters": (
        "default_planning_response_adapters/AddTimeOptimalParameterization "
        "default_planning_response_adapters/ValidateSolution "
        "default_planning_response_adapters/DisplayMotionPath"
    ),

    "start_state_max_bounds_error": 0.1,
})
```
Plan request parameters were also completed:
```bash
"plan_request_params": {
    "planning_pipeline": "ompl",
    "planner_id": "RRTConnectkConfigDefault",
    "planning_time": 5.0,
    "max_velocity_scaling_factor": 0.05,
    "max_acceleration_scaling_factor": 0.05,
}
```



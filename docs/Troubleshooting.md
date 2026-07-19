
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

## July 19th: 'GripperController' object has no attribute 'open_gripper'
Reason:
The structure of gripper_control.py

```bash
grep -n "open_gripper" \
~/franka_ros2_ws/install/fr3_moveit_python/lib/python3.12/site-packages/fr3_moveit_python/gripper_control.py
```
110:    def open_gripper(self):
142:    gripper.open_gripper()

```bash
grep -n "def open_gripper" \
~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python/gripper_control.py
```
110:    def open_gripper(self):

Final debugging order:

1. Check action server:

ros2 action list


2. Test official command:

ros2 action send_goal \
/franka_gripper/move \
franka_msgs/action/Move \
"{width: 0.00, speed: 0.05}"


3. Check ROS sees your package:

ros2 pkg executables fr3_moveit_python


4. Check your entry point:

cat setup.py


5. Rebuild:

colcon build --symlink-install

source install/setup.bash


6. Run:

ros2 run fr3_moveit_python gripper_control


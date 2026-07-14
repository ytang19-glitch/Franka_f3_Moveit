## Component Responsibilities

### setup.py 

Registers and installs the ROS 2 Python package during colcon build.

### cartesian_move.launch.py

Adapted from the official franka_fr3_moveit_config launch files. 
It reuses the official MoveIt and robot configuration while launching the complete runtime environment, including:
- MoveIt
- ROS 2 controllers
- RViz
- The custom application node (cartesian_move.py).

### cartesian_move.py

– Implements the robot's Cartesian motion logic using the MoveIt Python API.


### Architecture:


#### Overall Architecture

```bash
User
   │
   ▼
cartesian_move.launch.py
   │
   ▼
cartesian_move.py
   │
   ▼
MoveIt Python API
   │
   ▼
MoveIt Planning Pipeline
   │
   ▼
ROS2 Controllers
   │
   ▼
Franka Driver
   │
   ▼
FR3
```

#### Architecture (Build vs Runtime)

#### Build time
```bash

                Build Time
──────────────────────────────────────

package.xml
      │
setup.py
      │
colcon build
      │
Executable Installed
      │
──────────────────────────────────────
```
#### Runtime
```bash
               Runtime
──────────────────────────────────────


ros2 launch
      │
cartesian_move.launch.py
      │
cartesian_move.py
      │
MoveIt python API
      │
ROS2 Controllers
      │
Franka Driver
      │
Franka FR3

──────────────────────────────────────
```
#### EXplain:

- MoveIt Config:	Robot configuration
- ROS2 Controllers:	Execute trajectories
- libfranka:	Hardware communication




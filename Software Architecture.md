## Component Responsibilities

setup.py 
```bash
– Registers and installs the ROS 2 Python package during colcon build.
```

cartesian_move.launch.py
```text
– Starts the complete runtime environment, including MoveIt, ROS 2 controllers, RViz, and the application node.
```

cartesian_move.py
```text
– Implements the robot's Cartesian motion logic using the MoveIt Python API.
```

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

               Runtime
──────────────────────────────────────

ros2 launch
      │
cartesian_move.launch.py
      │
cartesian_move.py
      │
MoveIt
      │
ROS2 Controllers
      │
Franka Driver
      │
Franka FR3
```

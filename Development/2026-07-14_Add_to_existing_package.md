# July 14 — Add to existing package


## July 14 — Add Pick-and-Place Files to Existing Package

### Goal

Add the gripper-control and pick-and-place files to the existing `fr3_moveit_python` ROS 2 package instead of creating a separate package.

Create the new Python files inside the package source directory:

```bash
cd ~/franka_ros2_ws/src/fr3_moveit_python/fr3_moveit_python

touch gripper_control.py
touch pick_place.py
```

The package now contains:

```text
fr3_moveit_python/
├── cartesian_move.py
├── gripper_control.py
└── pick_place.py
```

Update `setup.py` so that `gripper_control.py` can be executed as a ROS 2 node:

```python
entry_points={
    'console_scripts': [
        'cartesian_move = fr3_moveit_python.cartesian_move:main',
        'gripper_control = fr3_moveit_python.gripper_control:main',
    ],
},
```

At this stage, `pick_place.py` was created for later integration but was not yet added as a console-script entry point.

---

### Test

#### Step 1 
Rebuild the package after modifying `setup.py`:

```bash
cd ~/franka_ros2_ws

colcon build --packages-select fr3_moveit_python
source install/setup.bash
```
#### Step 2

Confirm that the executable is available:

```bash
ros2 pkg executables fr3_moveit_python
```

Expected executables:

```text
fr3_moveit_python cartesian_move
fr3_moveit_python gripper_control
```

#### Step 3 

Run the gripper-control node:

```bash
ros2 run fr3_moveit_python gripper_control
```

The `pick_place.py` file cannot yet be started with `ros2 run` because it has not been added to `setup.py`.

---

### Conclusion

The existing `fr3_moveit_python` package was extended with two new files:

```text
gripper_control.py
    = gripper testing and control logic

pick_place.py
    = future high-level pick-and-place sequence
```

`gripper_control` was added as a ROS 2 executable through `setup.py`.

`pick_place.py` was created as the future task-orchestration file and can be added as an executable after its `main()` function is implemented.

---
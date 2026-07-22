# July 9 — Choosing MoveIt as the Main Motion Layer


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

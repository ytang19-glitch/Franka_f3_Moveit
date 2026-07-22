# July 11 — Inspecting Official Franka MoveIt Configuration


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
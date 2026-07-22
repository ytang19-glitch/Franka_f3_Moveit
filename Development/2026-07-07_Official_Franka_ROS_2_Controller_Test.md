# July 7 — Official Franka ROS 2 Controller Test


### Goal

Verify that the official `franka_ros2` package can communicate with the real FR3 hardware before writing any custom motion code.

### Test

The official example controller was launched:

```bash
ros2 launch franka_bringup example.launch.py \
  controller_names:=joint_position_example_controller \
  robot_ips:=172.16.0.2 \
  namespace:=fr3
```

Then the controllers and joint state topics were checked:

```bash
ros2 control list_controllers -c /fr3/controller_manager
ros2 topic list | grep joint
ros2 topic echo /fr3/joint_states --once
```

### Observation

The robot published joint states, and the controller manager was working.

However, `joint_position_example_controller` did not expose a normal command topic.

```bash
ros2 topic info /fr3/joint_position_example_controller/commands
```

Result:

```text
Unknown topic
```

### Conclusion

This is expected. The official `joint_position_example_controller` is mainly a demo/test controller.

It verifies:

```text
ROS 2 Control → franka_hardware → libfranka → FCI → FR3
```

but it is not intended for custom user-defined motion.

### Decision

Use the official controller only for system verification.
Test a trajectory controller next for custom motion.

---

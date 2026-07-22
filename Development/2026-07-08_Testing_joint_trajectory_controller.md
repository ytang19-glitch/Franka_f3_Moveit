# July 8 — Testing `joint_trajectory_controller`


### Goal

Test whether a standard ROS 2 `JointTrajectoryController` can be used for custom joint-space motion.

### Test

A `joint_trajectory_controller` was added to `controllers.yaml` and configured for the seven FR3 joints:

```text
fr3_joint1
fr3_joint2
fr3_joint3
fr3_joint4
fr3_joint5
fr3_joint6
fr3_joint7
```

The controller was launched through `franka_bringup`, and a `trajectory_msgs/msg/JointTrajectory` command was tested.

### Observation

The controller could be loaded, and the command interface could be checked with:

```bash
ros2 control list_hardware_interfaces -c /fr3/controller_manager
ros2 control list_controllers -c /fr3/controller_manager
```

However, direct trajectory control was not the cleanest or most reliable approach for the final Cartesian motion target.

### Conclusion

A generic trajectory controller is useful for testing, but it is not the best final method for Cartesian motion on the FR3.

### Decision

Move to the official MoveIt-based pipeline instead of manually controlling trajectories.

---

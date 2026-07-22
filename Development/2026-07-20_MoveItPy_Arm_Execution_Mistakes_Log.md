# July 20 — MoveItPy Arm Execution Mistakes Log


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
### Mistakes

#### Mistake 1 — Wrong Current State Usage
Problem:
 get the live robot state from RobotModel.

Error
AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'
Fix

RobotModel only describes the robot model.
The current robot state should be handled through the MoveItPy planning component.

#### Mistake 2 — Wrong Goal State Format
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
---
#### Mistake 3 — Misdiagnosing Execution Failure as Hardware Failure
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

#### Mistake 4 — Wrong OMPL Plugin Parameter
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

#### Mistake 5 — Missing Planning Adapters for Time Sequence
Problem

MoveIt could generate a geometric path, but the trajectory was not properly prepared for real controller execution.

Planning success alone does not guarantee valid trajectory timing.

The controller needs:
```text
- time_from_start
- velocity
- acceleration
- valid trajectory timing
```
Fix:

Add planning response adapters, especially:
```text
default_planning_response_adapters/AddTimeOptimalParameterization
```
Purpose

AddTimeOptimalParameterization converts the geometric path into a time-parameterized trajectory.

Without this adapter, fr3_arm_controller may reject the goal even when OMPL planning succeeds.

#### Mistake 6 — Missing Velocity and Acceleration Scaling
Problem:

The launch file did not define:
```bash
max_velocity_scaling_factor
max_acceleration_scaling_factor
```
Fix:

Add safe velocity and acceleration scaling parameters for real robot execution.

Example values:
```bash
max_velocity_scaling_factor: 0.05
max_acceleration_scaling_factor: 0.05
Mistake 7 — Misleading Execution Output
```
Problem:
```bash
The script printed: Execution finished
```
even when MoveIt reported:

Completed trajectory execution with status ABORTED
Fix:

Only print execution success after checking the actual execution result.

#### Final Fix Summary:

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
### Result

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
```text
- MoveItPy arm planning working                      
- fr3_arm_controller verified                        
- Direct FollowJointTrajectory test succeeded        
- OMPL plugin configuration fixed                    
- Trajectory time-parameterization added             
- MoveItPy arm execution succeeded                             
```

### Next Actions:
```bash
1. Clean up the custom MoveIt launch file.
2. Keep direct FollowJointTrajectory command as a hardware test.
3. Refactor reusable arm motion logic into motion.py.
4. Keep high-level task logic separate from reusable motion APIs.
5. Add Cartesian approach and retreat motion for the arm.
6. Test small safe arm motions first.
7. Update Troubleshooting.md with the OMPL plugin and adapter issue.
```
















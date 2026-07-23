# OMPL Pipeline Configuration for MoveItPy / MoveItCpp

## Purpose

This document explains the OMPL planning pipeline configuration used by MoveItPy and MoveItCpp for the Franka FR3 project.

The configuration defines:

- how OMPL plans robot motion,
- how MoveIt receives the robot state and planning scene,
- which planner is used,
- how the final trajectory is validated and time-parameterized,
- how velocity and acceleration limits are applied.

---

## 1. Load the OMPL YAML File

```python
ompl_yaml = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)
```

### Purpose

Loads the OMPL planner configuration from:

```text
franka_fr3_moveit_config/config/ompl_planning.yaml
```

The YAML file may define:

- available OMPL planners,
- planner-specific parameters,
- planning groups,
- RRTConnect settings,
- PRM settings,
- RRTstar settings,
- search range and resolution parameters.

This keeps planner parameters outside the Python source code.

---

## 2. Create the OMPL Planning Pipeline

```python
ompl_pipeline = {
```

### Purpose

Creates the planning pipeline configuration used by MoveItPy and MoveItCpp.

The pipeline controls the complete planning process:

```text
Planning Request
        │
        ▼
Request Validation
        │
        ▼
OMPL Path Planning
        │
        ▼
Trajectory Post-Processing
        │
        ▼
Trajectory Execution
```

---

## 3. Planning Plugin

```python
"planning_plugins": [
    "ompl_interface/OMPLPlanner",
],
```

### Purpose

Tells MoveIt to use the OMPL planner interface.

```text
ompl_interface/OMPLPlanner
```

connects MoveIt with the Open Motion Planning Library.

OMPL is responsible for:

- sampling possible robot configurations,
- checking collision-free states,
- searching for a valid path,
- generating a joint-space path from the start state to the goal state.

OMPL generates the path, but it does not directly control the robot hardware.

---

## 4. Request Adapters

```python
"request_adapters": [
```

Request adapters process and validate the planning request before OMPL starts planning.

### ResolveConstraintFrames

```python
"default_planning_request_adapters/"
"ResolveConstraintFrames",
```

#### Purpose

Resolves the reference frames used in planning constraints.

A target pose may be defined relative to frames such as:

```text
fr3_link0
world
```

This adapter ensures that constraint frames are transformed into frames understood by MoveIt.

### ValidateWorkspaceBounds

```python
"default_planning_request_adapters/"
"ValidateWorkspaceBounds",
```

#### Purpose

Checks that the planning workspace boundaries are valid.

The workspace defines the 3D area in which MoveIt is allowed to search for robot motion.

### CheckStartStateBounds

```python
"default_planning_request_adapters/"
"CheckStartStateBounds",
```

#### Purpose

Checks whether the robot's starting joint values are within their allowed limits.

If the current state is slightly outside a joint limit because of numerical error, this adapter may correct or reject it.

### CheckStartStateCollision

```python
"default_planning_request_adapters/"
"CheckStartStateCollision",
```

#### Purpose

Checks whether the robot's starting configuration is already in collision.

It checks:

- self-collision,
- collision with the environment,
- collision with attached objects.

---

## 5. Response Adapters

```python
"response_adapters": [
```

Response adapters process the trajectory after OMPL finds a path.

### AddTimeOptimalParameterization

```python
"default_planning_response_adapters/"
"AddTimeOptimalParameterization",
```

#### Purpose

Adds timing information to the trajectory.

OMPL normally produces a geometric path. The controller also needs:

- timestamps,
- velocities,
- accelerations.

This adapter converts the path into an executable, time-parameterized trajectory.

### ValidateSolution

```python
"default_planning_response_adapters/"
"ValidateSolution",
```

#### Purpose

Validates the final trajectory before execution.

It checks that the solution is:

- collision-free,
- within joint limits,
- consistent with the planning request,
- valid for execution.

### DisplayMotionPath

```python
"default_planning_response_adapters/"
"DisplayMotionPath",
```

#### Purpose

Publishes the planned trajectory for visualization in RViz.

This is useful for:

- debugging,
- visual inspection,
- checking whether the path looks correct.

---

## 6. Start-State Bounds Tolerance

```python
"start_state_max_bounds_error": 0.1,
```

### Purpose

Defines the maximum tolerated error when checking the start state against joint limits.

Here:

```text
0.1 radians
```

is the allowed tolerance.

A very large value may hide configuration problems, while a very small value may cause planning failures due to numerical or sensor errors.

---

## 7. Merge the YAML Configuration

```python
if ompl_yaml:
    ompl_pipeline.update(ompl_yaml)
```

### Purpose

Adds the settings loaded from `ompl_planning.yaml` into the Python pipeline dictionary.

The final OMPL configuration combines:

```text
Python-defined pipeline settings
            +
YAML-defined planner settings
```

---

# MoveItPy Configuration

```python
moveit_py_configuration = {
```

### Purpose

Creates the complete configuration passed to MoveItPy.

It contains:

- planning scene monitor options,
- planning pipeline selection,
- planning request parameters,
- OMPL pipeline configuration.

---

## 8. Planning Scene Monitor Options

```python
"planning_scene_monitor_options": {
```

### Purpose

Configures how MoveIt obtains and maintains information about:

- the robot model,
- current joint positions,
- collision objects,
- attached objects,
- the planning environment.

### Name

```python
"name": "planning_scene_monitor",
```

Sets the internal name of the planning scene monitor.

### Robot Description

```python
"robot_description": "robot_description",
```

Specifies the ROS parameter containing the robot URDF model.

The robot description includes:

- links,
- joints,
- kinematic chains,
- collision geometry,
- visual geometry.

### Joint-State Topic

```python
"joint_state_topic": "/joint_states",
```

Defines the ROS 2 topic that publishes the robot's current joint state.

Typical message type:

```text
sensor_msgs/msg/JointState
```

### Attached Collision-Object Topic

```python
"attached_collision_object_topic":
    "/attached_collision_object",
```

Specifies the topic used for objects attached to the robot.

For example, after the gripper picks up a box, the box should move with the robot in the planning scene.

### Publish Planning-Scene Topic

```python
"publish_planning_scene_topic":
    "/moveit_cpp/publish_planning_scene",
```

Defines the topic used to publish the planning scene maintained by MoveItPy or MoveItCpp.

### Monitored Planning-Scene Topic

```python
"monitored_planning_scene_topic":
    "/monitored_planning_scene",
```

Defines the topic from which MoveIt receives planning-scene updates.

Examples include:

- adding an obstacle,
- removing an object,
- attaching an object,
- detaching an object,
- updating the robot state.

### Initial-State Timeout

```python
"wait_for_initial_state_timeout": 10.0,
```

Specifies how long MoveIt waits for the first valid joint state.

Here, MoveIt waits up to:

```text
10 seconds
```

for data from `/joint_states`.

---

## 9. Planning Pipelines

```python
"planning_pipelines": {
    "pipeline_names": ["ompl"],
},
```

### Purpose

Defines which planning pipelines are available to MoveItPy.

Here, only one pipeline is registered:

```text
ompl
```

---

## 10. Planning Request Parameters

```python
"plan_request_params": {
```

### Purpose

Defines the default parameters used for each motion-planning request.

### Planning Attempts

```python
"planning_attempts": 1,
```

Defines how many times the planner should try to find a path.

Here, only one planning attempt is allowed.

### Planning Pipeline

```python
"planning_pipeline": "ompl",
```

Selects the OMPL planning pipeline.

The value must match:

```python
"pipeline_names": ["ompl"]
```

### Planner ID

```python
"planner_id":
    "RRTConnectkConfigDefault",
```

Selects the OMPL planning algorithm.

RRTConnect is a bidirectional sampling-based planner. It grows one search tree from the start state and another from the goal state, then attempts to connect them.

It is commonly used for robot arms because it is:

- fast,
- effective in high-dimensional spaces,
- suitable for collision-free motion planning.

The planner ID must match an entry in `ompl_planning.yaml`.

### Planning Time

```python
"planning_time": 5.0,
```

Defines the maximum time allowed for planning.

Here, OMPL has up to:

```text
5 seconds
```

to find a valid path.

### Velocity Scaling Factor

```python
"max_velocity_scaling_factor": 0.1,
```

Limits trajectory velocity to 10% of the robot's maximum allowed velocity.

```text
0.1 = 10%
1.0 = 100%
```

This is appropriate for:

- hardware testing,
- early development,
- debugging,
- safer robot motion.

### Acceleration Scaling Factor

```python
"max_acceleration_scaling_factor": 0.1,
```

Limits trajectory acceleration to 10% of the maximum allowed acceleration.

Lower acceleration produces:

- smoother starts,
- smoother stops,
- reduced mechanical shock,
- safer testing.

---

## 11. Attach the OMPL Pipeline

```python
"ompl": ompl_pipeline,
```

### Purpose

Adds the complete OMPL pipeline configuration to the MoveItPy configuration.

The key:

```text
ompl
```

must correspond to the registered pipeline name.

---

# Complete Workflow

```text
MoveItPy Application
        │
        ▼
Load Robot Description
        │
        ▼
Receive Current Joint State
        │
        ▼
Maintain Planning Scene
        │
        ▼
Create Planning Request
        │
        ├── Planner: RRTConnect
        ├── Planning time: 5 seconds
        ├── Velocity scaling: 10%
        └── Acceleration scaling: 10%
        │
        ▼
Request Adapters
        │
        ├── Resolve constraint frames
        ├── Validate workspace
        ├── Check joint bounds
        └── Check start-state collision
        │
        ▼
OMPL Planner
        │
        ▼
Response Adapters
        │
        ├── Add trajectory timing
        ├── Validate solution
        └── Display path in RViz
        │
        ▼
Executable Joint Trajectory
```

---

## Summary

The configuration prepares MoveItPy to safely plan Franka FR3 motion by:

- loading the robot model,
- receiving the current robot state,
- maintaining the collision environment,
- using RRTConnect for motion planning,
- validating the start state,
- generating trajectory timing,
- limiting velocity and acceleration,
- preparing the trajectory for visualization and execution.

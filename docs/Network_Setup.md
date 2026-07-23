# OMPL Planning Pipeline (MoveItPy / MoveItCpp)

## Purpose

This document explains how the OMPL planning pipeline is configured in this project and how each configuration block contributes to motion planning for the Franka FR3.

---

# Architecture Overview

```text
MoveItPy Application
        │
        ▼
Load Robot Description
        │
        ▼
Planning Scene Monitor
        │
        ▼
Planning Request
        │
        ▼
Request Adapters
        │
        ▼
OMPL Planner (RRTConnect)
        │
        ▼
Response Adapters
        │
        ▼
Time-Parameterized Trajectory
        │
        ▼
Robot Controller
```

---

# 1. Load Planner Configuration

## Code

```python
ompl_yaml = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)
```

## Purpose

Loads planner-specific parameters from `config/ompl_planning.yaml`.

**Benefits**

- Keeps planner parameters outside the source code.
- Allows planners and tuning values to be modified without editing Python files.

---

# 2. Configure the OMPL Pipeline

## Code

```python
ompl_pipeline = { ... }
```

## Purpose

Defines the complete planning pipeline used by MoveIt.

The pipeline consists of four stages:

```text
Planning Request
      ↓
Request Adapters
      ↓
OMPL Planner
      ↓
Response Adapters
```

---

# 3. Planning Plugin

## Code

```python
"planning_plugins": [
    "ompl_interface/OMPLPlanner",
]
```

## Purpose

Selects OMPL as the motion planning backend.

**Responsibilities**

- Search for collision-free paths
- Sample robot configurations
- Generate joint trajectories

---

# 4. Request Adapters

Request adapters validate the planning request before planning begins.

| Adapter | Purpose |
|---------|---------|
| ResolveConstraintFrames | Resolve constraint reference frames. |
| ValidateWorkspaceBounds | Validate workspace boundaries. |
| CheckStartStateBounds | Verify joint limits of the current state. |
| CheckStartStateCollision | Detect collisions before planning. |

---

# 5. Response Adapters

Response adapters process the planned trajectory.

| Adapter | Purpose |
|---------|---------|
| AddTimeOptimalParameterization | Compute timestamps, velocities and accelerations. |
| ValidateSolution | Verify the planned trajectory. |
| DisplayMotionPath | Publish the trajectory for RViz visualization. |

---

# 6. Start-State Tolerance

## Code

```python
"start_state_max_bounds_error": 0.1
```

## Purpose

Defines the allowable joint-limit tolerance when validating the current robot state.

---

# 7. Merge YAML Configuration

## Code

```python
if ompl_yaml:
    ompl_pipeline.update(ompl_yaml)
```

## Purpose

Combines the default Python configuration with planner settings from the YAML file.

---

# 8. Planning Scene Monitor

## Purpose

Maintains the robot model and planning environment.

### Components

| Parameter | Purpose |
|----------|---------|
| `robot_description` | Load the URDF model. |
| `joint_state_topic` | Receive current joint states. |
| `attached_collision_object_topic` | Track objects attached to the robot. |
| `publish_planning_scene_topic` | Publish the planning scene. |
| `monitored_planning_scene_topic` | Receive planning scene updates. |
| `wait_for_initial_state_timeout` | Wait for the initial robot state. |

---

# 9. Planning Pipeline Selection

## Code

```python
"planning_pipelines": {
    "pipeline_names": ["ompl"],
}
```

## Purpose

Registers the available planning pipelines.

This project uses a single planning pipeline:

- **OMPL**

---

# 10. Planning Request Parameters

| Parameter | Purpose |
|-----------|---------|
| `planning_attempts` | Number of planning attempts. |
| `planning_pipeline` | Pipeline used for planning. |
| `planner_id` | Selected OMPL planner (RRTConnect). |
| `planning_time` | Maximum planning time. |
| `max_velocity_scaling_factor` | Velocity scaling factor. |
| `max_acceleration_scaling_factor` | Acceleration scaling factor. |

### Planner

```text
RRTConnectkConfigDefault
```

Chosen because it provides fast and reliable planning for industrial manipulators.

---

# 11. Attach the OMPL Pipeline

## Code

```python
"ompl": ompl_pipeline,
```

## Purpose

Adds the complete OMPL configuration to the MoveItPy configuration object.

---

# Complete Workflow

```text
Python Application
        │
        ▼
Load Robot Model
        │
        ▼
Planning Scene Monitor
        │
        ▼
Planning Request
        │
        ▼
Request Adapters
        │
        ▼
OMPL (RRTConnect)
        │
        ▼
Response Adapters
        │
        ▼
Time-Parameterized Trajectory
        │
        ▼
Trajectory Execution
```

---

# Key Takeaways

- `ompl_planning.yaml` stores planner parameters.
- `planning_plugins` selects the planning backend.
- Request adapters validate the planning request.
- Response adapters optimize and validate the generated trajectory.
- The Planning Scene Monitor keeps the robot model and environment synchronized.
- Planning request parameters control planner behavior and execution speed.
- The complete configuration enables MoveItPy to generate safe, executable trajectories for the Franka FR3.

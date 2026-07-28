# Development Log — FR3 MoveIt Python Package Debugging
**Date:** July 28, 2026  
**Project:** Franka FR3 ROS 2 Jazzy + MoveItPy  
**Workspace:** `~/franka_ros2_ws`  
**Package:** `fr3_moveit_python`

---

# Objective

Debug and successfully launch the custom ROS 2 Python package
`fr3_moveit_python` for controlling the Franka FR3 robot using MoveItPy.

---

# Initial Issue

Attempting to launch:

```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py \
    dz:=-0.05 \
    execute:=true
```

Resulted in

```text
Package 'fr3_moveit_python' not found
```

---

# Investigation

## 1. Verify Workspace

Checked that the package existed.

```bash
ls ~/franka_ros2_ws/src
```

Confirmed:

```
fr3_moveit_python
```

---

## 2. Verify ROS Package Discovery

Checked:

```bash
ros2 pkg prefix fr3_moveit_python
```

Output:

```text
Package not found
```

This indicated the package had not been installed into the ROS 2 workspace.

---

## 3. Verify Colcon Detection

Executed

```bash
colcon list | grep fr3_moveit_python
```

Output

```text
fr3_moveit_python    src/fr3_moveit_python    (python)
```

Conclusion:

- Source package exists.
- Colcon can detect it.
- Problem occurs during installation or package registration.

---

# XML Parsing Issue

During the build process:

```text
XML Parsing Error:
XML or text declaration not at start of entity
```

Cause:

The `package.xml` file contained hidden characters or blank lines before

```xml
<?xml version="1.0"?>
```

Resolution:

- Removed leading blank lines/BOM.
- Verified XML formatting.
- Rebuilt the package.

---

# Package Registration

After fixing `package.xml`:

```bash
ros2 pkg prefix fr3_moveit_python
```

Package became discoverable.

---

# New Launch Error

Running

```bash
ros2 launch fr3_moveit_python cartesian_move.launch.py
```

produced

```text
package found

but libexec directory

install/fr3_moveit_python/lib/fr3_moveit_python

does not exist
```

Meaning:

ROS 2 located the package but no executable scripts were installed.

---

# setup.py Inspection

Verified:

```python
entry_points={
    "console_scripts":[
        "cartesian_move = fr3_moveit_python.cartesian_move:main",
        "gripper_control = fr3_moveit_python.gripper_control:main",
        "motion_test = fr3_moveit_python.motion_test:main",
        "pick_place = fr3_moveit_python.pick_place:main",
    ]
}
```

Problem discovered:

```
motion_test.py
```

did not exist.

Actual file:

```
motion.py
```

Required correction:

```python
motion = fr3_moveit_python.motion:main
```

---

# setup.cfg

Discovered that `setup.cfg` was missing.

Added

```ini
[develop]
script_dir=$base/lib/fr3_moveit_python

[install]
install_scripts=$base/lib/fr3_moveit_python
```

Purpose:

Ensures ROS 2 installs console scripts into

```
install/fr3_moveit_python/lib/fr3_moveit_python/
```

instead of the default Python location.

---

# Directory Inspection

Current module directory

```
fr3_moveit_python/
├── build
├── install
├── log
├── setup.py
├── cartesian_move.py
├── gripper.py
├── gripper_control.py
├── motion.py
├── pick_place.py
└── __init__.py
```

Unexpected directories:

```
build/
install/
log/
```

These should **not** exist inside the Python module.

Likely cause:

`colcon build` was accidentally executed inside the package directory.

Resolution:

Remove these directories and rebuild from the workspace root.

---

# Rebuild Procedure

```bash
cd ~/franka_ros2_ws

rm -rf build/fr3_moveit_python
rm -rf install/fr3_moveit_python

source /opt/ros/jazzy/setup.bash

colcon build \
    --symlink-install \
    --packages-select fr3_moveit_python

source install/setup.bash
```

---

# Verification

Verify package installation

```bash
ros2 pkg prefix fr3_moveit_python
```

Verify executables

```bash
ros2 pkg executables fr3_moveit_python
```

Expected

```text
fr3_moveit_python cartesian_move
fr3_moveit_python gripper_control
fr3_moveit_python motion
fr3_moveit_python pick_place
```

---

# Root Causes

1. Invalid `package.xml` due to hidden characters before the XML declaration.
2. Package initially not installed into the ROS 2 workspace.
3. Missing `setup.cfg`.
4. Incorrect `entry_points` referencing a non-existent Python module.
5. Build artifacts accidentally created inside the Python module directory.
6. Missing executable installation caused the `libexec` directory error.

---

# Lessons Learned

- Always build from the workspace root (`~/franka_ros2_ws`).
- Source the workspace after every successful build.
- Ensure `package.xml` begins with the XML declaration on the first line.
- Verify `setup.py`, `setup.cfg`, and `entry_points` for all Python ROS 2 packages.
- Keep the Python module directory free of `build`, `install`, and `log` folders.
- Use `ros2 pkg prefix` and `ros2 pkg executables` to verify successful package installation before launching.

---

# Status

**Current Status:** Debugging in progress.

Remaining tasks:

- Correct `entry_points`.
- Remove misplaced build artifacts.
- Rebuild the package.
- Verify console script installation.
- Successfully launch `cartesian_move.launch.py`.

"""
fr3_moveit_python

MoveItPy-based motion planning and Franka gripper control
for the Franka FR3 robot.

This package provides reusable motion and gripper interfaces
for higher-level robot applications.
"""

"""
If another file currently imports like this:
from fr3_moveit_python.motion import MotionController
from fr3_moveit_python.gripper import FrankaGripper
"""

# _init_.py can simpliify it 

# Example:

"""
from .motion import MotionController
from .gripper import FrankaGripper

__all__ = [
    "MotionController",
    "FrankaGripper",
]
"""

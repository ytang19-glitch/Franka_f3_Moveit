```python
import argparse
import math
import os
import sys
import time

import rclpy

from geometry_msgs.msg import PoseStamped
from moveit.planning import MoveItPy
from rclpy.logging import get_logger
from scipy.spatial.transform import Rotation


# ==========================================================
# Default robot configuration
# ==========================================================

PLANNING_GROUP = "fr3_arm"

DEFAULT_BASE_FRAME = "fr3_link0"

DEFAULT_EE_LINK = "fr3_hand_tcp"


# ==========================================================
# Cartesian Controller
# ==========================================================

class CartesianController:

    def __init__(
        self,
        base_frame=DEFAULT_BASE_FRAME,
        ee_link=DEFAULT_EE_LINK,
    ):

        # --------------------------------------------------
        # Store configurable frames
        # --------------------------------------------------

        self.base_frame = base_frame
        self.ee_link = ee_link

        # --------------------------------------------------
        # Logger
        # --------------------------------------------------

        self.logger = get_logger(
            "cartesian_controller"
        )

        # --------------------------------------------------
        # Initialize MoveItPy
        # --------------------------------------------------

        self.moveit = MoveItPy(
            node_name="fr3_cartesian_controller"
        )

        # --------------------------------------------------
        # Get FR3 planning group
        # --------------------------------------------------

        self.arm = self.moveit.get_planning_component(
            PLANNING_GROUP
        )

        self.logger.info(
            f"""
Cartesian Controller initialized

Planning group:
{PLANNING_GROUP}

Base frame:
{self.base_frame}

End-effector link:
{self.ee_link}
"""
        )

    # ======================================================
    # Main Cartesian relative motion function
    # ======================================================

    def move_relative(
        self,
        dx=0.0,
        dy=0.0,
        dz=0.0,
        droll=0.0,
        dpitch=0.0,
        dyaw=0.0,
        execute=True,
    ):

        # --------------------------------------------------
        # Start planning from current robot state
        # --------------------------------------------------

        self.arm.set_start_state_to_current_state()

        # --------------------------------------------------
        # Get planning scene monitor
        # --------------------------------------------------

        planning_scene_monitor = (
            self.moveit
            .get_planning_scene_monitor()
        )

        # --------------------------------------------------
        # Read current TCP transform
        # --------------------------------------------------

        with planning_scene_monitor.read_only() as scene:

            current_state = scene.current_state

            transform = (
                current_state
                .get_global_link_transform(
                    self.ee_link
                )
            ).copy()

        # --------------------------------------------------
        # Current TCP position
        # --------------------------------------------------

        current_x = float(
            transform[0, 3]
        )

        current_y = float(
            transform[1, 3]
        )

        current_z = float(
            transform[2, 3]
        )

        # --------------------------------------------------
        # Current TCP orientation
        # --------------------------------------------------

        current_rotation = Rotation.from_matrix(
            transform[:3, :3]
        )

        current_rpy = current_rotation.as_euler(
            "xyz",
            degrees=False,
        )

        # --------------------------------------------------
        # Relative orientation rotation
        #
        # droll  = rotation around local TCP X
        # dpitch = rotation around local TCP Y
        # dyaw   = rotation around local TCP Z
        # --------------------------------------------------

        delta_rotation = Rotation.from_euler(
            "xyz",
            [
                droll,
                dpitch,
                dyaw,
            ],
            degrees=False,
        )

        # --------------------------------------------------
        # Apply relative rotation
        #
        # current_rotation * delta_rotation
        #
        # means the incremental rotation is applied in
        # the current TCP/local coordinate frame.
        # --------------------------------------------------

        target_rotation = (
            current_rotation
            * delta_rotation
        )

        # --------------------------------------------------
        # Convert target orientation to quaternion
        #
        # scipy order:
        # [x, y, z, w]
        # --------------------------------------------------

        target_quaternion = (
            target_rotation.as_quat()
        )

        target_rpy = target_rotation.as_euler(
            "xyz",
            degrees=False,
        )

        # --------------------------------------------------
        # Create target PoseStamped
        # --------------------------------------------------

        target_pose = PoseStamped()

        target_pose.header.frame_id = (
            self.base_frame
        )

        # --------------------------------------------------
        # Target Cartesian position
        # --------------------------------------------------

        target_pose.pose.position.x = (
            current_x + dx
        )

        target_pose.pose.position.y = (
            current_y + dy
        )

        target_pose.pose.position.z = (
            current_z + dz
        )

        # --------------------------------------------------
        # Target Cartesian orientation
        # --------------------------------------------------

        target_pose.pose.orientation.x = float(
            target_quaternion[0]
        )

        target_pose.pose.orientation.y = float(
            target_quaternion[1]
        )

        target_pose.pose.orientation.z = float(
            target_quaternion[2]
        )

        target_pose.pose.orientation.w = float(
            target_quaternion[3]
        )

        # --------------------------------------------------
        # Print current pose and target pose
        # --------------------------------------------------

        self.logger.info(
            f"""
========================================
Current TCP Pose
========================================

Position:

x = {current_x:.4f} m
y = {current_y:.4f} m
z = {current_z:.4f} m


Orientation:

roll  = {current_rpy[0]:.4f} rad
pitch = {current_rpy[1]:.4f} rad
yaw   = {current_rpy[2]:.4f} rad


========================================
Requested Relative Motion
========================================

Translation:

dx = {dx:.4f} m
dy = {dy:.4f} m
dz = {dz:.4f} m


Rotation:

droll  = {droll:.4f} rad
dpitch = {dpitch:.4f} rad
dyaw   = {dyaw:.4f} rad


========================================
Target TCP Pose
========================================

Position:

x = {target_pose.pose.position.x:.4f} m
y = {target_pose.pose.position.y:.4f} m
z = {target_pose.pose.position.z:.4f} m


Orientation:

roll  = {target_rpy[0]:.4f} rad
pitch = {target_rpy[1]:.4f} rad
yaw   = {target_rpy[2]:.4f} rad


Quaternion:

qx = {target_quaternion[0]:.4f}
qy = {target_quaternion[1]:.4f}
qz = {target_quaternion[2]:.4f}
qw = {target_quaternion[3]:.4f}

========================================
"""
        )

        # --------------------------------------------------
        # Set MoveIt goal
        # --------------------------------------------------

        self.arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=self.ee_link,
        )

        self.logger.info(
            "Planning Cartesian position + orientation motion..."
        )

        # --------------------------------------------------
        # Plan motion
        # --------------------------------------------------

        plan_result = self.arm.plan()

        if not plan_result:

            self.logger.error(
                "Planning failed"
            )

            return False

        self.logger.info(
            "Planning succeeded"
        )

        # --------------------------------------------------
        # Planning-only mode
        # --------------------------------------------------

        if not execute:

            self.logger.info(
                "Execution disabled. Planning only."
            )

            return True

        # --------------------------------------------------
        # Wait for MoveIt controller discovery
        # --------------------------------------------------

        time.sleep(5.0)

        # --------------------------------------------------
        # Execute trajectory
        # --------------------------------------------------

        self.logger.info(
            "Executing trajectory..."
        )

        result = self.moveit.execute(
            plan_result.trajectory,
            controllers=[
                "fr3_arm_controller"
            ],
        )

        self.logger.info(
            f"Execution result: {result}"
        )

        return True

    # ======================================================
    # Cartesian position helper functions
    # ======================================================

    def move_down(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dz=-distance,
            execute=execute,
        )

    def move_up(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dz=distance,
            execute=execute,
        )

    def move_forward(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dx=distance,
            execute=execute,
        )

    def move_backward(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dx=-distance,
            execute=execute,
        )

    def move_left(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dy=distance,
            execute=execute,
        )

    def move_right(
        self,
        distance,
        execute=True,
    ):

        return self.move_relative(
            dy=-distance,
            execute=execute,
        )

    # ======================================================
    # Orientation helper functions
    # ======================================================

    def rotate_roll(
        self,
        angle,
        execute=True,
    ):

        return self.move_relative(
            droll=angle,
            execute=execute,
        )

    def rotate_pitch(
        self,
        angle,
        execute=True,
    ):

        return self.move_relative(
            dpitch=angle,
            execute=execute,
        )

    def rotate_yaw(
        self,
        angle,
        execute=True,
    ):

        return self.move_relative(
            dyaw=angle,
            execute=execute,
        )


# ==========================================================
# Argument parser
# ==========================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "FR3 Cartesian Position + Orientation Motion"
        )
    )

    # ------------------------------------------------------
    # Position arguments
    # ------------------------------------------------------

    parser.add_argument(
        "--dx",
        type=float,
        default=0.0,
        help="Relative X displacement in metres",
    )

    parser.add_argument(
        "--dy",
        type=float,
        default=0.0,
        help="Relative Y displacement in metres",
    )

    parser.add_argument(
        "--dz",
        type=float,
        default=0.0,
        help="Relative Z displacement in metres",
    )

    # ------------------------------------------------------
    # Orientation arguments in radians
    # ------------------------------------------------------

    parser.add_argument(
        "--droll",
        type=float,
        default=0.0,
        help="Relative roll rotation in radians",
    )

    parser.add_argument(
        "--dpitch",
        type=float,
        default=0.0,
        help="Relative pitch rotation in radians",
    )

    parser.add_argument(
        "--dyaw",
        type=float,
        default=0.0,
        help="Relative yaw rotation in radians",
    )

    # ------------------------------------------------------
    # Optional orientation arguments in degrees
    # ------------------------------------------------------

    parser.add_argument(
        "--droll-deg",
        type=float,
        default=None,
        help="Relative roll rotation in degrees",
    )

    parser.add_argument(
        "--dpitch-deg",
        type=float,
        default=None,
        help="Relative pitch rotation in degrees",
    )

    parser.add_argument(
        "--dyaw-deg",
        type=float,
        default=None,
        help="Relative yaw rotation in degrees",
    )

    # ------------------------------------------------------
    # Base frame
    # ------------------------------------------------------

    parser.add_argument(
        "--base-frame",
        type=str,
        default=DEFAULT_BASE_FRAME,
        help="Base reference frame",
    )

    # ------------------------------------------------------
    # End-effector link
    # ------------------------------------------------------

    parser.add_argument(
        "--ee-link",
        type=str,
        default=DEFAULT_EE_LINK,
        help="End-effector TCP link",
    )

    # ------------------------------------------------------
    # Execute / planning-only
    # ------------------------------------------------------

    parser.add_argument(
        "--execute",
        type=str,
        default="false",
        help=(
            "true = execute trajectory, "
            "false = planning only"
        ),
    )

    # parse_known_args() is useful with ROS 2 because
    # ROS may add extra arguments automatically.

    return parser.parse_known_args()[0]


# ==========================================================
# Boolean parser
# ==========================================================

def parse_bool(value):

    return value.lower() in [
        "true",
        "1",
        "yes",
        "on",
    ]


# ==========================================================
# Safe exit
#
# Avoid MoveItPy shutdown hanging issues.
# ==========================================================

def safe_exit(code):

    sys.stdout.flush()
    sys.stderr.flush()

    os._exit(code)


# ==========================================================
# Main
# ==========================================================

def main():

    # ------------------------------------------------------
    # Read command-line arguments
    # ------------------------------------------------------

    args = parse_arguments()

    # ------------------------------------------------------
    # Initialize ROS 2
    # ------------------------------------------------------

    rclpy.init()

    # ------------------------------------------------------
    # Create Cartesian controller
    #
    # base_frame and ee_link now come from launch arguments
    # ------------------------------------------------------

    motion = CartesianController(
        base_frame=args.base_frame,
        ee_link=args.ee_link,
    )

    # ------------------------------------------------------
    # Default orientation values use radians
    # ------------------------------------------------------

    droll = args.droll
    dpitch = args.dpitch
    dyaw = args.dyaw

    # ------------------------------------------------------
    # If degree arguments are supplied,
    # convert them to radians
    # ------------------------------------------------------

    if args.droll_deg is not None:

        droll = math.radians(
            args.droll_deg
        )

    if args.dpitch_deg is not None:

        dpitch = math.radians(
            args.dpitch_deg
        )

    if args.dyaw_deg is not None:

        dyaw = math.radians(
            args.dyaw_deg
        )

    # ------------------------------------------------------
    # Run Cartesian motion
    # ------------------------------------------------------

    success = motion.move_relative(

        # Position
        dx=args.dx,
        dy=args.dy,
        dz=args.dz,

        # Orientation
        droll=droll,
        dpitch=dpitch,
        dyaw=dyaw,

        # Execute or planning-only
        execute=parse_bool(
            args.execute
        ),
    )

    # ------------------------------------------------------
    # Safe process exit
    # ------------------------------------------------------

    safe_exit(
        0 if success else 1
    )


# ==========================================================
# Python entry point
# ==========================================================

if __name__ == "__main__":

    main()
```

#Stondalone script for relative Cartesian pose-goal motion for Franka FR3.

import argparse
import os
import sys
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from moveit.planning import MoveItPy
from rclpy.logging import get_logger
from scipy.spatial.transform import Rotation


PLANNING_GROUP = "fr3_arm"
DEFAULT_BASE_FRAME = "fr3_link0"
DEFAULT_EE_LINK = "fr3_hand_tcp"

# only for command line testing.

# Example:

# python cartesian_move.py --dx 0.1 --dz -0.1

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Relative Cartesian pose-goal motion for Franka FR3."
    )

    parser.add_argument("--dx", type=float, default=0.0)
    parser.add_argument("--dy", type=float, default=0.0)
    parser.add_argument("--dz", type=float, default=0.0)

    parser.add_argument(
        "--execute",
        type=str,
        default="false",
    )

    parser.add_argument(
        "--base-frame",
        type=str,
        default=DEFAULT_BASE_FRAME,
    )

    parser.add_argument(
        "--ee-link",
        type=str,
        default=DEFAULT_EE_LINK,
    )

    args, _ = parser.parse_known_args()
    return args


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }



def main() -> None:
    args = parse_arguments()
    execute_motion = parse_bool(args.execute)

    rclpy.init()

    logger = get_logger("fr3_cartesian_move")

    logger.info(
        "Requested displacement:\n"
        f"  base frame = {args.base_frame}\n"
        f"  end link   = {args.ee_link}\n"
        f"  dx         = {args.dx:.4f} m\n"
        f"  dy         = {args.dy:.4f} m\n"
        f"  dz         = {args.dz:.4f} m\n"
        f"  execute    = {execute_motion}"
    )

    try:
        moveit = MoveItPy(
            node_name="fr3_cartesian_moveitpy"
        )

        arm = moveit.get_planning_component(
            PLANNING_GROUP
        )

        logger.info("MoveItPy initialized.")

        arm.set_start_state_to_current_state()

        planning_scene_monitor = (
            moveit.get_planning_scene_monitor()
        )

        with planning_scene_monitor.read_only() as scene:
            current_state = scene.current_state

            transform = (
                current_state.get_global_link_transform(
                    args.ee_link
                )
            ).copy()

        current_x = float(transform[0, 3])
        current_y = float(transform[1, 3])
        current_z = float(transform[2, 3])

        quaternion = Rotation.from_matrix(
            transform[:3, :3]
        ).as_quat()

        target_pose = PoseStamped()
        target_pose.header.frame_id = args.base_frame

        target_pose.pose.position.x = current_x + args.dx
        target_pose.pose.position.y = current_y + args.dy
        target_pose.pose.position.z = current_z + args.dz

        # Keep the current end-effector orientation unchanged.
        target_pose.pose.orientation.x = float(quaternion[0])
        target_pose.pose.orientation.y = float(quaternion[1])
        target_pose.pose.orientation.z = float(quaternion[2])
        target_pose.pose.orientation.w = float(quaternion[3])

        logger.info(
            "Current TCP position:\n"
            f"  x = {current_x:.4f}\n"
            f"  y = {current_y:.4f}\n"
            f"  z = {current_z:.4f}"
        )

        logger.info(
            "Target TCP position:\n"
            f"  x = {target_pose.pose.position.x:.4f}\n"
            f"  y = {target_pose.pose.position.y:.4f}\n"
            f"  z = {target_pose.pose.position.z:.4f}"
        )

        arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=args.ee_link,
        )

        logger.info("Planning trajectory...")

        plan_result = arm.plan()

        if not plan_result:
            logger.error("Planning failed.")
            flush_and_exit(1)

        logger.info("Planning succeeded.")

        if not execute_motion:
            logger.info(
                "Execution is disabled. "
                "Run with execute:=true to move the robot."
            )
            flush_and_exit(0)

        logger.warning(
            "Waiting for fr3_arm_controller action server discovery..."
        )

       # Give DDS and MoveIt controller manager time to discover the action server.
       #Safe check: The following sleep is necessary to avoid the MoveItCpp error:
        
        time.sleep(5.0)

        logger.warning("Executing trajectory on the real robot...")

        execution_result = moveit.execute(
            plan_result.trajectory,
            controllers=["fr3_arm_controller"],
        )

        logger.info(
            f"Execution result: {execution_result}"
        )

        time.sleep(1.0)
        flush_and_exit(0)


    except Exception as error:
        logger.error(
            f"MoveItPy error: {error}"
        )
        flush_and_exit(1)


if __name__ == "__main__":
    main()












old version:


import argparse
import time

import os
import sys

import rclpy

from geometry_msgs.msg import PoseStamped

from moveit.planning import MoveItPy

from rclpy.logging import get_logger
0
from scipy.spatial.transform import Rotation



PLANNING_GROUP = "fr3_arm"

DEFAULT_BASE_FRAME = "fr3_link0"

DEFAULT_EE_LINK = "fr3_hand_tcp"




class CartesianController:


    def __init__(self):

        self.logger = get_logger(
            "cartesian_controller"
        )


        self.moveit = MoveItPy(
            node_name="fr3_cartesian_controller"
        )


        self.arm = self.moveit.get_planning_component(
            PLANNING_GROUP
        )


        self.logger.info(
            "Cartesian Controller initialized"
        )

#fee

    def move_relative(
        self,
        dx=0.0,
        dy=0.0,
        dz=0.0,
        execute=True
    ):


        self.arm.set_start_state_to_current_state()



        planning_scene_monitor = (
            self.moveit
            .get_planning_scene_monitor()
        )


        with planning_scene_monitor.read_only() as scene:


            current_state = scene.current_state


            transform = (
                current_state
                .get_global_link_transform(
                    DEFAULT_EE_LINK
                )
            ).copy()



        current_x = float(
            transform[0,3]
        )

        current_y = float(
            transform[1,3]
        )

        current_z = float(
            transform[2,3]
        )



        quaternion = Rotation.from_matrix(
            transform[:3,:3]
        ).as_quat()



        target_pose = PoseStamped()


        target_pose.header.frame_id = (
            DEFAULT_BASE_FRAME
        )



        target_pose.pose.position.x = (
            current_x + dx
        )


        target_pose.pose.position.y = (
            current_y + dy
        )


        target_pose.pose.position.z = (
            current_z + dz
        )



        # Keep current TCP orientation

        target_pose.pose.orientation.x = (
            float(quaternion[0])
        )

        target_pose.pose.orientation.y = (
            float(quaternion[1])
        )

        target_pose.pose.orientation.z = (
            float(quaternion[2])
        )

        target_pose.pose.orientation.w = (
            float(quaternion[3])
        )



        self.logger.info(
            f"""
Current TCP:

x = {current_x:.4f}
y = {current_y:.4f}
z = {current_z:.4f}


Target TCP:

x = {target_pose.pose.position.x:.4f}
y = {target_pose.pose.position.y:.4f}
z = {target_pose.pose.position.z:.4f}
"""
        )



        self.arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=DEFAULT_EE_LINK
        )



        self.logger.info(
            "Planning Cartesian trajectory..."
        )



        plan_result = self.arm.plan()



        if not plan_result:

            self.logger.error(
                "Planning failed"
            )

            return False



        if not execute:

            self.logger.info(
                "Planning finished. Execution disabled."
            )

            return True



        # Avoid MoveIt controller discovery issue

        time.sleep(5.0)



        self.logger.info(
            "Executing trajectory..."
        )



        result = self.moveit.execute(
            plan_result.trajectory,
            controllers=[
                "fr3_arm_controller"
            ]
        )



        self.logger.info(
            f"Execution result: {result}"
        )


        return True





    # -------------------------
    # Helper functions
    # -------------------------


    def move_down(
        self,
        distance
    ):

        return self.move_relative(
            dz=-distance
        )



    def move_up(
        self,
        distance
    ):

        return self.move_relative(
            dz=distance
        )



    def move_forward(
        self,
        distance
    ):

        return self.move_relative(
            dx=distance
        )



    def move_backward(
        self,
        distance
    ):

        return self.move_relative(
            dx=-distance
        )





# ==================================
# Standalone testing interface
# ==================================


def parse_arguments():

    parser = argparse.ArgumentParser(
        description=
        "FR3 Cartesian Motion Test"
    )


    parser.add_argument(
        "--dx",
        type=float,
        default=0.0
    )


    parser.add_argument(
        "--dy",
        type=float,
        default=0.0
    )


    parser.add_argument(
        "--dz",
        type=float,
        default=0.0
    )


    parser.add_argument(
        "--execute",
        type=str,
        default="false"
    )


    return parser.parse_known_args()[0]




def parse_bool(value):

    return value.lower() in [
        "true",
        "1",
        "yes",
        "on"
    ]


# Safe exit function to ensure proper shutdown of ROS2 nodes and processes
# Avoid MoveItPy bug
def safe_exit(code):

    sys.stdout.flush()
    sys.stderr.flush()

    os._exit(code)



def main():


    args = parse_arguments()


    rclpy.init()



    motion = CartesianController()



    success = motion.move_relative(

        dx=args.dx,

        dy=args.dy,

        dz=args.dz,

        execute=parse_bool(
            args.execute
        )
    )

    # safe_exit

    safe_exit(
        0 if success else 1
    )
    


    rclpy.shutdown()





if __name__ == "__main__":

    main()















## Update cartesian_move.py

import argparse
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from moveit.planning import MoveItPy
from rclpy.logging import get_logger
from scipy.spatial.transform import Rotation


PLANNING_GROUP = "fr3_arm"
DEFAULT_BASE_FRAME = "fr3_link0"
DEFAULT_EE_LINK = "fr3_hand_tcp"
ARM_CONTROLLER = "fr3_arm_controller"


class CartesianController:

    def __init__(self):
        self.logger = get_logger("cartesian_controller")

        self.moveit = MoveItPy(
            node_name="fr3_cartesian_controller"
        )

        self.arm = self.moveit.get_planning_component(
            PLANNING_GROUP
        )

        self.logger.info(
            "Cartesian controller initialized"
        )

    def move_relative(
        self,
        dx=0.0,
        dy=0.0,
        dz=0.0,
        execute=True
    ):
        """Move the TCP relative to its current position."""

        self.arm.set_start_state_to_current_state()

        # Read current TCP pose
        planning_scene_monitor = (
            self.moveit.get_planning_scene_monitor()
        )

        with planning_scene_monitor.read_only() as scene:
            transform = (
                scene.current_state
                .get_global_link_transform(
                    DEFAULT_EE_LINK
                )
            ).copy()

        current_x = float(transform[0, 3])
        current_y = float(transform[1, 3])
        current_z = float(transform[2, 3])

        quaternion = Rotation.from_matrix(
            transform[:3, :3]
        ).as_quat()

        # Create target pose
        target_pose = PoseStamped()
        target_pose.header.frame_id = DEFAULT_BASE_FRAME

        target_pose.pose.position.x = current_x + dx
        target_pose.pose.position.y = current_y + dy
        target_pose.pose.position.z = current_z + dz

        target_pose.pose.orientation.x = float(quaternion[0])
        target_pose.pose.orientation.y = float(quaternion[1])
        target_pose.pose.orientation.z = float(quaternion[2])
        target_pose.pose.orientation.w = float(quaternion[3])

        self.logger.info(
            "\n"
            f"Current TCP: "
            f"x={current_x:.4f}, "
            f"y={current_y:.4f}, "
            f"z={current_z:.4f}\n"
            f"Target TCP:  "
            f"x={target_pose.pose.position.x:.4f}, "
            f"y={target_pose.pose.position.y:.4f}, "
            f"z={target_pose.pose.position.z:.4f}"
        )

        # Plan motion
        self.arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=DEFAULT_EE_LINK
        )

        self.logger.info("Planning trajectory...")

        plan_result = self.arm.plan()

        if not plan_result:
            self.logger.error("Planning failed")
            return False

        if not execute:
            self.logger.info(
                "Planning succeeded. Execution disabled."
            )
            return True

        # Execute motion
        time.sleep(5.0)

        self.logger.info("Executing trajectory...")

        result = self.moveit.execute(
            plan_result.trajectory,
            controllers=[ARM_CONTROLLER]
        )

        self.logger.info(
            f"Execution result: {result}"
        )

        return True

    def move_down(self, distance):
        return self.move_relative(dz=-distance)

    def move_up(self, distance):
        return self.move_relative(dz=distance)

    def move_forward(self, distance):
        return self.move_relative(dx=distance)

    def move_backward(self, distance):
        return self.move_relative(dx=-distance)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="FR3 Cartesian motion test"
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
        action="store_true"
    )

    return parser.parse_known_args()[0]


def main():
    args = parse_arguments()

    rclpy.init()

    try:
        controller = CartesianController()

        controller.move_relative(
            dx=args.dx,
            dy=args.dy,
            dz=args.dz,
            execute=args.execute
        )

    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()

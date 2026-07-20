import os
import sys
import time

import rclpy
import numpy as np

from moveit.planning import MoveItPy
from moveit.core.robot_state import RobotState


def flush_and_exit(exit_code: int):
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)


def main():
    rclpy.init()

    moveit = MoveItPy(
        node_name="pick_place"
    )

    arm = moveit.get_planning_component(
        "fr3_arm"
    )

    robot_model = moveit.get_robot_model()

    # Correct way: use current robot state as start state
    arm.set_start_state_to_current_state()

    # Create goal state
    goal_state = RobotState(robot_model)

    # Set goal joint positions for the pick and place task ( minor adjustments may be needed based on the actual robot configuration and task requirements )

    goal_positions = np.array(
        [
            -0.125,
            -0.114,
            0.340,
            -1.512,
            -0.05,
            1.434,
            -2.302,
        ],
        dtype=np.float64,
    )

    goal_state.set_joint_group_positions(
        "fr3_arm",
        goal_positions
    )

    arm.set_goal_state(
        robot_state=goal_state
    )

    print("Planning...")

    plan_result = arm.plan()

    if plan_result:
        print("Planning succeeded.")

        # Give action client / controller discovery some time
        time.sleep(3.0)

        moveit.execute(
            plan_result.trajectory,
            controllers=[
                "fr3_arm_controller"
            ]
        )

        print("Execution finished.")
        flush_and_exit(0)

    else:
        print("Planning failed.")
        flush_and_exit(1)


if __name__ == "__main__":
    main()

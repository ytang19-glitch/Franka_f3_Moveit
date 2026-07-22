
import argparse
import time

import rclpy

from geometry_msgs.msg import PoseStamped

from moveit.planning import MoveItPy

from rclpy.logging import get_logger

from scipy.spatial.transform import Rotation


# ==================================
# Robot and MoveIt configuration
# ==================================

# MoveIt planning group defined in the SRDF file.
PLANNING_GROUP = "fr3_arm"

# Reference frame used for all Cartesian target poses.
DEFAULT_BASE_FRAME = "fr3_link0"

# Tool center point used to read and command the robot pose.
DEFAULT_EE_LINK = "fr3_hand_tcp"


# ==================================
# Cartesian motion controller
# ==================================


class CartesianController:


    # -------------------------
    # Controller initialization
    # -------------------------

    def __init__(self):

        """
        Initialize the FR3 Cartesian motion controller.

        This function:

        1. Creates a ROS 2 logger.
        2. Initializes the MoveItPy interface.
        3. Gets the MoveIt planning component for the FR3 arm.
        4. Prepares the controller for motion planning and execution.
        """

        self.logger = get_logger(
            "cartesian_controller"
        )


        # Create the MoveItPy interface.
        #
        # MoveItPy provides access to:
        # - Robot state
        # - Planning scene
        # - Motion planning
        # - Trajectory execution
        self.moveit = MoveItPy(
            node_name="fr3_cartesian_controller"
        )


        # Get the planning component associated with
        # the "fr3_arm" planning group.
        self.arm = self.moveit.get_planning_component(
            PLANNING_GROUP
        )


        self.logger.info(
            "Cartesian Controller initialized"
        )



    # -------------------------
    # Relative Cartesian motion
    # -------------------------

    def move_relative(
        self,
        dx=0.0,
        dy=0.0,
        dz=0.0,
        execute=True
    ):

        """
        Move the FR3 tool center point relative to its current pose.

        Parameters
        ----------
        dx : float
            Relative displacement along the base-frame x-axis in metres.

        dy : float
            Relative displacement along the base-frame y-axis in metres.

        dz : float
            Relative displacement along the base-frame z-axis in metres.

        execute : bool
            If True, execute the planned trajectory on the robot.

            If False, only perform motion planning without execution.

        Returns
        -------
        bool
            True if planning succeeds.

            False if planning fails.

        Important
        ---------
        This function creates a Cartesian pose goal.

        MoveIt may generate a joint-space path to reach the target pose.
        Therefore, the end-effector path is not guaranteed to be a
        perfectly straight Cartesian line.
        """


        # ----------------------------------
        # Step 1: Set current start state
        # ----------------------------------

        # Tell MoveIt to use the robot's current joint state
        # as the starting state for motion planning.
        self.arm.set_start_state_to_current_state()



        # ----------------------------------
        # Step 2: Access planning scene
        # ----------------------------------

        # Get the planning scene monitor.
        #
        # The planning scene contains:
        # - Current robot state
        # - Robot model
        # - Collision objects
        # - Attached objects
        planning_scene_monitor = (
            self.moveit
            .get_planning_scene_monitor()
        )


        # Read the planning scene safely without modifying it.
        with planning_scene_monitor.read_only() as scene:


            # Get the latest robot state from the planning scene.
            current_state = scene.current_state


            # Get the global transformation matrix of the TCP.
            #
            # The transform is a 4 × 4 homogeneous matrix:
            #
            # [ R11 R12 R13 x ]
            # [ R21 R22 R23 y ]
            # [ R31 R32 R33 z ]
            # [  0   0   0  1 ]
            #
            # The upper-left 3 × 3 section is orientation.
            # The last column contains position.
            transform = (
                current_state
                .get_global_link_transform(
                    DEFAULT_EE_LINK
                )
            ).copy()



        # ----------------------------------
        # Step 3: Read current TCP position
        # ----------------------------------

        # Extract the current TCP position from
        # the homogeneous transformation matrix.
        current_x = float(
            transform[0, 3]
        )

        current_y = float(
            transform[1, 3]
        )

        current_z = float(
            transform[2, 3]
        )



        # ----------------------------------
        # Step 4: Read current orientation
        # ----------------------------------

        # Convert the 3 × 3 rotation matrix into a quaternion.
        #
        # SciPy returns quaternion values in this order:
        #
        # [x, y, z, w]
        quaternion = Rotation.from_matrix(
            transform[:3, :3]
        ).as_quat()



        # ----------------------------------
        # Step 5: Create target pose
        # ----------------------------------

        # Create a ROS 2 PoseStamped message for
        # the desired end-effector pose.
        target_pose = PoseStamped()


        # Define the coordinate frame in which the target
        # Cartesian position is expressed.
        target_pose.header.frame_id = (
            DEFAULT_BASE_FRAME
        )



        # Add the requested displacement to the
        # current TCP position.
        target_pose.pose.position.x = (
            current_x + dx
        )


        target_pose.pose.position.y = (
            current_y + dy
        )


        target_pose.pose.position.z = (
            current_z + dz
        )



        # ----------------------------------
        # Step 6: Preserve TCP orientation
        # ----------------------------------

        # Keep the current TCP orientation unchanged.
        #
        # Only the position changes.
        # The tool should not rotate during the move.
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



        # ----------------------------------
        # Step 7: Print motion information
        # ----------------------------------

        # Display the current and target TCP positions
        # before planning.
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



        # ----------------------------------
        # Step 8: Set MoveIt pose goal
        # ----------------------------------

        # Set the Cartesian target pose for the specified
        # end-effector link.
        #
        # MoveIt will use inverse kinematics to find a
        # valid joint configuration for this pose.
        self.arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=DEFAULT_EE_LINK
        )



        # ----------------------------------
        # Step 9: Plan robot motion
        # ----------------------------------

        self.logger.info(
            "Planning Cartesian pose trajectory..."
        )


        # Request a collision-free trajectory from MoveIt.
        #
        # The resulting trajectory contains joint positions,
        # velocities, accelerations, and timing information.
        plan_result = self.arm.plan()



        # Check whether MoveIt successfully generated a plan.
        if not plan_result:

            self.logger.error(
                "Planning failed"
            )

            return False



        # ----------------------------------
        # Step 10: Planning-only mode
        # ----------------------------------

        # Stop after planning if execution is disabled.
        #
        # This is useful for testing whether:
        # - The target pose is reachable
        # - Inverse kinematics succeeds
        # - Collision checking succeeds
        # - Motion planning succeeds
        if not execute:

            self.logger.info(
                "Planning finished. Execution disabled."
            )

            return True



        # ----------------------------------
        # Step 11: Wait for controller discovery
        # ----------------------------------

        # Give MoveIt time to discover and connect to
        # the trajectory controller.
        #
        # This is currently used as a workaround for
        # delayed controller discovery.
        time.sleep(5.0)



        # ----------------------------------
        # Step 12: Execute trajectory
        # ----------------------------------

        self.logger.info(
            "Executing trajectory..."
        )


        # Send the planned joint trajectory to the
        # FR3 arm controller.
        #
        # The execution chain is:
        #
        # MoveIt
        #   ↓
        # fr3_arm_controller
        #   ↓
        # ros2_control
        #   ↓
        # franka_hardware
        #   ↓
        # libfranka / FCI
        #   ↓
        # Franka FR3
        result = self.moveit.execute(
            plan_result.trajectory,
            controllers=[
                "fr3_arm_controller"
            ]
        )



        # Print the execution result returned by MoveIt.
        self.logger.info(
            f"Execution result: {result}"
        )


        return True





    # ==================================
    # Direction helper functions
    # ==================================


    # -------------------------
    # Move downward
    # -------------------------

    def move_down(
        self,
        distance
    ):

        """
        Move the TCP downward along the negative z-axis.

        Parameters
        ----------
        distance : float
            Downward movement distance in metres.
        """

        return self.move_relative(
            dz=-distance
        )



    # -------------------------
    # Move upward
    # -------------------------

    def move_up(
        self,
        distance
    ):

        """
        Move the TCP upward along the positive z-axis.

        Parameters
        ----------
        distance : float
            Upward movement distance in metres.
        """

        return self.move_relative(
            dz=distance
        )



    # -------------------------
    # Move forward
    # -------------------------

    def move_forward(
        self,
        distance
    ):

        """
        Move the TCP forward along the positive x-axis.

        Parameters
        ----------
        distance : float
            Forward movement distance in metres.

        Note
        ----
        The physical meaning of "forward" depends on the
        orientation of the fr3_link0 coordinate frame.
        """

        return self.move_relative(
            dx=distance
        )



    # -------------------------
    # Move backward
    # -------------------------

    def move_backward(
        self,
        distance
    ):

        """
        Move the TCP backward along the negative x-axis.

        Parameters
        ----------
        distance : float
            Backward movement distance in metres.
        """

        return self.move_relative(
            dx=-distance
        )





# ==================================
# Command-line argument interface
# ==================================


def parse_arguments():

    """
    Read Cartesian movement values from the command line.

    Supported arguments
    -------------------
    --dx
        Relative x-axis displacement in metres.

    --dy
        Relative y-axis displacement in metres.

    --dz
        Relative z-axis displacement in metres.

    --execute
        Whether the planned trajectory should be executed.

    Example
    -------
    ros2 run fr3_moveit_python motion \
        --dx 0.0 \
        --dy 0.0 \
        --dz -0.05 \
        --execute true
    """

    parser = argparse.ArgumentParser(
        description=
        "FR3 Cartesian Motion Test"
    )


    parser.add_argument(
        "--dx",
        type=float,
        default=0.0,
        help=
        "Relative x displacement in metres"
    )


    parser.add_argument(
        "--dy",
        type=float,
        default=0.0,
        help=
        "Relative y displacement in metres"
    )


    parser.add_argument(
        "--dz",
        type=float,
        default=0.0,
        help=
        "Relative z displacement in metres"
    )


    parser.add_argument(
        "--execute",
        type=str,
        default="false",
        help=
        "Execute trajectory: true or false"
    )


    # parse_known_args() is used because ROS 2 may add
    # additional command-line arguments automatically.
    return parser.parse_known_args()[0]




# ==================================
# Boolean argument conversion
# ==================================


def parse_bool(value):

    """
    Convert a command-line string into a Boolean value.

    Values interpreted as True:
    - true
    - 1
    - yes
    - on

    All other values are interpreted as False.
    """

    return value.lower() in [
        "true",
        "1",
        "yes",
        "on"
    ]





# ==================================
# Main program entry point
# ==================================


def main():

    """
    Run the standalone FR3 Cartesian motion test.

    Program sequence
    ----------------
    1. Read command-line arguments.
    2. Initialize ROS 2.
    3. Initialize the Cartesian controller.
    4. Plan or execute the requested relative movement.
    5. Shut down ROS 2.
    """


    # Read movement and execution arguments.
    args = parse_arguments()


    # Initialize the ROS 2 Python context.
    rclpy.init()



    try:

        # Create the FR3 Cartesian motion controller.
        motion = CartesianController()



        # Plan or execute the requested relative TCP movement.
        success = motion.move_relative(

            dx=args.dx,

            dy=args.dy,

            dz=args.dz,

            execute=parse_bool(
                args.execute
            )
        )


        if not success:

            get_logger(
                "fr3_cartesian_controller"
            ).error(
                "Cartesian motion command failed"
            )


    finally:

        # Always shut down ROS 2, including when
        # planning or execution raises an exception.
        rclpy.shutdown()


if __name__ == "__main__":

    main()
```


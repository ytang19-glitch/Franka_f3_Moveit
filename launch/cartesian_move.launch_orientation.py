import os
import yaml

from ament_index_python.packages import (
    get_package_share_directory,
)

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
)

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import (
    ParameterValue,
)


# ==========================================================
# YAML loader
# ==========================================================

def load_yaml(
    package_name: str,
    relative_path: str,
):

    package_share = get_package_share_directory(
        package_name
    )

    absolute_path = os.path.join(
        package_share,
        relative_path,
    )

    with open(
        absolute_path,
        "r",
        encoding="utf-8",
    ) as yaml_file:

        return yaml.safe_load(
            yaml_file
        )


# ==========================================================
# Main launch description
# ==========================================================

def generate_launch_description():

    # ------------------------------------------------------
    # Robot configuration
    # ------------------------------------------------------

    robot_ip = LaunchConfiguration(
        "robot_ip"
    )

    load_gripper = LaunchConfiguration(
        "load_gripper"
    )

    ee_id = LaunchConfiguration(
        "ee_id"
    )

    use_fake_hardware = LaunchConfiguration(
        "use_fake_hardware"
    )

    fake_sensor_commands = LaunchConfiguration(
        "fake_sensor_commands"
    )

    # ------------------------------------------------------
    # Cartesian position
    # ------------------------------------------------------

    dx = LaunchConfiguration(
        "dx"
    )

    dy = LaunchConfiguration(
        "dy"
    )

    dz = LaunchConfiguration(
        "dz"
    )

    # ------------------------------------------------------
    # Cartesian orientation
    # ------------------------------------------------------

    droll = LaunchConfiguration(
        "droll"
    )

    dpitch = LaunchConfiguration(
        "dpitch"
    )

    dyaw = LaunchConfiguration(
        "dyaw"
    )

    # ------------------------------------------------------
    # Other controller settings
    # ------------------------------------------------------

    execute = LaunchConfiguration(
        "execute"
    )

    base_frame = LaunchConfiguration(
        "base_frame"
    )

    ee_link = LaunchConfiguration(
        "ee_link"
    )

    # ======================================================
    # Launch arguments
    # ======================================================

    declared_arguments = [

        # --------------------------------------------------
        # Robot
        # --------------------------------------------------

        DeclareLaunchArgument(
            "robot_ip",
            default_value="172.16.0.2",
            description="FR3 robot IP address",
        ),

        DeclareLaunchArgument(
            "load_gripper",
            default_value="true",
            description="Load Franka gripper",
        ),

        DeclareLaunchArgument(
            "ee_id",
            default_value="franka_hand",
            description="End-effector ID",
        ),

        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Use fake ros2_control hardware",
        ),

        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="false",
            description="Enable fake sensor commands",
        ),

        # --------------------------------------------------
        # Position
        # --------------------------------------------------

        DeclareLaunchArgument(
            "dx",
            default_value="0.0",
            description=(
                "Relative X displacement in metres"
            ),
        ),

        DeclareLaunchArgument(
            "dy",
            default_value="0.0",
            description=(
                "Relative Y displacement in metres"
            ),
        ),

        DeclareLaunchArgument(
            "dz",
            default_value="0.0",
            description=(
                "Relative Z displacement in metres"
            ),
        ),

        # --------------------------------------------------
        # Orientation
        # --------------------------------------------------

        DeclareLaunchArgument(
            "droll",
            default_value="0.0",
            description=(
                "Relative roll rotation in radians"
            ),
        ),

        DeclareLaunchArgument(
            "dpitch",
            default_value="0.0",
            description=(
                "Relative pitch rotation in radians"
            ),
        ),

        DeclareLaunchArgument(
            "dyaw",
            default_value="0.0",
            description=(
                "Relative yaw rotation in radians"
            ),
        ),

        # --------------------------------------------------
        # Execution
        # --------------------------------------------------

        DeclareLaunchArgument(
            "execute",
            default_value="false",
            description=(
                "Execute the planned trajectory"
            ),
        ),

        # --------------------------------------------------
        # Frames
        # --------------------------------------------------

        DeclareLaunchArgument(
            "base_frame",
            default_value="fr3_link0",
            description=(
                "Reference frame used for target pose"
            ),
        ),

        DeclareLaunchArgument(
            "ee_link",
            default_value="fr3_hand_tcp",
            description=(
                "End-effector TCP link"
            ),
        ),
    ]

    # ======================================================
    # Robot description
    # Official Franka FR3 URDF
    # ======================================================

    fr3_urdf_xacro = os.path.join(

        get_package_share_directory(
            "franka_description"
        ),

        "robots",
        "fr3",
        "fr3.urdf.xacro",
    )

    robot_description_command = Command(
        [
            FindExecutable(
                name="xacro"
            ),

            " ",
            fr3_urdf_xacro,

            " hand:=",
            load_gripper,

            " robot_ip:=",
            robot_ip,

            " ee_id:=",
            ee_id,

            " use_fake_hardware:=",
            use_fake_hardware,

            " fake_sensor_commands:=",
            fake_sensor_commands,

            " ros2_control:=true",
        ]
    )

    robot_description = {

        "robot_description":
            ParameterValue(
                robot_description_command,
                value_type=str,
            )
    }

    # ======================================================
    # Semantic robot description
    # Official Franka SRDF
    # ======================================================

    fr3_srdf_xacro = os.path.join(

        get_package_share_directory(
            "franka_description"
        ),

        "robots",
        "fr3",
        "fr3.srdf.xacro",
    )

    robot_description_semantic_command = Command(
        [
            FindExecutable(
                name="xacro"
            ),

            " ",
            fr3_srdf_xacro,

            " hand:=",
            load_gripper,

            " ee_id:=",
            ee_id,
        ]
    )

    robot_description_semantic = {

        "robot_description_semantic":
            ParameterValue(
                robot_description_semantic_command,
                value_type=str,
            )
    }

    # ======================================================
    # Kinematics configuration
    # ======================================================

    kinematics_config = {

        "robot_description_kinematics":
            load_yaml(
                "franka_fr3_moveit_config",
                "config/kinematics.yaml",
            )
    }

    # ======================================================
    # Joint limits
    # ======================================================

    joint_limits_config = {

        "robot_description_planning":
            load_yaml(
                "franka_fr3_moveit_config",
                "config/fr3_joint_limits.yaml",
            )
    }

    # ======================================================
    # OMPL planning configuration
    # ======================================================

    ompl_yaml = load_yaml(
        "franka_fr3_moveit_config",
        "config/ompl_planning.yaml",
    )

    ompl_pipeline = {

        "planning_plugins": [
            "ompl_interface/OMPLPlanner",
        ],

        "request_adapters": [

            "default_planning_request_adapters/"
            "ResolveConstraintFrames",

            "default_planning_request_adapters/"
            "ValidateWorkspaceBounds",

            "default_planning_request_adapters/"
            "CheckStartStateBounds",

            "default_planning_request_adapters/"
            "CheckStartStateCollision",
        ],

        "response_adapters": [

            "default_planning_response_adapters/"
            "AddTimeOptimalParameterization",

            "default_planning_response_adapters/"
            "ValidateSolution",

            "default_planning_response_adapters/"
            "DisplayMotionPath",
        ],

        "start_state_max_bounds_error": 0.1,
    }

    if ompl_yaml:

        ompl_pipeline.update(
            ompl_yaml
        )

    # ======================================================
    # MoveItPy / MoveItCpp configuration
    # ======================================================

    moveit_py_configuration = {

        "planning_scene_monitor_options": {

            "name":
                "planning_scene_monitor",

            "robot_description":
                "robot_description",

            "joint_state_topic":
                "/joint_states",

            "attached_collision_object_topic":
                "/attached_collision_object",

            "publish_planning_scene_topic":
                "/moveit_cpp/publish_planning_scene",

            "monitored_planning_scene_topic":
                "/monitored_planning_scene",

            "wait_for_initial_state_timeout":
                10.0,
        },

        "planning_pipelines": {

            "pipeline_names": [
                "ompl"
            ],
        },

        "plan_request_params": {

            "planning_attempts":
                1,

            "planning_pipeline":
                "ompl",

            "planner_id":
                "RRTConnectkConfigDefault",

            "planning_time":
                5.0,

            # Start slowly on real FR3
            "max_velocity_scaling_factor":
                0.1,

            "max_acceleration_scaling_factor":
                0.1,
        },

        "ompl":
            ompl_pipeline,
    }

    # ======================================================
    # MoveIt controller configuration
    # ======================================================

    controller_yaml = load_yaml(

        "franka_fr3_moveit_config",

        "config/fr3_controllers.yaml",
    )

    moveit_controllers = {

        "moveit_simple_controller_manager":
            controller_yaml,

        "moveit_controller_manager":
            (
                "moveit_simple_controller_manager/"
                "MoveItSimpleControllerManager"
            ),
    }

    # ======================================================
    # Trajectory execution
    # ======================================================

    trajectory_execution = {

        "moveit_manage_controllers":
            True,

        "trajectory_execution."
        "allowed_execution_duration_scaling":
            1.2,

        "trajectory_execution."
        "allowed_goal_duration_margin":
            0.5,

        "trajectory_execution."
        "allowed_start_tolerance":
            0.01,
    }

    # ======================================================
    # Cartesian controller node
    # ======================================================

    cartesian_move_node = Node(

        package="fr3_moveit_python",

        executable="cartesian_move",

        name="fr3_cartesian_move",

        output="screen",

        arguments=[

            # ----------------------------------------------
            # Position
            # ----------------------------------------------

            "--dx",
            dx,

            "--dy",
            dy,

            "--dz",
            dz,

            # ----------------------------------------------
            # Orientation
            # ----------------------------------------------

            "--droll",
            droll,

            "--dpitch",
            dpitch,

            "--dyaw",
            dyaw,

            # ----------------------------------------------
            # Execution
            # ----------------------------------------------

            "--execute",
            execute,

            # ----------------------------------------------
            # Frames
            # ----------------------------------------------

            "--base-frame",
            base_frame,

            "--ee-link",
            ee_link,
        ],

        parameters=[

            robot_description,

            robot_description_semantic,

            kinematics_config,

            joint_limits_config,

            moveit_py_configuration,

            moveit_controllers,

            trajectory_execution,

            {
                "use_sim_time":
                    False,
            },
        ],
    )

    # ======================================================
    # Return launch description
    # ======================================================

    return LaunchDescription(

        declared_arguments
        +
        [
            cartesian_move_node
        ]
    )

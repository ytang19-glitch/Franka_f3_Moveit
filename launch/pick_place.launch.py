import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def load_yaml(package_name, path):
    pkg = get_package_share_directory(package_name)
    with open(os.path.join(pkg, path), "r") as f:
        return yaml.safe_load(f)


def generate_launch_description():

    robot_ip = LaunchConfiguration("robot_ip")

    declared_arguments = [
        DeclareLaunchArgument(
            "robot_ip",
            default_value="172.16.0.2",
        )
    ]

    # ==========================
    # URDF
    # ==========================

    urdf = os.path.join(
        get_package_share_directory("franka_description"),
        "robots",
        "fr3",
        "fr3.urdf.xacro",
    )

    robot_description = {
        "robot_description": ParameterValue(
            Command([
                FindExecutable(name="xacro"),
                " ",
                urdf,
                " robot_ip:=",
                robot_ip,
                " hand:=true",
                " ros2_control:=true",
            ]),
            value_type=str,
        )
    }

    # ==========================
    # SRDF
    # ==========================

    srdf = os.path.join(
        get_package_share_directory("franka_description"),
        "robots",
        "fr3",
        "fr3.srdf.xacro",
    )

    robot_description_semantic = {
        "robot_description_semantic": ParameterValue(
            Command([
                FindExecutable(name="xacro"),
                " ",
                srdf,
                " hand:=true",
            ]),
            value_type=str,
        )
    }

    # ==========================
    # Kinematics
    # ==========================

    kinematics = {
        "robot_description_kinematics": load_yaml(
            "franka_fr3_moveit_config",
            "config/kinematics.yaml",
        )
    }

    joint_limits = {
        "robot_description_planning": load_yaml(
            "franka_fr3_moveit_config",
            "config/fr3_joint_limits.yaml",
        )
    }

    # ==========================
    # OMPL
    # ==========================

    ompl= load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
    )


    ompl.update({

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

        # AddTimeOptimalParameterization add reasonable time parameter to trajectory
        "response_adapters": [
            "default_planning_response_adapters/"
            "AddTimeOptimalParameterization",
            "default_planning_response_adapters/"
            "ValidateSolution",
            "default_planning_response_adapters/"
            "DisplayMotionPath",
        ],
        "start_state_max_bounds_error": 0.1,
    })



    #From the official FR3 MoveItCpp configuration, we can set the planning attempts to 1, 
    #and the max velocity and acceleration scaling factors to 0.1. This is a reasonable starting point for Cartesian motion planning with the FR3 robot.    
    #franka_fr3_moveit_config/config: cd ~/franka_ros2_ws/src/franka_fr3_moveit_config/launch
    #nano ~/franka_ros2_ws/src/franka_fr3_moveit_config/launch/moveit.launch.py

    moveit_config = {
        "planning_scene_monitor_options": {
            "name": "planning_scene_monitor",
            "robot_description": "robot_description",
            "joint_state_topic": "/joint_states",
            "wait_for_initial_state_timeout": 10.0,
        },
        "planning_pipelines": {
            "pipeline_names": [
                "ompl",
            ]
        },

        "default_planning_pipeline": "ompl",

        
        "plan_request_params": {
            "planning_pipeline": "ompl",
            "planner_id": "RRTConnectkConfigDefault",
            "planning_time": 5.0,
            # plan_request_params
            "max_velocity_scaling_factor": 0.05,
            "max_acceleration_scaling_factor": 0.05,

        },
        "ompl": ompl,
    }

    # ==========================
    # Controller
    # ==========================

    controllers = {
        "moveit_simple_controller_manager": load_yaml(
            "franka_fr3_moveit_config",
            "config/fr3_controllers.yaml",
        ),
        "moveit_controller_manager":
            "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }
    # node of the pick_place.py script
    node = Node(
        package="fr3_moveit_python",
        executable="pick_place",
        name="fr3_pick_place",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics,
            joint_limits,
            moveit_config,
            controllers,
            {"use_sim_time": False},
        ],
    )

    return LaunchDescription(
        declared_arguments + [
            node,
        ]
    )

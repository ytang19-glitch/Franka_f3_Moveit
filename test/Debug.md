

[pick_place-1] [INFO] [1784576579.905852650] [moveit_1697702080.moveit.ros.current_state_monitor]: Listening to joint states on topic 'joint_states'
[pick_place-1] [INFO] [1784576579.911822258] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Listening to '/attached_collision_object' for attached collision objects
[pick_place-1] [INFO] [1784576579.913016068] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Publishing maintained planning scene on 'monitored_planning_scene'
[pick_place-1] [INFO] [1784576579.913137599] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Starting planning scene monitor
[pick_place-1] [INFO] [1784576579.913497413] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Listening to '/planning_scene'
[pick_place-1] [INFO] [1784576579.913514051] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Starting world geometry update monitor for collision objects, attached objects, octomap updates.
[pick_place-1] [INFO] [1784576579.913901692] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Listening to 'collision_object'
[pick_place-1] [INFO] [1784576579.914282865] [moveit_1697702080.moveit.ros.planning_scene_monitor]: Listening to 'planning_scene_world' for planning scene world geometry
[pick_place-1] [WARN] [1784576579.914735917] [moveit_1697702080.moveit.ros.occupancy_map_monitor]: Resolution not specified for Octomap. Assuming resolution = 0.1 instead
[pick_place-1] [ERROR] [1784576579.914752118] [moveit_1697702080.moveit.ros.occupancy_map_monitor]: No 3D sensor plugin(s) defined for octomap updates
[pick_place-1] [INFO] [1784576579.997928070] [moveit_1697702080.moveit.ros.planning_pipeline]: Successfully loaded planner 'OMPL'
[pick_place-1] [WARN] [1784576579.997954252] [moveit_1697702080.moveit.ros.planning_pipeline]: No planning request adapter names specified.
[pick_place-1] [WARN] [1784576579.997959365] [moveit_1697702080.moveit.ros.planning_pipeline]: No planning response adapter names specified.
[pick_place-1] [INFO] [1784576580.043148230] [moveit_1697702080.moveit.plugins.simple_controller_manager]: Added FollowJointTrajectory controller for fr3_arm_controller
[pick_place-1] [INFO] [1784576580.043210296] [moveit_1697702080.moveit.plugins.simple_controller_manager]: fr3_gripper will command a max effort of: 0
[pick_place-1] [INFO] [1784576580.046778381] [moveit_1697702080.moveit.plugins.simple_controller_manager]: Added GripperCommand controller for fr3_gripper
[pick_place-1] [INFO] [1784576580.046947339] [moveit_1697702080.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784576580.046982047] [moveit_1697702080.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784576580.047803977] [moveit_1697702080.moveit.ros.trajectory_execution_manager]: Trajectory execution is not managing controllers
[pick_place-1] Traceback (most recent call last):
[pick_place-1]   File "/home/yujietang/franka_ros2_ws/install/fr3_moveit_python/lib/fr3_moveit_python/pick_place", line 33, in <module>
[pick_place-1]     sys.exit(load_entry_point('fr3-moveit-python==0.0.1', 'console_scripts', 'pick_place')())
[pick_place-1]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[pick_place-1]   File "/home/yujietang/franka_ros2_ws/build/fr3_moveit_python/fr3_moveit_python/pick_place.py", line 30, in main
[pick_place-1]     arm.set_start_state(
[pick_place-1] TypeError: set_start_state(): incompatible function arguments. The following argument types are supported:
[pick_place-1]     1. (self: moveit.planning.PlanningComponent, configuration_name: Optional[str] = None, robot_state: Optional[moveit.core.robot_state.RobotState] = None) -> bool
[pick_place-1] 
[pick_place-1] Invoked with: <moveit.planning.PlanningComponent object at 0x78de7a78ed70>, <moveit.core.robot_state.RobotState object at 0x78de7a5033b0>
[pick_place-1] [INFO] [1784576580.136403807] [moveit_1697702080.moveit.ros.moveit_cpp]: Deleting MoveItCpp
[ERROR] [pic





k_place-1]: process has died [pid 221142, exit code -11, cmd '/home/yujietang/franka_ros2_ws/install/fr3_moveit_python/lib/fr3_moveit_python/pick_place --ros-args -r __node:=fr3_pick_place --params-file /tmp/launch_params_xbglb9d4 --params-file /tmp/launch_params_1rl3fon1 --params-file /tmp/launch_params_dm0mu7fx --params-file /tmp/launch_params_rjkgqqv1 --params-file /tmp/launch_params_1ya8_4h1 --params-file /tmp/launch_params_4_j7m6l1 --params-file /tmp/launch_params_5ihjxe61'].





import rclpy

from moveit.planning import MoveItPy
from moveit.core.robot_state import RobotState


def main():

    rclpy.init()


    moveit = MoveItPy(
        node_name="pick_place"
    )


    arm = moveit.get_planning_component(
        "fr3_arm"
    )


    robot_model = moveit.get_robot_model()


    robot_state = RobotState(
        robot_model
    )


    current_state = robot_model.get_current_state()


    arm.set_start_state(
        robot_state=current_state
    )


    arm.set_goal_state(
        joint_positions={

            "fr3_joint1":0.0,
            "fr3_joint2":-0.5,
            "fr3_joint3":0.0,
            "fr3_joint4":-2.0,
            "fr3_joint5":0.0,
            "fr3_joint6":1.5,
            "fr3_joint7":0.7

        }
    )


    print("Planning...")


    plan_result = arm.plan()


    if plan_result:

        print("Planning succeeded.")


        moveit.execute(
            plan_result.trajectory,
            [
                "fr3_arm_controller"
            ]
        )
    else:
        
        print("Planning failed.")

    rclpy.shutdown()



if __name__=="__main__":
    main()




TypeError: set_goal_state(): incompatible function arguments

import rclpy

from moveit.planning import MoveItPy
from moveit.core.robot_state import RobotState


def main():
    rclpy.init()

    moveit = MoveItPy(
        node_name="pick_place"
    )

    arm = moveit.get_planning_component(
        "fr3_arm"
    )

    robot_model = moveit.get_robot_model()

    current_state = robot_model.get_current_state()

    arm.set_start_state(
        robot_state=current_state
    )

    goal_state = RobotState(
        robot_model
    )

    goal_state.set_joint_group_positions(
        "fr3_arm",
        [
            0.0,
            -0.5,
            0.0,
            -2.0,
            0.0,
            1.5,
            0.7,
        ]
    )

    arm.set_goal_state(
        robot_state=goal_state
    )

    print("Planning...")

    plan_result = arm.plan()

    if plan_result:
        print("Planning succeeded.")

        moveit.execute(
            plan_result.trajectory,
            controllers=[
                "fr3_arm_controller"
            ]
        )
    else:
        print("Planning failed.")

    rclpy.shutdown()


if __name__ == "__main__":
    main()



检查 set_joint_group_positions() 是否支持你的版本：

python3 - <<'PY'
from moveit.core.robot_state import RobotState
print(RobotState.set_joint_group_positions.__doc__)
PY

也检查 planning group 名字是不是正确：

ros2 param get /move_group robot_description_semantic | grep fr3_arm
修改后重新编译
cd ~/franka_ros2_ws
colcon build --packages-select fr3_moveit_python --symlink-install
source install/setup.bash

然后重新运行：

ros2 launch fr3_moveit_python pick_place.launch.py





yujietang@yujietang-System-Product-Name:~$ python3 - <<'PY'
from moveit.core.robot_state import RobotState
print(RobotState.set_joint_group_positions.__doc__)
PY

           Sets the positions of the joints in the specified joint model group.

	   Args:
               joint_model_group_name (str):
               position_values (:py:class:`numpy.ndarray`): The positions of the joints in the joint model group.
       
yujietang@yujietang-System-Product-Name:~$ ros2 param get /move_group robot_description_semantic | grep fr3_arm
  <group name="fr3_arm">
  <group_state group="fr3_arm" name="ready">
  <group_state group="fr3_arm" name="extended">
  <end_effector group="fr3_hand" name="fr3_hand" parent_group="fr3_arm" parent_link="fr3_hand_tcp"/>




anager]: Trajectory execution is not managing controllers
[pick_place-1] Traceback (most recent call last):
[pick_place-1]   File "/home/yujietang/franka_ros2_ws/install/fr3_moveit_python/lib/fr3_moveit_python/pick_place", line 33, in <module>
[pick_place-1]     sys.exit(load_entry_point('fr3-moveit-python==0.0.1', 'console_scripts', 'pick_place')())
[pick_place-1]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[pick_place-1]   File "/home/yujietang/franka_ros2_ws/build/fr3_moveit_python/fr3_moveit_python/pick_place.py", line 20, in main
[pick_place-1]     current_state = robot_model.get_current_state()
[pick_place-1]                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[pick_place-1] AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'
[pick_place-1] [INFO] [1784579139.219604596] [moveit_3908876052.moveit.ros.moveit_cpp]: Deleting MoveItCpp
[ERROR] [pick_place-1]: process has died [pid 245618, exit code -11, cmd '/home/yujietang/franka_ros2_ws/install/fr3_moveit_python/lib/fr3_moveit_python/pick_place --ros-args -r __node:=fr3_pick_place --params-file /tmp/launch_params_0spq6ey3 --params-file /tmp/launch_params_sfu7_a7v --params-file /tmp/launch_params_4hydsqe5 --params-file /tmp/launch_params_t7dlddpp --params-file /tmp/launch_params_kvd8nc0x --params-file /tmp/launch_params_w90g6gx0 --params-file /tmp/launch_params_rd3hng96'].






现在新的错误已经很明确：

AttributeError: 'moveit.core.robot_model.RobotModel' object has no attribute 'get_current_state'

意思是：robot_model 只是机器人模型，不负责读取当前机器人状态。
所以这一行是错的：

current_state = robot_model.get_current_state()

在 MoveItPy 里，start state 最简单应该直接用：

arm.set_start_state_to_current_state()
你现在应该这样改

你的 group name fr3_arm 是正确的，因为你查到了：

<group name="fr3_arm">

set_joint_group_positions() 也存在，但它要求的是：

numpy.ndarray

所以 goal joint position 最好用 numpy.array()。

推荐完整版本

把 pick_place.py 改成这样：

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

    goal_positions = np.array(
        [
            0.0,
            -0.5,
            0.0,
            -2.0,
            0.0,
            1.5,
            0.7,
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
关键修改点

删除这个：

current_state = robot_model.get_current_state()

删除这个：

arm.set_start_state(
    robot_state=current_state
)

改成：

arm.set_start_state_to_current_state()

然后 goal state 用：

goal_state = RobotState(robot_model)

goal_state.set_joint_group_positions(
    "fr3_arm",
    np.array([...], dtype=np.float64)
)

arm.set_goal_state(robot_state=goal_state)
重新编译
cd ~/franka_ros2_ws
colcon build --packages-select fr3_moveit_python --symlink-install
source install/setup.bash

再运行：

ros2 launch fr3_moveit_python pick_place.launch.py

现在你的错误链条是：

旧错误 1: set_start_state(current_state) 参数错误
已修复

旧错误 2: set_goal_state(joint_positions={...}) 参数错误
需要用 RobotState + numpy.ndarray

当前错误 3: robot_model.get_current_state() 不存在
需要用 arm.set_start_state_to_current_state()

所以这次重点是：不要从 robot_model 读取 current state；让 PlanningComponent 自己设置当前 start state。



[pick_place-1] [WARN] [1784580369.504631635] [pick_place]: Parameter 'plan_request_params.max_velocity_scaling_factor' not found in config use default value instead, check parameter type and namespace in YAML file
[pick_place-1] [WARN] [1784580369.504641341] [pick_place]: Parameter 'plan_request_params.max_acceleration_scaling_factor' not found in config use default value instead, check parameter type and namespace in YAML file
[pick_place-1] [WARN] [1784580369.504769845] [moveit_3798351232.moveit.planners.ompl.planning_context_manager]: Cannot find planning configuration for group 'fr3_arm' using planner 'RRTConnectkConfigDefault'. Will use defaults instead.
[pick_place-1] [WARN] [1784580369.504982779] [moveit_3798351232.moveit.planners.ompl.model_based_planning_context]: It looks like the planning volume was not specified.
[pick_place-1] [INFO] [1784580369.505259493] [moveit_3798351232.moveit.planners.ompl.model_based_planning_context]: Planner configuration 'fr3_arm' will use planner 'geometric::RRTConnect'. Additional configuration parameters will be set when the planner is constructed.
[pick_place-1] [INFO] [1784580369.505374956] [pick_place]: Calling Planner 'OMPL'
[pick_place-1] [INFO] [1784580372.511510743] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.511557463] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.511598883] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.511613503] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.511641143] [moveit_3798351232.moveit.ros.trajectory_execution_manager]: Validating trajectory with allowed_start_tolerance 0.01
[pick_place-1] [INFO] [1784580372.524370316] [moveit_3798351232.moveit.ros.trajectory_execution_manager]: Starting trajectory execution ...
[pick_place-1] [INFO] [1784580372.524526074] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.524553536] [moveit_3798351232.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784580372.524751832] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: sending trajectory to fr3_arm_controller
[pick_place-1] [INFO] [1784580372.525323220] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: fr3_arm_controller started execution
[pick_place-1] [WARN] [1784580372.525346521] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: Goal request rejected
[pick_place-1] [ERROR] [1784580372.525326098] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: Goal was rejected by server
[pick_place-1] [ERROR] [1784580372.525388200] [moveit_3798351232.moveit.ros.trajectory_execution_manager]: Failed to send trajectory part 1 of 1 to controller fr3_arm_controller
[pick_place-1] [INFO] [1784580372.525404852] [moveit_3798351232.moveit.ros.trajectory_execution_manager]: Completed trajectory execution with status ABORTED ...
[pick_place-1] Planning...
[pick_place-1] Planning succeeded.
[pick_place-1] Execution finished.
[INFO] [pick_place-1]: process has finished cleanly [pid 257338]




 ros2 param get /fr3_arm_controller joints
String values are: ['fr3_joint1', 'fr3_joint2', 'fr3_joint3', 'fr3_joint4', 'fr3_joint5', 'fr3_joint6', 'fr3_joint7']
yujietang@yujietang-System-Product-Name:~/franka_ros2_w
还有一个代码问题：不要打印 “Execution finished” 太早

你现在即使执行失败，也打印：

这个结果说明 joint names 是匹配的：

/fr3_arm_controller joints =
fr3_joint1 ... fr3_joint7

所以 Goal request rejected 不是因为 joint name 不一致。

现在优先怀疑下面几个原因。

1. 先确认 controller 是 active

运行：

ros2 control list_controllers

你需要看到：

fr3_arm_controller    active
joint_state_broadcaster    active
franka_robot_state_broadcaster    active

如果 fr3_arm_controller 不是 active，MoveIt 可以规划成功，但执行时会被 controller 拒绝。

2. 检查 trajectory action server

运行：

ros2 action list -t | grep FollowJointTrajectory

应该看到：

/fr3_arm_controller/follow_joint_trajectory [control_msgs/action/FollowJointTrajectory]

再查：

ros2 action info /fr3_arm_controller/follow_joint_trajectory

需要看到：

Action servers: 1
Action clients: 1
3. 检查 controller 的 command interface

运行：

ros2 param get /fr3_arm_controller command_interfaces
ros2 param get /fr3_arm_controller state_interfaces

以及：

ros2 control list_hardware_interfaces

重点看 fr3_joint1 到 fr3_joint7 的 command interface 是否被 fr3_arm_controller claim。

如果官方 MoveIt 配置使用的是 effort interface，你可能看到类似：

fr3_joint1/effort [claimed]
...
fr3_joint7/effort [claimed]

这才说明 controller 真正拿到了硬件控制权。

4. 目标 joint position 可能太远，先测试极小运动

你的目标：

[0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.7]

可能离当前状态比较远。先读取当前状态：

ros2 topic echo /joint_states --once

然后把 goal 改成 几乎等于当前值，只让 fr3_joint1 改 0.01 或 0.02 rad。

例如当前如果是：

[0.01, -0.49, 0.02, -2.05, 0.00, 1.55, 0.70]

就测试：

goal_positions = np.array(
    [
        0.03,
        -0.49,
        0.02,
        -2.05,
        0.00,
        1.55,
        0.70,
    ],
    dtype=np.float64,
)

这样可以判断是不是目标太大导致 controller 拒绝。

5. 在代码里打印 trajectory 内容

在 moveit.execute(...) 前加：

traj = plan_result.trajectory.joint_trajectory

print("Trajectory joints:")
print(traj.joint_names)

print("Number of points:")
print(len(traj.points))

if len(traj.points) > 0:
    print("First point:")
    print(traj.points[0])

    print("Last point:")
    print(traj.points[-1])

然后看是否有问题：

joint_names 是否是 fr3_joint1 ... fr3_joint7
points 是否为空
time_from_start 是否大于 0
positions 数量是否是 7

如果 points 是空的，或者 time_from_start 不正常，controller 会直接 reject goal。

当前结论

你现在已经确认：

joint names 匹配
MoveIt planning 成功
trajectory 被发送到 fr3_arm_controller
controller 拒绝 goal

所以问题集中在：

controller 是否 active
hardware interface 是否 claimed
trajectory 内容是否有效
目标位置是否太远/不安全

下一步最关键的是跑这三个：

ros2 control list_controllers
ros2 control list_hardware_interfaces
ros2 action info /fr3_arm_controller/follow_joint_trajectory


ujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 control list_controllers
fr3_arm_controller             joint_trajectory_controller/JointTrajectoryController       active
joint_state_broadcaster        joint_state_broadcaster/JointStateBroadcaster               active
franka_robot_state_broadcaster franka_robot_state_broadcaster/FrankaRobotStateBroadcaster  active
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 action list | grep FollowJointTrajectory
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 action list -t | grep FollowJointTrajectory
/fr3_arm_controller/follow_joint_trajectory [control_msgs/action/FollowJointTrajectory]
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 action info /fr3_arm_controller/follow_joint_trajectory
Action: /fr3_arm_controller/follow_joint_trajectory
Action clients: 1
    /moveit_simple_controller_manager
Action servers: 1
    /fr3_arm_controller
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ 
ros2 param get /fr3_arm_controller command_interfaces
ros2 param get /fr3_arm_controller state_interfaces
String values are: ['effort']
String values are: ['position', 'velocity']
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 control list_hardware_interfaces
[INFO] [1784580839.568409982] [_ros2cli_261859]: waiting for service /controller_manager/list_hardware_interfaces to become available...
command interfaces
	0/cartesian_pose_command [available] [unclaimed]
	1/cartesian_pose_command [available] [unclaimed]
	10/cartesian_pose_command [available] [unclaimed]
	11/cartesian_pose_command [available] [unclaimed]
	12/cartesian_pose_command [available] [unclaimed]
	13/cartesian_pose_command [available] [unclaimed]
	14/cartesian_pose_command [available] [unclaimed]
	15/cartesian_pose_command [available] [unclaimed]
	2/cartesian_pose_command [available] [unclaimed]
	3/cartesian_pose_command [available] [unclaimed]
	4/cartesian_pose_command [available] [unclaimed]
	5/cartesian_pose_command [available] [unclaimed]
	6/cartesian_pose_command [available] [unclaimed]
	7/cartesian_pose_command [available] [unclaimed]
	8/cartesian_pose_command [available] [unclaimed]
	9/cartesian_pose_command [available] [unclaimed]
	fr3_joint1/effort [available] [claimed]
	fr3_joint1/position [available] [unclaimed]
	fr3_joint1/velocity [available] [unclaimed]
	fr3_joint2/effort [available] [claimed]
	fr3_joint2/position [available] [unclaimed]
	fr3_joint2/velocity [available] [unclaimed]
	fr3_joint3/effort [available] [claimed]
	fr3_joint3/position [available] [unclaimed]
	fr3_joint3/velocity [available] [unclaimed]
	fr3_joint4/effort [available] [claimed]
	fr3_joint4/position [available] [unclaimed]
	fr3_joint4/velocity [available] [unclaimed]
	fr3_joint5/effort [available] [claimed]
	fr3_joint5/position [available] [unclaimed]
	fr3_joint5/velocity [available] [unclaimed]
	fr3_joint6/effort [available] [claimed]
	fr3_joint6/position [available] [unclaimed]
	fr3_joint6/velocity [available] [unclaimed]
	fr3_joint7/effort [available] [claimed]
	fr3_joint7/position [available] [unclaimed]
	fr3_joint7/velocity [available] [unclaimed]
	joint_3_position/elbow_command [available] [unclaimed]
	joint_4_sign/elbow_command [available] [unclaimed]
	vx/cartesian_velocity [available] [unclaimed]
	vy/cartesian_velocity [available] [unclaimed]
	vz/cartesian_velocity [available] [unclaimed]
	wx/cartesian_velocity [available] [unclaimed]
	wy/cartesian_velocity [available] [unclaimed]
	wz/cartesian_velocity [available] [unclaimed]
state interfaces
	0/cartesian_pose_state
	1/cartesian_pose_state
	10/cartesian_pose_state
	11/cartesian_pose_state
	12/cartesian_pose_state
	13/cartesian_pose_state
	14/cartesian_pose_state
	15/cartesian_pose_state
	2/cartesian_pose_state
	3/cartesian_pose_state
	4/cartesian_pose_state
	5/cartesian_pose_state
	6/cartesian_pose_state
	7/cartesian_pose_state
	8/cartesian_pose_state
	9/cartesian_pose_state
	fr3/robot_model
	fr3/robot_state
	fr3/robot_time
	fr3_joint1/effort
	fr3_joint1/position
	fr3_joint1/velocity
	fr3_joint2/effort
	fr3_joint2/position
	fr3_joint2/velocity
	fr3_joint3/effort
	fr3_joint3/position
	fr3_joint3/velocity
	fr3_joint4/effort
	fr3_joint4/position
	fr3_joint4/velocity
	fr3_joint5/effort
	fr3_joint5/position
	fr3_joint5/velocity
	fr3_joint6/effort
	fr3_joint6/position
	fr3_joint6/velocity
	fr3_joint7/effort
	fr3_joint7/position
	fr3_joint7/velocity
	joint_3_position/elbow_state
	joint_4_sign/elbow_state
yujietang@yujietang-System-Product-Name:~/franka_ros2_ws$ ros2 topic echo /joint_states --once
header:
  stamp:
    sec: 1784580856
    nanosec: 456622518
  frame_id: ''
name:
- fr3_joint1
- fr3_joint2
- fr3_joint3
- fr3_joint4
- fr3_joint5
- fr3_joint6
- fr3_joint7
- fr3_finger_joint1
- fr3_finger_joint2
position:
- -0.1451645791530609
- -0.11397621780633926
- 0.3398693799972534
- -1.5122379064559937
- -0.049642473459243774
- 1.4341906309127808
- -2.3022968769073486
- 0.0
- 0.0
velocity:
- 0.0008992538787424564
- -0.0008934641373343766
- -0.0013580952072516084
- -0.0006372042698785663
- 0.0003246653650421649
- 0.0005019662203267217
- -0.00019932891882490367
- 0.0
- 0.0
effort:
- 1.0503417253494263
- -24.101978302001953
- 0.038999710232019424
- 22.121191024780273
- 0.9111942648887634
- 2.441458225250244
- 0.02026766538619995
- 0.0
- 0.0
---


一个直接 action 测试，排除 MoveIt 问题

这个测试非常关键。它可以判断问题是：

MoveIt trajectory 问题

还是：

controller 本身拒绝所有 goal


ros2 action send_goal /fr3_arm_controller/follow_joint_trajectory \
control_msgs/action/FollowJointTrajectory \
"{trajectory: {joint_names: ['fr3_joint1', 'fr3_joint2', 'fr3_joint3', 'fr3_joint4', 'fr3_joint5', 'fr3_joint6', 'fr3_joint7'], points: [{positions: [-0.125, -0.114, 0.340, -1.512, -0.050, 1.434, -2.302], velocities: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], time_from_start: {sec: 5, nanosec: 0}}]}}"


Goal accepted with ID: 1ea98f31fb824b66aa14a0a66a5779b4

Result:
    error_code: 0
error_string: Goal successfully reached!

Goal finished with status: SUCCEEDED


_manager]: Starting trajectory execution ...
[pick_place-1] [INFO] [1784581865.223701328] [moveit_3222647999.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784581865.223731513] [moveit_3222647999.moveit.plugins.simple_controller_manager]: Returned 2 controllers in list
[pick_place-1] [INFO] [1784581865.223916218] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: sending trajectory to fr3_arm_controller
[pick_place-1] [INFO] [1784581865.224456994] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: fr3_arm_controller started execution
[pick_place-1] [WARN] [1784581865.224475534] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: Goal request rejected
[pick_place-1] [ERROR] [1784581865.224460506] [moveit.simple_controller_manager.follow_joint_trajectory_controller_handle]: Goal was rejected by server
[pick_place-1] [ERROR] [1784581865.224511704] [moveit_3222647999.moveit.ros.trajectory_execution_manager]: Failed to send trajectory part 1 of 1 to controller fr3_arm_controller
[pick_place-1] [INFO] [1784581865.224528917] [moveit_3222647999.moveit.ros.trajectory_execution_manager]: Completed trajectory execution with status ABORTED ...
[pick_place-1] Planning...
[pick_place-1] Planning succeeded.
[pick_place-1] Execution finished.
[INFO] [pick_place-1]: process has fi





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

    ompl_yaml = load_yaml(
        "franka_fr3_moveit_config",
        "config/ompl_planning.yaml",
    )

    ompl = {
        "planning_plugins": [
            "ompl_interface/OMPLPlanner",
        ]
    }
    ompl.update(ompl_yaml)

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
        "plan_request_params": {
            "planning_pipeline": "ompl",
            "planner_id": "RRTConnectkConfigDefault",
            "planning_time": 5.0,
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



把你现在的 OMPL 部分：

ompl_yaml = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)

ompl = {
    "planning_plugins": [
        "ompl_interface/OMPLPlanner",
    ]
}
ompl.update(ompl_yaml)

改成：

ompl_yaml = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)

ompl = {}
ompl.update(ompl_yaml)

ompl.update({
    "planning_plugins": [
        "ompl_interface/OMPLPlanner",
    ],

    "request_adapters": (
        "default_planning_request_adapters/ResolveConstraintFrames "
        "default_planning_request_adapters/ValidateWorkspaceBounds "
        "default_planning_request_adapters/CheckStartStateBounds "
        "default_planning_request_adapters/CheckStartStateCollision"
    ),

    "response_adapters": (
        "default_planning_response_adapters/AddTimeOptimalParameterization "
        "default_planning_response_adapters/ValidateSolution "
        "default_planning_response_adapters/DisplayMotionPath"
    ),

    "start_state_max_bounds_error": 0.1,
})

重点是这个：

"response_adapters": (
    "default_planning_response_adapters/AddTimeOptimalParameterization "
    "default_planning_response_adapters/ValidateSolution "
    "default_planning_response_adapters/DisplayMotionPath"
)

AddTimeOptimalParameterization 会给 trajectory 添加合理的时间参数。否则 OMPL 可能只给出几何路径，controller 执行时就可能 reject。


还要补充 plan_request_params

你现在日志有：

Parameter 'plan_request_params.max_velocity_scaling_factor' not found
Parameter 'plan_request_params.max_acceleration_scaling_factor' not found


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

    "plan_request_params": {
        "planning_pipeline": "ompl",
        "planner_id": "RRTConnectkConfigDefault",
        "planning_time": 5.0,
        "max_velocity_scaling_factor": 0.05,
        "max_acceleration_scaling_factor": 0.05,
    },

    "ompl": ompl,
}

最后你传给 MoveIt 的还是：

"ompl": ompl,

而 ompl 里面没有这些插件配置。

如果你的目的是把 YAML 和这些参数合并，应该这样：

ompl = load_yaml(
    "franka_fr3_moveit_config",
    "config/ompl_planning.yaml",
)

ompl.update({
    "planning_plugins": [
        "ompl_interface/OMPLPlanner",
    ],
    "request_adapters": [
        "default_planning_request_adapters/ResolveConstraintFrames",
        "default_planning_request_adapters/ValidateWorkspaceBounds",
        "default_planning_request_adapters/CheckStartStateBounds",
        "default_planning_request_adapters/CheckStartStateCollision",
    ],
    "response_adapters": [
        "default_planning_response_adapters/AddTimeOptimalParameterization",
        "default_planning_response_adapters/ValidateSolution",
        "default_planning_response_adapters/DisplayMotionPath",
    ],
    "start_state_max_bounds_error": 0.1,
})

这样 moveit_config 中：

"ompl": ompl,

就会同时包含：

ompl_planning.yaml 的所有规划器配置
planning_plugins
request_adapters
response_adapters
start_state_max_bounds_error

[pick_place-1]              ^^^^^^^^^
[pick_place-1] RuntimeError: Planning plugin name is empty or not defined in namespace 'ompl'. Please choose one of the available plugins: chomp_interface/CHOMPPlanner, ompl_interface/OMPLPlanner, pilz_industrial_motion_planner/CommandPlanner, stomp_moveit/StompPlanner
[ERROR] [pick_place-1]: process has died [pid 302967, exit code 1, cmd '/home/yujietang/franka_ros2_ws/install/fr3_moveit_python/lib/fr3_moveit_python/pick_place --ros-args -r __node:=fr3_pick_place --params-file /tmp/launch_params_xk_e5s15 --params-file /tmp/launch_params_k9f5fi1k --params-file /tmp/launch_params_bge8w9x2 --params-file /tmp/launch_params_45722bpo --params-file /tmp/launch_params_5a6f14d3 --params-file /tmp/launch_params_lp3hfgq4 --params-file /tmp/launch_params_jjaydkym'].

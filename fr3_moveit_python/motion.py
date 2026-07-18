import time

from geometry_msgs.msg import PoseStamped

from moveit.planning import MoveItPy

from rclpy.logging import get_logger

from scipy.spatial.transform import Rotation


PLANNING_GROUP = "fr3_arm"

BASE_FRAME = "fr3_link0"

EE_LINK = "fr3_hand_tcp"


import time

from geometry_msgs.msg import PoseStamped

from moveit.planning import MoveItPy

from rclpy.logging import get_logger

from scipy.spatial.transform import Rotation



PLANNING_GROUP = "fr3_arm"

BASE_FRAME = "fr3_link0"

EE_LINK = "fr3_hand_tcp"



class MotionController:


    def __init__(self):

        self.logger = get_logger(
            "motion_controller"
        )


        self.moveit = MoveItPy(
            node_name="fr3_motion_controller"
        )


        self.arm = self.moveit.get_planning_component(
            PLANNING_GROUP
        )


        self.logger.info(
            "Motion controller initialized"
        )



    def move_cartesian(
        self,
        dx=0.0,
        dy=0.0,
        dz=0.0,
        execute=True
    ):


        self.arm.set_start_state_to_current_state()



        scene_monitor = (
            self.moveit
            .get_planning_scene_monitor()
        )


        with scene_monitor.read_only() as scene:


            current_state = (
                scene.current_state
            )


            transform = (
                current_state
                .get_global_link_transform(
                    EE_LINK
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



        rotation = Rotation.from_matrix(
            transform[:3,:3]
        )


        quaternion = rotation.as_quat()



        target_pose = PoseStamped()


        target_pose.header.frame_id = (
            BASE_FRAME
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



        # keep current orientation

        target_pose.pose.orientation.x = (
            quaternion[0]
        )

        target_pose.pose.orientation.y = (
            quaternion[1]
        )

        target_pose.pose.orientation.z = (
            quaternion[2]
        )

        target_pose.pose.orientation.w = (
            quaternion[3]
        )



        self.arm.set_goal_state(
            pose_stamped_msg=target_pose,
            pose_link=EE_LINK
        )



        self.logger.info(
            "Planning Cartesian motion..."
        )


        plan = self.arm.plan()



        if not plan:

            self.logger.error(
                "Planning failed"
            )

            return False



        if not execute:

            return True



        # avoid MoveIt controller discovery issue

        time.sleep(5)



        result = self.moveit.execute(
            plan.trajectory,
            controllers=[
                "fr3_arm_controller"
            ]
        )


        self.logger.info(
            f"Motion result: {result}"
        )


        return True



    # -------------------------
    # high level functions
    # -------------------------


    def move_down(
        self,
        distance
    ):

        return self.move_cartesian(
            dz=-distance
        )



    def move_up(
        self,
        distance
    ):

        return self.move_cartesian(
            dz=distance
        )



    def move_forward(
        self,
        distance
    ):

        return self.move_cartesian(
            dx=distance
        )



    def move_backward(
        self,
        distance
    ):

        return self.move_cartesian(
            dx=-distance
        )



    def move_left(
        self,
        distance
    ):

        return self.move_cartesian(
            dy=distance
        )



    def move_right(
        self,
        distance
    ):

        return self.move_cartesian(
            dy=-distance
        )

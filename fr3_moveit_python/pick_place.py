import rclpy

from fr3_moveit_python.motion import MotionController

from fr3_moveit_python.gripper_control import GripperController



def main():

    rclpy.init()


    motion = MotionController()

    gripper = GripperController()



    # 1. move above object

    motion.move_down(
        0.10
    )



    # 2. close gripper

    gripper.close_gripper()



    # 3. lift object

    motion.move_up(
        0.10
    )



    # 4. move to place position

    motion.move_forward(
        0.30
    )



    # 5. release

    gripper.open_gripper()



    rclpy.shutdown()



if __name__ == "__main__":

    main()

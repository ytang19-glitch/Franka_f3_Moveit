
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from franka_msgs.action import Move


class GripperController(Node):

    def __init__(self):
        super().__init__("gripper_controller")

        self.client = ActionClient(
            self,
            Move,
            "/franka_gripper/move",
        )

        self.get_logger().info(
            "Waiting for Franka gripper server..."
        )

        self.client.wait_for_server()

        self.get_logger().info(
            "Connected to Franka gripper."
        )


    def feedback_callback(self, feedback_msg):

        feedback = feedback_msg.feedback

        self.get_logger().info(
            f"Current width: {feedback.current_width:.3f} m"
        )


    def move(self, width, speed):

        goal = Move.Goal()

        goal.width = width
        goal.speed = speed

        self.get_logger().info(
            f"Sending gripper goal: width={width:.3f} m, speed={speed:.3f} m/s"
        )


        future = self.client.send_goal_async( 
            goal,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(
            self,
            future
        )


        goal_handle = future.result()


        if not goal_handle.accepted:

            self.get_logger().error(
                "Gripper goal rejected"
            )

            return False


        self.get_logger().info(
            "Gripper goal accepted"
        )


        result_future = goal_handle.get_result_async()


        rclpy.spin_until_future_complete(
            self,
            result_future
        )


        result = result_future.result().result

        if result.success:

            self.get_logger().info(
                "Gripper motion completed successfully."
            )

        else:

            self.get_logger().error(
                result.error
            )


    
        return result.success

     # ===================================
     # Reusable library mode 
     # ===================================

    def open_gripper(self):

        return self.move(
            width=0.08,
            speed=0.05
        )


    def close_gripper(self):

        return self.move(
        width=0.00,
        speed=0.05
        )




# ===================================
# Standalone executable test
# ===================================

#Using for testing the gripper control action server.

def main(): 

    rclpy.init()

    gripper = GripperController()


    # Open gripper
    gripper.open_gripper()


    # Close gripper
    gripper.close_gripper()


    gripper.destroy_node()
    

    rclpy.shutdown()

#AFTER BUILDING THE PACKAGE, RUN THE FOLLOWING COMMAND TO TEST THE GRIPPER CONTROL ACTION SERVER:
#colcon build --packages-select fr3_moveit_python source install/setup.bash

if __name__ == "__main__":
    main()


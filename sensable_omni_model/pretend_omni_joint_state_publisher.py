#
# Simple script to emulate an Omni trajectory.  It can be used if you
# don't have access to a device (Sensable Omni, 3DS Touch...).
#
# This script assumes the device follows the CRTK naming convention,
# i.e. the joint state is published on the topic `measured_js`.  The
# launch file in this repository uses the ROS 2 node
# `joint_state_publisher` to rename the joint state to the default ROS
# value `joint_states` expected by the `robot_state_publisher`.  The
# node `joint_state_publisher` also defines the rate used to publish
# to the `robot_state_publisher`
#

import rclpy, sys
from rclpy.node import Node
from rclpy.qos import QoSProfile
from sensor_msgs.msg import JointState
from math import cos, radians

class StatePublisher(Node):

    def __init__(self, argv):
        rclpy.init(args = argv)
        super().__init__('state_publisher')

        qos_profile = QoSProfile(depth=10)
        self.joint_pub = self.create_publisher(JointState, 'measured_js', qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info("{0} started".format(self.nodeName))

        loop_rate = self.create_rate(1000)

        # message declarations
        joint_state = JointState()
        # make sure names match URDF
        joint_state.name = ['waist', 'shoulder', 'elbow', 'yaw', 'pitch', 'roll']
        joint_state.position = [0.0, 0.0, 0.0, 0.0, 0.1, 0.0]

        try:
            counter = 0.0
            while rclpy.ok():
                rclpy.spin_once(self)

                # update joint_state
                now = self.get_clock().now()
                joint_state.header.stamp = now.to_msg()

                counter += 0.001
                position = radians(20.0) * cos(counter)
                for i in range(6):
                    joint_state.position[i] = position

                # so arm doesn't hit itself
                joint_state.position[1] += radians(20)
                joint_state.position[2] += radians(20)
                joint_state.position[4] += radians(50)

                # send the joint state and transform
                self.joint_pub.publish(joint_state)

                # This will adjust as needed per iteration
                loop_rate.sleep()

        except KeyboardInterrupt:
            pass

def main():
    node = StatePublisher(sys.argv)

if __name__ == '__main__':
    main()

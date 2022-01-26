#!/usr/bin/env python2
# Receive user input for the objective position and attitude (later on will be received from a subscriber to pose of aruco pkg)
import rospy
from std_msgs.msg import String


def input_objective_pose():
    position = input("Enter desired position (x, y, z): ")
    attitude = input("Enter desired attitude (alpha, beta, gamma): ")
    return position, attitude


if __name__ == '__main__':
    try:
        position, attitude = input_objective_pose()
    except rospy.ROSInterruptException:
        pass
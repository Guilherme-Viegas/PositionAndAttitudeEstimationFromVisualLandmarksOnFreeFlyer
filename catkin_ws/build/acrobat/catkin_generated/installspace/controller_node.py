#!/usr/bin/env python2
import rospy
from std_msgs.msg import Float64MultiArray, String
import numpy as np

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    if len(data.data) == 0:
        print "No new localization data!"
        return

def listener:
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber("chatter", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()


if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
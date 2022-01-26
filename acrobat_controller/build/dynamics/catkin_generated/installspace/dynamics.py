#!/usr/bin/env python2
# Receive intended force and torque and compute the pwm values for the propellers
# Computes the necessary rotations per second on each of ACROBAT's blades to reach that position and attitude
import rospy
from std_msgs.msg import String
import numpy as np

a1 = np.array((-0.02219657522, 0.01859006027, 0.01279597757, -0.01859006027, -0.03499255279, 0.01859006027)).T
a2 = np.array((0.00023789747, 0.01859006027, 0.01279597757, 0.0191789862, 0.0004043464, -0.00083633887)).T
a3 = np.array((0.01079543949, 0.9998789634, 0.01079611706, 0.9979681394, -0.00933602561, -0.1332524502)).T
a4 = np.array((0.7653778177, 0.01913843278, 0.9996875163, -0.03321824755, -0.0134563338, 0.02569007069)).T
a5 = np.array((-0.001067244345, 0.01896885746, -0.05617408802, 0.05638539532, -0.00126732433, -0.00128318081)).T
a6 = np.array((.9982558165, 0.05796384873, 0.9983184715, -0.01714869459, 0.07147917464, 0.01299743049)).T
A = np.column_stack((a1, a2, a3, a4, a5, a6))
A_inverse = np.linalg.inv(A)

# For now it returns the rotations per second (q) instead of pwm -> TODO: Find how to make this conversion from q to pwm
def compute_pwm_control(force, torque):
    input_vect = np.concatenate((force, torque), axis = 0)
    q = np.dot(A_inverse, input_vect.T)
    return q

if __name__ == '__main__':
    force = np.array((1, 2, 3))
    torque = np.array((2, 2, 2))
    try:
        print(compute_pwm_control(force, torque))
    except rospy.ROSInterruptException:
        pass
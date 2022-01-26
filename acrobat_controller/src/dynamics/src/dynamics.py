#!/usr/bin/env python
# Receive user input for the objective position and attitude (later on will be received from a subscriber to pose of aruco pkg)
# Computes the necessary rotations per second on each of ACROBAT's blades to reach that position and attitude
# Based on 2 papers:
#   - "A multi-objective optimization approach to the design of a free-flyer space robot for in-orbit manufacturing and assembly" by Vale, Rocha, Leite and Ventura
#   - "Towards an autonomous free-flying robot fleet for intra-vehicular trasnportation of loads in unmanned space stations" by Ventura, Roque and Ekal
import rospy
from std_msgs.msg import String
import numpy as np

def get_rotation_matrix_from_euler_angles(euler_angles):
    x = euler_angles[0]
    y = euler_angles[1]
    z = euler_angles[2]
    return np.array([
            [np.cos(y)*np.cos(x) ,  -np.cos(z)*np.sin(x)+np.sin(z)*np.cos(x)*np.sin(y) , np.sin(z)*np.sin(x)+np.cos(z)*np.sin(y)*np.cos(x)],    #TODO(): Double check if it's correct
            [np.cos(y)*np.sin(x) , np.cos(z)*np.cos(x)+np.sin(z)*np.sin(y)*np.sin(x) , -np.sin(z)*np.cos(x)+np.cos(z)*np.sin(y)*np.sin(x)],
            [-np.sin(y) , np.sin(z)*np.cos(y) , np.cos(z)*np.cos(y)]
        ])

FREE_FLYER_MASS = 9.7 # Kg, Random testing value... Still have to search for the exact mass of the ACROBAT
FREE_FLYER_MOMENT_OF_INERTIA = np.array((7, 7, 10)) # Kg.m^2 ... Still have to search for exact moment of inertia vector of the ACROBAT

# Controller Gains TODO: Need to be calibrated
K_x = 0.2 # Controller Proportional Gain (Translational part)
K_v = 0.1 # Controller Derivative Gain (Translational part)
K_r = 0.2 # Controller Porportional Gains (Rotational part)
K_w = 0.1 # Controller Derivative Gain (Rotational part)

a1 = np.array((-0.02219657522, 0.01859006027, 0.01279597757, -0.01859006027, -0.03499255279, 0.01859006027)).T
a2 = np.array((0.00023789747, 0.01859006027, 0.01279597757, 0.0191789862, 0.0004043464, -0.00083633887)).T
a3 = np.array((0.01079543949, 0.9998789634, 0.01079611706, 0.9979681394, -0.00933602561, -0.1332524502)).T
a4 = np.array((0.7653778177, 0.01913843278, 0.9996875163, -0.03321824755, -0.0134563338, 0.02569007069)).T
a5 = np.array((-0.001067244345, 0.01896885746, -0.05617408802, 0.05638539532, -0.00126732433, -0.00128318081)).T
a6 = np.array((.9982558165, 0.05796384873, 0.9983184715, -0.01714869459, 0.07147917464, 0.01299743049)).T
A = np.column_stack((a1, a2, a3, a4, a5, a6))
A_inverse = np.linalg.inv(A)

DESIRED_POSITION = np.array((0.1, 0, 0)) # To be 10cm in front of the AR tag
DESIRED_LINEAR_VELOCITY = np.array((0, 0, 0)) # TODO: To be confirmed whit professor on how to know its value
DESIRED_ATTITUDE = np.array((0, 0, 0)) # To be aligned with the AR tag TODO: This might have be confirmed... don't known if this will make the front of the robot face backwards
DESIRED_ROTATION_MATRIX = get_rotation_matrix_from_euler_angles(DESIRED_ATTITUDE)
DESIRED_ANGULAR_VELOCITY = np.array((0, 0, 0)) # TODO: To be confirmed whit professor on how to know its value
DESIRED_ANGULAR_ACCELERATION = np.array((0, 0, 0))

# Some testing values -> Later, these will be received by the Aruco Pkg
current_position = np.array((1, 2, 3))
current_attitude = np.array((np.pi/2, np.pi/4, np.pi/2)) # Euler angles as x, y, z

def input_objective_pose():
    position = input("Enter desired position (x, y, z): ")
    attitude = input("Enter desired attitude (x, y, z) euler angles: ")
    return position, attitude

def compute_force_and_torque(position, attitude):
    # ************* Testing values, will be erased later *************
    current_linear_velocity = np.array((0, 0, 0))
    current_angular_velocity = np.array((0, 0, 0))
    # ****************************************************************

    attitude_rotation_matrix = get_rotation_matrix_from_euler_angles(attitude)

    # Translational Part
    error_x = current_position - DESIRED_POSITION
    error_v = current_linear_velocity - DESIRED_LINEAR_VELOCITY # current_velocity has to be somehow received by the ACROBAT sensors (subscribe to topic) 
    acceleration = -K_x * error_x - K_v * error_v # K_x and K_v are the proportionate and derivative gains (constants) and error_x and error_v the position and velocity errors
    force = np.dot( (FREE_FLYER_MASS * attitude_rotation_matrix), acceleration)

    # Rotational Part
    inverse_of_S_w = get_inverse_S_w( (np.dot(DESIRED_ROTATION_MATRIX.T, attitude_rotation_matrix) - np.dot(attitude_rotation_matrix.T, DESIRED_ROTATION_MATRIX)) )
    error_r = ( 1 / (2*np.sqrt(1 + np.trace( np.dot(DESIRED_ROTATION_MATRIX.T, attitude_rotation_matrix ))) )) * inverse_of_S_w
    error_w = current_angular_velocity - np.dot(np.dot( attitude_rotation_matrix.T, DESIRED_ROTATION_MATRIX), DESIRED_ANGULAR_VELOCITY)
    inverse_of_S_w = get_inverse_S_w( np.dot( np.dot(attitude_rotation_matrix.T, DESIRED_ROTATION_MATRIX), np.asmatrix(DESIRED_ANGULAR_VELOCITY).T ) )
    torque = -K_r * error_r - K_w * error_w + np.dot(np.dot(np.dot(np.dot(inverse_of_S_w, FREE_FLYER_MOMENT_OF_INERTIA), attitude_rotation_matrix.T), DESIRED_ROTATION_MATRIX), DESIRED_ANGULAR_VELOCITY) + np.dot(np.dot(np.dot(FREE_FLYER_MOMENT_OF_INERTIA, attitude_rotation_matrix.T), DESIRED_ROTATION_MATRIX), DESIRED_ANGULAR_ACCELERATION)

    return force, torque

# Matrix operations that recovers angular velocity vector from a skew-symmetrix matrix (Check paper)
# S(w) = [0, -w_z, w_y; w_z, 0, -w_x; -w_y, w_x, 0]
def get_inverse_S_w(matrix):
    print(matrix)
    angular_velocity = (matrix[2][1], matrix[0][2], matrix[1][0])
    return np.array(angular_velocity)

# For now it returns the rotations per second (q) instead of pwm -> TODO: Find how to make this conversion from q to pwm
def compute_pwm_control(force, torque):
    input_vect = np.concatenate((force, torque), axis = 0)
    q = np.dot(A_inverse, input_vect)
    return np.array(q)

if __name__ == '__main__':
    
    try:
        #Compute Force and Torque vectors from desired state vector
        force, torque = compute_force_and_torque(current_position, current_attitude)
        #Compute pwm values from intended Force and Torque
        print(compute_pwm_control(force, torque))
    except rospy.ROSInterruptException:
        pass
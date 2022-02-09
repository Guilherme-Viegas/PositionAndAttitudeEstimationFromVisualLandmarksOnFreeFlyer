

from __future__ import print_function # Python 2/3 compatibility
import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library
import aruco_tracker as my_aruco
#import motor_control as motor_control # Can only be run on an RPi due to the need for the RPi.GPIO library
import controller as controller

def main():
    #motor_control.setup_motors()

    # Check that we have a valid ArUco marker
    my_aruco.check_aruco_validity()
        
    # Load the ArUco dictionary
    this_aruco_dictionary, this_aruco_parameters = my_aruco.load_aruco_dictionary()

    # Load camera calibration parameters
    npzfile = np.load('cali_values.npz')
    camera_matrix = npzfile['mtx']
    distortion = npzfile['dist']
    ret = npzfile['ret']
    rvecs = npzfile['rvecs']
    tvecs = npzfile['tvecs']

    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    while(True):
        # Capture frame-by-frame
        # This method returns True/False as well
        # as the video frame.
        ret, frame = cap.read()
        img = cv2.undistort(frame, camera_matrix, distortion)

        # Detect ArUco markers in the video frame
        (corners, ids, rejected) = cv2.aruco.detectMarkers(img, this_aruco_dictionary, parameters=this_aruco_parameters)
        rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, my_aruco.ARUCO_SIZE, camera_matrix, distortion)

        # Check that at least one ArUco marker was detected
        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, my_aruco.ARUCO_SIZE, camera_matrix, distortion)

            # rvecs is a compact Rodrigues rotation vector so I need to convert it to euler angles form
            rotation_matrix, _ = cv2.Rodrigues(rvecs[0][0])
            rotation_matrix = np.asmatrix(rotation_matrix)
            current_attitude = controller.get_euler_anles_from_rotation_matrix(rotation_matrix)

            ##for i in range(len(ids)):
                ##img = cv2.aruco.drawAxis(img, camera_matrix, distortion, rvecs[i], tvecs[i],  0.05)
        # Display the resulting frame
        ##cv2.imshow('img',img)

            # Computing control values of the feedback chain (Only if one aruco marker was found)
            #TODO: I have to confirm that tvecs and rvecs is the position and attitude of the acrobat in relation to aruco marker (I believe it is the opposite now)
            force, torque = controller.compute_force_and_torque(tvecs[0][0], current_attitude)
            pwm_control = controller.compute_pwm_control(force, torque)
            print(force)
            print(torque)
            print("-------------")
            print(pwm_control)
            print("*******************")
            #motor_control.write_pwm(pwm_control)

        # If "q" is pressed on the keyboard, 
        # exit this loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close down the video stream
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print(__doc__)
    main()
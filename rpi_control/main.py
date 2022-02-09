#!/usr/bin/env python

from __future__ import print_function # Python 2/3 compatibility
import cv2 # Import the OpenCV library
import numpy as np # Import Numpy library

desired_aruco_dictionary = "DICT_5X5_50"
aruco_size = 0.05

# The different ArUco dictionaries built into the OpenCV library. 
ARUCO_DICT = {
  "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
  "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
  "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
  "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
  "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
  "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
  "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
  "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
  "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
  "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
  "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
  "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
  "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
  "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
  "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
  "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
  "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL
}

def main():
    # Check that we have a valid ArUco marker
    if ARUCO_DICT.get(desired_aruco_dictionary, None) is None:
        print("[INFO] ArUCo tag of '{}' is not supported".format(args["type"]))
        sys.exit(0)
        
    # Load the ArUco dictionary
    print("[INFO] detecting '{}' markers...".format(desired_aruco_dictionary))
    this_aruco_dictionary = cv2.aruco.Dictionary_get(ARUCO_DICT[desired_aruco_dictionary])
    this_aruco_parameters = cv2.aruco.DetectorParameters_create()

    # Load camera calibration
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
        #img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Detect ArUco markers in the video frame
        (corners, ids, rejected) = cv2.aruco.detectMarkers(img, this_aruco_dictionary, parameters=this_aruco_parameters)
        rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, aruco_size, camera_matrix, distortion)

        # Check that at least one ArUco marker was detected
        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, aruco_size, camera_matrix, distortion)
            for i in range(len(ids)):
                img = cv2.aruco.drawAxis(img, camera_matrix, distortion, rvecs[i], tvecs[i],  0.05)
        # Display the resulting frame
        cv2.imshow('img',img)

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
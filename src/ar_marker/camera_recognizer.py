import cv2
from cv2 import aruco

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)


def check_camera_connection():
    """
    Check the connection between the camera numbers and the computer.

    """
    true_camera_is = []

    # check the camera number from 0 to 9
    for camera_number in range(0, 10):
        cap = cv2.VideoCapture(camera_number)
        ret, frame = cap.read()

        if ret is True:
            true_camera_is.append(camera_number)
            print("port number", camera_number, "Find!")

        else:
            print("port number", camera_number, "None")
    print("Connected camera", len(true_camera_is))


def capture_camera():
    capture = cv2.VideoCapture(1)
    while cv2.waitKey(1) & 0xFF != ord("q"):
        _, frame = capture.read()

        corners, ids, _ = detector.detectMarkers(frame)
        ar_image = aruco.drawDetectedMarkers(frame, corners, ids)

        cv2.imshow("frame", ar_image)

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # check_camera_connection()
    capture_camera()

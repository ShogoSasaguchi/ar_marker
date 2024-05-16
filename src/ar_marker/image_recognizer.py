import argparse
import os

import cv2
from cv2 import aruco


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", help="input image file", required=True)
    parser.add_argument("--output_dir_path", help="output image file", required=True)
    args = parser.parse_args()

    # get dicionary and get parameters
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(dictionary, parameters)

    # read from image
    input_path = args.input_path
    input_img = cv2.imread(input_path)
    # output_dir_path にinput_pathのファイル名に`_output`を追加したファイル名を指定
    output_path = os.path.join(args.output_dir_path, os.path.basename(input_path).replace(".", "_output."))

    # detect and draw marker's information
    corners, ids, _ = detector.detectMarkers(input_img)
    ar_image = aruco.drawDetectedMarkers(input_img, corners, ids)

    cv2.imwrite(output_path, ar_image)


if __name__ == "__main__":
    main()

import argparse
import os

import cv2
import numpy as np
from cv2 import aruco


def generate_marker(output_dir_path, marker_id):
    # Size and offset value
    SIZE = 150
    OFFSET = 0
    X_OFFSET = Y_OFFSET = int(OFFSET) // 2

    # get dictionary and generate image
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    ar_img = aruco.generateImageMarker(dictionary, marker_id, SIZE)

    # make white image
    img = np.zeros((SIZE + OFFSET, SIZE + OFFSET), dtype=np.uint8)
    img += 255

    # overlap image
    img[Y_OFFSET : Y_OFFSET + ar_img.shape[0], X_OFFSET : X_OFFSET + ar_img.shape[1]] = ar_img

    # save image
    output_path = os.path.join(output_dir_path, f"marker_{marker_id}.png")
    cv2.imwrite(output_path, img)

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir_path", help="output image file", required=True)
    # parser.add_argument("--marker_id", type=int, default=0, help="marker id", required=True)
    args = parser.parse_args()

    if not os.path.exists(args.output_dir_path):
        os.makedirs(args.output_dir_path)

    for i in range(16):
        generate_marker(args.output_dir_path, i)

    # generate_marker(args.output_dir_path, args.marker_id)

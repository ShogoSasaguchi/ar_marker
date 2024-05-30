import time

import cv2
from cv2 import aruco

from ar_marker.basler_camera import Camera as BaslerCamera

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)


def capture_camera():
    camera = BaslerCamera(model_name="acA2440-20gc", serial_number="24144460", name="camera")
    # 接続が成功すること
    print("接続成功") if camera.connect() else print("接続失敗")
    # ワンショット撮影が成功すること
    image = camera.grab_one()
    print(image)
    del image
    # 連続撮影がスタートできること
    print("連続撮影スタート成功") if camera.start_continuous_grab() else print("連続撮影スタート失敗")

    while cv2.waitKey(1) & 0xFF != ord("q"):
        frame = camera.grab()
        if frame is None:
            continue
        height, width = frame.shape[:2]
        max_height = 1500
        max_width = 800
        # print(frame.shape)
        # break
        scale = min(max_height / height, max_width / width)
        resized_frame = cv2.resize(frame, (int(width * scale), int(height * scale)))

        corners, ids, _ = detector.detectMarkers(resized_frame)
        ar_image = aruco.drawDetectedMarkers(resized_frame, corners, ids)

        cv2.imshow("frame", ar_image)

        # スクリーンショット
        if cv2.waitKey(1) & 0xFF == ord("s"):
            cv2.imwrite(f".\save\screenshot_{time.time()}.png", ar_image)

    cv2.destroyAllWindows()
    # 連続撮影が停止できること
    print("連続撮影停止成功") if camera.stop_continuous_grab() else print("連続撮影停止失敗")
    # 正常にカメラをクローズできること
    print("カメラクローズ成功") if camera.disconnect() else print("カメラクローズ失敗")


if __name__ == "__main__":
    # check_camera_connection()
    capture_camera()

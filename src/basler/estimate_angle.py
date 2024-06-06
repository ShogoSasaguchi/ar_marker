import os
import time

import cv2
import numpy as np
from basler.camera import Camera as BaslerCamera
from cv2 import aruco

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)
# マーカーの実際のサイズ（メートル単位）
MARKER_SIZE = 0.063
SAVE_DIR_PATH = ".\save"


def capture_camera():
    if not os.path.exists(SAVE_DIR_PATH):
        os.makedirs(SAVE_DIR_PATH)
    # カメラキャリブレーションデータの読み込み
    camera_matrix = np.load(
        os.path.join(".", "camera_meta", "camera_matrix.npy"),
    )
    dist_coeffs = np.load(os.path.join(".", "camera_meta", "dist_coeffs.npy"))
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

        if ids is not None:
            rvecs = []
            tvecs = []
            for i in range(len(ids)):
                # マーカーの4隅の3次元座標を準備
                obj_points = np.array(
                    [
                        [-MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
                        [MARKER_SIZE / 2, MARKER_SIZE / 2, 0],
                        [MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                        [-MARKER_SIZE / 2, -MARKER_SIZE / 2, 0],
                    ],
                    dtype=np.float32,
                )

                # 姿勢推定
                _, rvec, tvec = cv2.solvePnP(obj_points, corners[i], camera_matrix, dist_coeffs)
                rvecs.append(rvec)
                tvecs.append(tvec)

            # 回転ベクトルの平均を計算
            rvec_avg = np.mean(rvecs, axis=0)
            tvec_avg = np.mean(tvecs, axis=0)

            # 回転ベクトルをオイラー角に変換
            rmat, _ = cv2.Rodrigues(rvec_avg)
            roll = np.rad2deg(np.arctan2(rmat[2][1], rmat[2][2]))
            pitch = np.rad2deg(-np.arcsin(rmat[2][0]))
            yaw = np.rad2deg(np.arctan2(rmat[1][0], rmat[0][0]))

            # カメラとの距離を計算
            distance = np.sqrt(tvec_avg[0, 0] ** 2 + tvec_avg[1, 0] ** 2 + tvec_avg[2, 0] ** 2)

            # 結果を画面に表示
            cv2.putText(frame, f"Roll: {roll:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Pitch: {pitch:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Yaw: {yaw:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Distance: {distance:.2f}m", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
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

import os

import cv2
import numpy as np
from basler.camera import Camera as BaslerCamera
from cv2 import aruco

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)
# チェスボードの設定
chessboard_size = (7, 7)  # 交点の数（幅, 高さ）
square_size = 0.0008  # チェスボードの正方形の一辺の長さ（メートル単位）


def calibration():
    camera = BaslerCamera(model_name="acA2440-20gc", serial_number="24144460", name="camera")
    # 接続が成功すること
    print("接続成功") if camera.connect() else print("接続失敗")
    # ワンショット撮影が成功すること
    image = camera.grab_one()
    print(image.shape)
    del image
    # 連続撮影がスタートできること
    print("連続撮影スタート成功") if camera.start_continuous_grab() else print("連続撮影スタート失敗")
    img_count = 0
    img_points = []
    obj_points = []
    # 3次元点の準備
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : chessboard_size[0], 0 : chessboard_size[1]].T.reshape(-1, 2) * square_size

    while img_count < 20:
        frame = camera.grab()
        height, width = frame.shape[:2]
        max_height = 1500
        max_width = 800
        scale = min(max_height / height, max_width / width)
        frame = cv2.resize(frame, (int(width * scale), int(height * scale)))
        # frame = cv2.resize(frame, (256, 256))
        print(frame.shape)
        if frame is None:
            continue
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        ret, corners = cv2.findChessboardCorners(gray_frame, chessboard_size, None)
        if ret:
            print(ret)
            img_points.append(corners)
            obj_points.append(objp)
            img_count += 1

            print("Capture image: ", img_count, "/ 20 Done!")

            # 検出したチェスボードを描画
            cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
            if cv2.waitKey(500) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()
    # カメラキャリブレーションの実行
    ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
        obj_points, img_points, gray_frame.shape[::-1], None, None
    )

    # キャリブレーション結果の保存
    np.save(os.path.join(".", "camera_meta", "basler_camera_matrix.npy"), camera_matrix)
    np.save(os.path.join(".", "camera_meta", "basler_dist_coeffs.npy"), dist_coeffs)
    # 連続撮影が停止できること
    print("連続撮影停止成功") if camera.stop_continuous_grab() else print("連続撮影停止失敗")
    # 正常にカメラをクローズできること
    print("カメラクローズ成功") if camera.disconnect() else print("カメラクローズ失敗")


if __name__ == "__main__":
    calibration()

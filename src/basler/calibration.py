import cv2
import numpy as np
from basler.camera import Camera as BaslerCamera
from cv2 import aruco

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(dictionary, parameters)
# チェスボードの設定
chessboard_size = (7, 7)  # 交点の数（幅, 高さ）
square_size = 0.19  # チェスボードの正方形の一辺の長さ（メートル単位）


def calibration():
    camera = BaslerCamera(model_name="acA2440-20gc", serial_number="24144460", name="camera")
    # 接続が成功すること
    print("接続成功") if camera.connect() else print("接続失敗")
    # ワンショット撮影が成功すること
    image = camera.grab_one()
    print(image)
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
        if frame is None:
            continue
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray_frame, chessboard_size, None)

        if ret:
            img_points.append(corners)
            obj_points.append(objp)
            img_count += 1

            print("Capture image: ", img_count, "/ 20 Done!")
            # 検出したチェスボードを描画
            cv2.drawChessboardCorners(frame, chessboard_size, corners, ret)
            cv2.waitKey(500)
        cv2.imshow("img", frame)

    cv2.destroyAllWindows()
    # 連続撮影が停止できること
    print("連続撮影停止成功") if camera.stop_continuous_grab() else print("連続撮影停止失敗")
    # 正常にカメラをクローズできること
    print("カメラクローズ成功") if camera.disconnect() else print("カメラクローズ失敗")


if __name__ == "__main__":
    calibration()

import os

import cv2
import numpy as np

# チェスボードの設定
chessboard_size = (7, 7)  # 交点の数（幅, 高さ）
square_size = 0.19  # チェスボードの正方形の一辺の長さ（メートル単位）


def main():
    # 3次元点の準備
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : chessboard_size[0], 0 : chessboard_size[1]].T.reshape(-1, 2) * square_size

    # 画像点と3次元点の配列
    img_points = []
    obj_points = []

    # カメラからキャリブレーション画像を取得
    cap = cv2.VideoCapture(1)
    img_count = 0

    print("Start capturing images...")
    while img_count < 10:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            img_points.append(corners)
            obj_points.append(objp)
            img_count += 1

            print("Capture image: ", img_count, "/ 10 Done!")
            # 検出したチェスボードを描画
            cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
            cv2.imshow("img", img)
            cv2.waitKey(500)

    cv2.destroyAllWindows()
    cap.release()

    # カメラキャリブレーションの実行
    ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

    # キャリブレーション結果の保存
    np.save(os.path.join(".", "camera_meta", "camera_matrix.npy"), camera_matrix)
    np.save(os.path.join(".", "camera_meta", "dist_coeffs.npy"), dist_coeffs)


if __name__ == "__main__":
    main()

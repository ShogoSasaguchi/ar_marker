import argparse
import datetime
import os

import cv2
import numpy as np
from pupil_apriltags import Detector

SAVE_DIR_PATH = ".\save"
# マーカーの実際のサイズ（メートル単位）
MARKER_SIZE = 0.0645


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--families", type=str, default="tag25h9")
    args = parser.parse_args()

    if not os.path.exists(SAVE_DIR_PATH):
        os.makedirs(SAVE_DIR_PATH)
    # カメラキャリブレーションデータの読み込み
    camera_matrix = np.load(
        os.path.join(".", "camera_meta", "camera_matrix.npy"),
    )
    dist_coeffs = np.load(os.path.join(".", "camera_meta", "dist_coeffs.npy"))

    # AprilTagの検出器を初期化
    detector = Detector(families=args.families)

    # カメラからの入力
    cap = cv2.VideoCapture(0)

    while True:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # マーカーの検出
        detections = detector.detect(gray)

        for detection in detections:
            corners = detection.corners.reshape(-1, 2)

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
            _, rvec, tvec = cv2.solvePnP(obj_points, corners, camera_matrix, dist_coeffs)
            # 回転ベクトルをオイラー角に変換
            rmat, _ = cv2.Rodrigues(rvec)
            roll = np.rad2deg(np.arctan2(rmat[2][1], rmat[2][2]))
            pitch = np.rad2deg(-np.arcsin(rmat[2][0]))
            yaw = np.rad2deg(np.arctan2(rmat[1][0], rmat[0][0]))

            # カメラとの距離を計算
            distance = np.sqrt(tvec[0, 0] ** 2 + tvec[1, 0] ** 2 + tvec[2, 0] ** 2)

            # 結果を画面に表示
            cv2.putText(frame, f"Roll: {roll:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Pitch: {pitch:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Yaw: {yaw:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"Distance: {distance:.2f}m", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 検出されたマーカーを描画
            cv2.drawContours(frame, [np.int32(corners)], -1, (0, 255, 0), 2)

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        # sを押すとスクリーンショットを保存
        if cv2.waitKey(1) & 0xFF == ord("s"):
            print("Save screenshot!")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(SAVE_DIR_PATH, f"screenshot_{timestamp}.jpg")
            cv2.imwrite(screenshot_path, frame)
            print(f"Save screenshot Done! Saved as: {screenshot_path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

import os

import cv2


def crop_movie(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    input_file_list = os.listdir(input_dir)

    for input_file in input_file_list:
        print(f"動画のクロップを開始します: {input_file}")

        input_file_path = os.path.join(input_dir, input_file)
        output_file_path = os.path.join(output_dir, input_file)

        # 動画を読み込む
        cap = cv2.VideoCapture(input_file_path)

        # 元の動画の情報を取得
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # クロップする上下のピクセル数を計算
        crop_pixels = (height - 1080) // 2

        # 出力用のVideoWriterを作成
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_file_path, fourcc, fps, (1920, 1080))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # フレームをクロップ
            cropped_frame = frame[crop_pixels : height - crop_pixels, :]

            # クロップしたフレームを書き込む
            out.write(cropped_frame)

        # リソースを解放
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        print("動画のクロップが完了しました。")


if __name__ == "__main__":
    # 入力と出力のファイル名
    input_dir = "C:/Users/shogo.sasaguchi_hutz/Documents/錦城_医療ゴム/row_data/"
    output_dir = "C:/Users/shogo.sasaguchi_hutz/Documents/錦城_医療ゴム/output/"

    crop_movie(input_dir, output_dir)

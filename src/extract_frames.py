import os
from glob import glob

import ffmpeg


def extract_frames(input_video_path, output_dir, interval):
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 入力動画のストリーム情報を取得
    probe = ffmpeg.probe(input_video_path)
    video_stream = next((stream for stream in probe["streams"] if stream["codec_type"] == "video"), None)

    if video_stream is None:
        print("エラー: 動画ストリームが見つかりません。")
        return

    # フレーム抽出処理
    (
        ffmpeg.input(input_video_path)
        .filter("fps", fps=1 / interval)
        .output(f"{output_dir}/%03d.jpg", start_number=0, video_bitrate="5000k")
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )

    print(f"画像の抽出が完了しました。保存先: {output_dir}")


def multi_extract_frames(input_video_dir, output_dir, interval):
    # 入力動画のパス一覧を取得
    input_video_paths = glob(f"{input_video_dir}/*")

    # 各動画に対してフレーム抽出処理を実行
    for input_video_path in input_video_paths:
        output_dir_path = os.path.join(output_dir, os.path.basename(input_video_path).split(".")[0])
        extract_frames(input_video_path, output_dir_path, interval)


if __name__ == "__main__":
    # 使用例
    input_video = "C:/Users/shogo.sasaguchi_hutz/Documents/錦城_医療ゴム/output/動画1.mov"  # 入力動画ファイルのパス
    output_dir = "C:/Users/shogo.sasaguchi_hutz/Documents/錦城_医療ゴム/extract/movie_001"  # 出力ディレクトリ
    interval = 2  # 画像を切り出す間隔（秒）

    extract_frames(input_video, output_dir, interval)

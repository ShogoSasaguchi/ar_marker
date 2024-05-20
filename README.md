# AR Marker の実験用

## 環境構築

- rye をインストールする。
- ライブラリをインストールする。
  ```
  rye sync
  ```

## マーカー生成

```
python3 src/generator.py --output_dir_path [出力ディレクトリのパス] --marker_id [マーカーのID]
```

## マーカー認識

```
python3 src/recognizer.py --input_path [判定する入力画像のパス] --output_dir_path [判定した画像に結果を上書きした画像の保存先]
```

## カメラでマーカーをとらえる

- まずカメラのキャリブレーションをする必要がある。

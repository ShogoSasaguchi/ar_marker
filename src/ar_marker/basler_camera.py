import traceback

from pypylon import pylon


class Camera(object):
    def __init__(self, model_name: str, serial_number: str, name: str):
        # カメラ情報
        self.model_name = model_name
        self.serial_number = serial_number
        self.name = name
        print(f"Creating camera instance(Model Name: {self.model_name}, Serial Number: {self.serial_number})...")

        # カメラの設定情報を格納したディレクトリを指定
        self.camera_setting_dir = "C:/Users/shogo.sasaguchi_hutz/Documents/錦城_医療ゴム"

        # コンバータ設定 (RAW->numpy変換用)
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    # カメラ接続処理
    def connect(self):
        try:
            print(f"Connecting to {self.name}.")
            # シリアルナンバー指定でカメラ起動
            dummy_device = pylon.DeviceInfo()
            device_info = dummy_device.SetSerialNumber(
                self.serial_number
            )  # dummy_deviceの中間変数を挟まないとなぜかコアダンプする
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(device_info))
            self.camera.Open()

            # パラメータファイル読みこみ
            file_path = f"{self.camera_setting_dir}/{self.model_name}_{self.serial_number}.pfs"
            print(f".pfs file_path: {file_path}")
            pylon.FeaturePersistence.Load(file_path, self.camera.GetNodeMap(), True)

            # 露光時間を設定（pfsファイルから読み込み）
            with open(file_path) as pfs_file:
                lines = pfs_file.readlines()
                # USBカメラの場合
                if lines[2][19:34] == "UsbCameraParams":
                    for line in lines:
                        if line[0:12] == "ExposureTime" and line[0:16] != "ExposureTimeMode":
                            self.exposure_time = int(line[12:20].strip().split(".")[0])
                            break
                # GigEカメラの場合
                elif lines[2][19:29] == "GigECamera":
                    for line in lines:
                        if line[0:15] == "ExposureTimeRaw":
                            self.exposure_time = int(line[15:20].strip().split(".")[0])
                            break

            print(f"Successfully connected to {self.name}.")
            return True

        except Exception as e:
            print(f"\nCamera connection error: {e}\n")
            traceback.print_exc()
            return False

    # カメラ切断処理
    def disconnect(self):
        try:
            print(f"Disconnectiong from {self.name}...")
            if self.camera.IsOpen():
                self.camera.Close()
            print(f"Successfully disconnected from {self.name}.")
            return True

        except Exception as e:
            print(f"\nCamera disconnection error: {e}\n")
            traceback.print_exc()
            return False

    # 連続撮影開始
    def start_continuous_grab(self):
        try:
            print(f"Starting continuous grabbing by {self.name}.")
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            print(f"Continuous grabbing by {self.name} is started.")
            return True

        except Exception as e:
            print(f"\nstart_continuous_grab in Camera class: {e}\n")
            traceback.print_exc()
            return False

    # 連続撮影停止
    def stop_continuous_grab(self):
        try:
            print(f"Stopping continuous grabbing by {self.name}.")
            self.camera.StopGrabbing()
            print(f"Continuous grabbing by {self.name} is stopped.")
            return True

        except Exception as e:
            print(f"\nstop_continuous_grab error in Camera class: {e}\n")
            traceback.print_exc()
            return False

    # ワンショット撮影
    def grab_one(self):
        try:
            result = self.camera.GrabOne(self.exposure_time)
            if result.GrabSucceeded():
                image = self.converter.Convert(result)
                img = image.GetArray()
                del image
                return img
            else:
                return None

        except Exception as e:
            print(f"\ngrab error in Camera class: {e}\n")
            traceback.print_exc()
            return False

    # 連続撮影中の画像から１枚取得
    def grab(self):
        try:
            grab_result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                image = self.converter.Convert(grab_result)
                img = image.GetArray()
                grab_result.Release()
                del image
                return img
            else:
                grab_result.Release()
                return None

        except Exception as e:
            print(f"\nretrieve error in Camera class: {e}\n")
            traceback.print_exc()
            return None


if __name__ == "__main__":
    camera = Camera(model_name="acA2440-20gc", serial_number="24144460", name="camera")
    # 接続が成功すること
    print("接続成功") if camera.connect() else print("接続失敗")
    # ワンショット撮影が成功すること
    image = camera.grab_one()
    print(image)
    del image
    # 連続撮影がスタートできること
    print("連続撮影スタート成功") if camera.start_continuous_grab() else print("連続撮影スタート失敗")
    # 連続撮影中の画像から１枚取得できること
    image = camera.grab()
    print(image)
    del image
    # 連続撮影が停止できること
    print("連続撮影停止成功") if camera.stop_continuous_grab() else print("連続撮影停止失敗")
    # 正常にカメラをクローズできること
    print("カメラクローズ成功") if camera.disconnect() else print("カメラクローズ失敗")

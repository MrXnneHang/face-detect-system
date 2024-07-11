import sys
import cv2
import os
import threading
from PIL import Image
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap, QImage,QIcon
from qframelesswindow import FramelessWindow
from PyQt5.QtWidgets import QApplication, QWidget,QMessageBox
from mainwindow import Main_Window
from window_1 import Window_1
from delete_window import Delete_window
from time import sleep
import PIL
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from util import load_config
from util import load_config, read_userdata_from_path, custom_round, read_users_from_database
from insert import insert
from datetime import datetime
from time import sleep

config = load_config()

class Login(FramelessWindow, Main_Window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Button3.clicked.connect(self.showWindow2)
        self.Button2.clicked.connect(self.showWindow1)

        self.Button1.clicked.connect(self.on_button1_click)
        self.Button4.clicked.connect(self.on_button2_click)
        self.stop_detection = threading.Event()
        self.cap = None
        self.resnet = None
        # Start the camera initialization in a separate thread
        self.camera_thread = threading.Thread(target=self.initialize_camera)
        self.camera_thread.start()

        self.model_thread = threading.Thread(target=self.initialize_model)
        self.model_thread.start()
        self.alreay_open = False



    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0)
        # sleep(2)  # Add a small delay to ensure the camera is initialized
    def initialize_model(self):
        config = load_config()
        device = config["device"]
        # 设置设备
        self.device = torch.device(device)

        # 定义MTCNN进行人脸检测
        self.mtcnn = MTCNN(
            image_size=160, margin=0, min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
            device=device
        )

        # 定义Facenet模型
        self.resnet = InceptionResnetV1(pretrained="vggface2").to(device)
        self.resnet.eval()
    def on_button1_click(self):
        self.stop_detection.clear()
        self.detect_user_and_display()

    def on_button2_click(self):
        self.upload_users()

    def stopCamera(self):
        self.stop_detection.set()
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None
    
    def run_detection(self):
            for frame, matched_name in self.detect_user():
                if self.stop_detection.is_set():
                    break
                self.update_label(frame, matched_name)
    def detect_user_and_display(self):
        if not self.alreay_open:
            threading.Thread(target=self.run_detection).start()
            self.alreay_open = True
        else:
            print("已经在运行了。")
            pass


    def update_label(self, frame, matched_name):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.Image_label.setPixmap(pixmap)
        self.label_3.setText(matched_name)

    def closeEvent(self, event):
        self.stop_detection.set()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    def showWindow1(self):
        w_1 = window_1(self.cap)
        sleep(1)
        w_1.show()

    def showWindow2(self):

        w_2 = delete_window()
        w_2.show()
    def wait_load_model(self):
        while True:
            if self.resnet is not None:
                break
            else:
                sleep(0.2)
                print("等待模型加载..")
    def wait_camera(self):
        while True:
            if self.cap:
                break
            else:
                sleep(0.2)
                print("等待摄像头打开..")
    def upload_users(self):
        self.wait_load_model()
        users = []
        user_data = []
        config = load_config()
        imgs_dir = config["imgs_dir"]
        imgs = os.listdir(imgs_dir)
        imgs = [img for img in imgs if ".jpg" in img]
        img_paths = [os.path.join(imgs_dir, img) for img in imgs]
        for img_path in img_paths:
            img = Image.open(img_path)
            img = self.mtcnn(img)
            img = img.unsqueeze(0).to(self.device)
            feature = self.resnet(img)
            feature = feature.cpu().detach().numpy()
            feature = [custom_round(float(f)) for f in feature[0]]
            user_data = read_userdata_from_path(img_path)
            user_data.append(feature)
            user_data = tuple(user_data)
            users.append(user_data)

        insert(users)
        return tuple(user_data)


    def detect_user(self):
        self.wait_load_model()
        users = read_users_from_database()
        data_features = [torch.tensor(users[i]["features"]).to(self.device) for i in range(len(users))]

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            imgs = self.mtcnn(pil_img)
            landmarks, _, _ = self.mtcnn.detect(pil_img, landmarks=True)
            box = 0
            flag = 0
            matched_name = ""

            if imgs is not None:
                imgs = imgs.unsqueeze(0).to(self.device)
                features = [self.resnet(face.unsqueeze(0)) for face in imgs]
                

                for i, feature in enumerate(features):
                    no_match = 0
                    for index, data_feature in enumerate(data_features):
                        similarity = torch.dist(feature, data_feature, p=2)
                        print(similarity)
                        if similarity < 0.78:
                            matched_name = users[index]["name"]
                            print("发现匹配人员:", matched_name, similarity)
                            current_time = datetime.now()
                            print("发现时间:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
                            frame_box = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            landmark = landmarks[i]
                            x1, y1, x2, y2 = landmark[:4].astype(int)
                            cv2.rectangle(frame_box, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            box = frame_box
                            flag = 1
                        else:
                            no_match += 1
                            frame_box = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            landmark = landmarks[i]
                            x1, y1, x2, y2 = landmark[:4].astype(int)
                            cv2.rectangle(frame_box, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            box = frame_box
                            flag = 1
                        if no_match == len(data_features):
                            matched_name = "没有找到这个人员。"
                            print(matched_name)
                    if len(data_features) == 0:
                        print("没有找到这个人")
                        matched_name = "没有找到这个人员。"

                        

            if flag == 0:
                yield frame, matched_name
            else:
                yield box, matched_name

        # self.cap.release()
        cv2.destroyAllWindows()


class window_1(FramelessWindow, Window_1):
    def __init__(self,cap):
        super().__init__()
        self.setupUi(self)
        self.pushButton_4.clicked.connect(self.Close)
        self.pushButton_2.clicked.connect(self.start_camera)
        self.pushButton_1.clicked.connect(self.take_photo)
        self.pushButton_3.clicked.connect(self.change_name)
        self.camera = cap
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.close_window = 0
        # self.debug_timer = QTimer()
        # self.debug_timer.timeout.connect(self.debug)
        # self.debug_timer.start(5)
        # 很神奇如果进入这个window后不读摄像机，就会秒关闭。但是一直读就不会关闭。
        self.debug_thread = threading.Thread(target=self.debug)
        self.debug_thread.start()

    def debug(self):
        while not self.close_window:
            self.camera.read()
            sleep(0.2)
    def Close(self):
        self.close_window=1
        sleep(0.3)
        self.close()
    def Open(self): 
        self.show()

    def change_name(self):
        self.take_photo()
        
        test_1 = self.lineEdit_1.text()
        test_2 = self.lineEdit_2.text()

        # 指定要修改文件名称的目录路径
        directory = './users/'
        # 指定要修改的文件名
        old_filename = 'photo.jpg'
        # 指定新的文件名
        new_filename = test_1+'_'+test_2+'.jpg'
        # 获取原始文件路径
        original_path = os.path.join(directory, old_filename)
        # 获取新的文件路径
        new_path = os.path.join(directory, new_filename)
        # 重命名文件
        os.rename(original_path, new_path)
        self.label_1.setText("录入成功！")
    

    def start_camera(self):
        self.timer.start(20)  # 以大约50fps的速度更新画面

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(image)
            self.Image_label.setPixmap(pix)

    def take_photo(self):
        ret, frame = self.camera.read()
        if ret:
            photo_path = './users/photo.jpg'
            cv2.imwrite(photo_path, frame)
            print(f'Photo saved to {photo_path}')
        self.label_1.setText("拍照成功！")

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

class delete_window(FramelessWindow, Delete_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_3.clicked.connect(self.delete)
        self.pushButton_4.clicked.connect(self.close)

    def Close(self):
        self.close()
    def Open(self):
        self.show()

    def delete(self):
        test_1 = self.lineEdit_1.text()
        test_2 = self.lineEdit_2.text()
        # 指定要删除文件所在的目录路径
        directory = './users/'
        # 指定要删除的文件名
        filename = test_1+'_'+test_2+'.jpg'

        # 获取文件路径
        file_path = os.path.join(directory, filename)

        # 检查文件是否存在
        if os.path.exists(file_path):
            # 删除文件
            os.remove(file_path)
            self.label_1.setText("成功删除"+test_2)
        else:
            self.label_1.setText("用户不存在")

if __name__ == "__main__":

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    m = Login()
    m.wait_load_model()
    m.wait_camera()
    m.setWindowIcon(QIcon(config["logo"]))
    m.show()
    

    app.exec_()
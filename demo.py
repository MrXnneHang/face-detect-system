import sys
import cv2
import os
import threading
from PIL import Image
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QPixmap, QImage,QIcon
from qframelesswindow import FramelessWindow
from PyQt5.QtWidgets import QApplication, QWidget
from mainwindow import Main_Window
from window_1 import Window_1
from delete_window import Delete_window
from face import upload_users, detect_user
from time import sleep
import PIL
import numpy as np

from util import load_config

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
        # Start the camera initialization in a separate thread
        self.camera_thread = threading.Thread(target=self.initialize_camera)
        self.camera_thread.start()

        self.Addbijin()
        self.AddLogo()
    def Addbijin(self):
        self.img = PIL.Image.open(config["bg1"])
        self.img = self.img.resize((521, 391))
        self.img = np.array(self.img)
        # rgb_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        rgb_image = self.img
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.Image_label.setPixmap(pixmap)

    def AddLogo(self):
        self.img = PIL.Image.open(config["logo"])
        self.img = self.img.resize((108,108))
        self.img = np.array(self.img)
        # rgb_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        rgb_image = self.img
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.logo.setPixmap(pixmap)
    def initialize_camera(self):
        self.cap = cv2.VideoCapture(0)
        sleep(2)  # Add a small delay to ensure the camera is initialized
    def on_button1_click(self):
        self.stop_detection.clear()
        self.detect_user_and_display()

    def on_button2_click(self):
        upload_users()

    def stopCamera(self):
        self.stop_detection.set()
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None
    
    def run_detection(self):
            for frame, matched_name in detect_user():
                if self.stop_detection.is_set():
                    break
                self.update_label(frame, matched_name)
    def detect_user_and_display(self):
        threading.Thread(target=self.run_detection).start()

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
        if self.cap:
            self.stopCamera()
            sleep(0.2)
        w_1 = window_1()
        w_1.show()

    def showWindow2(self):
        if self.cap:
            self.stopCamera()
            sleep(0.2)

        w_2 = delete_window()
        w_2.show()

class window_1(FramelessWindow, Window_1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_4.clicked.connect(self.Close)
        self.pushButton_2.clicked.connect(self.start_camera)
        self.pushButton_1.clicked.connect(self.take_photo)
        self.pushButton_3.clicked.connect(self.change_name)
        self.camera = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
                # Start the camera initialization in a separate thread
        self.camera_thread = threading.Thread(target=self.initialize_camera)
        self.camera_thread.start()


    def Close(self):
        self.close()
    def Open(self): 
        self.show()

    def change_name(self):

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
    
    def initialize_camera(self):
        self.camera = cv2.VideoCapture(0)
        sleep(2)  # Add a small delay to ensure the camera is initialized

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
        if self.camera:
            self.camera.release()
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
    w_1 = window_1()
    w_2 = delete_window()
    m.setWindowIcon(QIcon("./img/logo.jpg"))

    m.show()

    app.exec_()
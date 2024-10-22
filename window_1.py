# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window_1.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import PIL
import PIL.Image
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import QtCore, QtGui, QtWidgets
from qfluentwidgets import PrimaryPushButton

from util import load_config


config = load_config()
class Window_1(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(878, 518)
        self.label_1 = QtWidgets.QLabel(Form)
        self.label_1.setGeometry(QtCore.QRect(660, 300, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_1.setFont(font)
        self.label_1.setObjectName("label_1")
        self.pushButton_1 = PrimaryPushButton(Form)
        self.pushButton_1.setGeometry(QtCore.QRect(320, 470, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_1.setFont(font)
        self.pushButton_1.setObjectName("pushButton_1")
        self.pushButton_2 = PrimaryPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(130, 470, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.Image_label = QtWidgets.QLabel(Form)
        self.Image_label.setGeometry(QtCore.QRect(30, 40, 521, 391))
        self.Image_label.setText("")
        self.Image_label.setObjectName("Image_label")
        self.tixing = QtWidgets.QLabel(Form)
        self.tixing.setGeometry(QtCore.QRect(610, 40, 220, 290)) 
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(580, 360, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(580, 400, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.lineEdit_1 = QtWidgets.QLineEdit(Form)
        self.lineEdit_1.setGeometry(QtCore.QRect(630, 390, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_1.setFont(font)
        self.lineEdit_1.setObjectName("lineEdit_1")
        self.pushButton_3 = PrimaryPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(630, 450, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(630, 350, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton_4 = PrimaryPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(720, 450, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.add_bijin()
        self.add_tixing()
    
    # 加入背景图片
    def add_bijin(self):
        self.img = PIL.Image.open(config["bg2"])
        self.img = self.img.resize((521, 391))
        self.img = np.array(self.img)
        # rgb_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        rgb_image = self.img
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.Image_label.setPixmap(pixmap)
    # 加入猫娘图片
    def add_tixing(self):
        self.img = PIL.Image.open(config["bg3"])
        self.img = self.img.resize((220, 391))
        self.img = np.array(self.img)
        # rgb_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        rgb_image = self.img
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.tixing.setPixmap(pixmap) 

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_1.setText(_translate("Form", "录入程序"))
        self.pushButton_1.setText(_translate("Form", "拍照"))
        self.pushButton_2.setText(_translate("Form", "打开摄像头"))
        self.label_2.setText(_translate("Form", "姓名："))
        self.label_5.setText(_translate("Form", "学号："))
        self.pushButton_3.setText(_translate("Form", "确认"))
        self.pushButton_4.setText(_translate("Form", "完成"))
from qfluentwidgets import PrimaryPushButton

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

import models
from form_profile_designer import Ui_FormProfile


class FormProfile(QtWidgets.QDialog, Ui_FormProfile):
    def __init__(self, employee=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.employee = employee
        # SETTINGS
        if self.employee is not None:
            self.__set_employee_data()
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        # self.button_accept.clicked.connect()
        # self.button_cancel.clicked.connect()
        self.frame_header.mouseMoveEvent = self.__frame_header_move_window
        self.frame_header.mousePressEvent = self.__frame_header_mouse_press

    # EVENTS
    def __frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def __frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    # SETTINGS
    def __get_departments(self):
        pass

    def __set_employee_data(self):
        self.lineEdit_id.setText(str(self.employee.id))
        self.lineEdit_name.setText(self.employee.name)
        self.lineEdit_phonenumber.setText(self.employee.phone_number)
        self.comboBox_gender.setCurrentIndex(self.employee.gender.value - 1)
        self.label_photo.setScaledContents(False)
        pixmap = QPixmap(QImage(f'nginx/html{self.employee.face}'))
        pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
        self.label_photo.setPixmap(pixmap)
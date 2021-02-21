from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

import models
from form_devices_designer import Ui_FormDevices


class FormDevices(QtWidgets.QDialog, Ui_FormDevices):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        # SETTINGS
        # SYSTEM BUTTONS, FRAME HEADER
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self.__button_accept_clicked)
        self.button_cancel.clicked.connect(self.__button_cancel_clicked)
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

    def __button_accept_clicked(self, event):
        self.dialog_result = 1
        self.close()

    def __button_cancel_clicked(self, event):
        self.dialog_result = 0
        self.close()
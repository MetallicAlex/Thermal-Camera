import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt

from form_main_designer import Ui_MainWindow


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # SETTINGS
        self.theme = self.__get_theme('dark theme')
        self.stackedWidget.setCurrentWidget(self.page_device)
        # DATA
        # SYSTEM BUTTONS, HEADER FRAME AND SIZEGRIP
        self.button_close.clicked.connect(lambda: self.close())
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")
        self.frame_header.mouseMoveEvent = self.__frame_header_move_window
        self.frame_header.mousePressEvent = self.__frame_header_mouse_press
        # MENU BUTTONS
        self.button_device.clicked.connect(self.__button_device_clicked)
        self.button_database.clicked.connect(self.__button_database_clicked)
        # PAGE DEVICE
        # PAGE DATABASE
        # PAGE STATISTIC

    # EVENTS
    def __frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def __frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def __button_device_clicked(self, event):
        self.__update_system_buttons(self.button_device)
        self.stackedWidget.setCurrentWidget(self.page_device)

    def __button_database_clicked(self, event):
        self.__update_system_buttons(self.button_database)
        self.stackedWidget.setCurrentWidget(self.page_device)

    # SETTINGS
    def __get_theme(self, theme=str):
        with open('data/themes.json') as file:
            data = json.load(file, strict=False)
        return data[theme]

    # OTHERS
    def __update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['button_device'])
        self.button_database.setStyleSheet(self.theme['button_database'])
        button.setStyleSheet(self.theme[button.objectName()] + "QPushButton{border-right: 7px solid rgb(44, 49, 60);}")

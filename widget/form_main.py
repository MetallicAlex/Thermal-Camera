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
        self.button_device.setStyleSheet("QPushButton {\n"
                                         "    background-position: center;\n"
                                         "    background-repeat: no-reperat;\n"
                                         "    border: none;\n"
                                         "    border-right: 7px solid rgb(85, 170, 255);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "}\n"
                                         "QPushButton:hover {\n"
                                         "    background-color: rgb(40, 44, 52);\n"
                                         "}\n"
                                         "QPushButton:pressed {    \n"
                                         "    background-color: rgb(85, 170, 255);\n"
                                         "}")
        self.stackedWidget.setCurrentWidget(self.page_device)

    def __button_database_clicked(self, event):
        self.button_database.setStyleSheet("QPushButton {\n"
                                           "    background-position: center;\n"
                                           "    background-repeat: no-reperat;\n"
                                           "    border: none;\n"
                                           "    border-right: 7px solid rgb(85, 170, 255);\n"
                                           "    color: rgb(255, 255, 255);\n"
                                           "}\n"
                                           "QPushButton:hover {\n"
                                           "    background-color: rgb(40, 44, 52);\n"
                                           "}\n"
                                           "QPushButton:pressed {    \n"
                                           "    background-color: rgb(85, 170, 255);\n"
                                           "}")
        self.stackedWidget.setCurrentWidget(self.page_database)

    # OTHERS

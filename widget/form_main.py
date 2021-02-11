import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect, \
    QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt

from form_main_designer import Ui_MainWindow
import models


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # SETTINGS
        self.theme = self.__get_theme('dark theme')
        self.__load_employees_to_table()
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
        self.stackedWidget.setCurrentWidget(self.page_database)

    # SETTINGS
    def __get_theme(self, theme=str):
        with open('data/themes.json') as file:
            data = json.load(file, strict=False)
        return data[theme]

    # OTHERS
    def __update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['button_device'])
        self.button_database.setStyleSheet(self.theme['button_database'])
        button.setStyleSheet(self.theme[button.objectName()] +
                             "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")

    def __get_employees_from_database(self):
        with models.get_session() as session:
            employees = session.query(models.Employee).all()
        return employees

    def __get_statistics_from_database(self):
        pass

    def __load_employees_to_table(self):
        self.table_persons.removeRow(0)
        for row_position, employee in enumerate(self.__get_employees_from_database()):
            self.table_persons.insertRow(row_position)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, employee.id)
            self.table_persons.setItem(row_position, 0, item)
            self.table_persons.setItem(row_position, 1, QTableWidgetItem(employee.face))
            self.table_persons.setItem(row_position, 2, QTableWidgetItem(employee.name))
            self.table_persons.setItem(row_position, 3, QTableWidgetItem(employee.name_department))
            self.table_persons.setItem(row_position, 4, QTableWidgetItem(str(employee.gender)))
            self.table_persons.setItem(row_position, 5, QTableWidgetItem(str(employee.phone_number)))
import json
import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect, \
    QTableWidgetItem, QLabel
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
        self.__load_departments_to_table()
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
        self.button_statistic.clicked.connect(self.__button_statistic_clicked)
        self.button_settings.clicked.connect(self.__button_settings_clicked)
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

    def __button_statistic_clicked(self, event):
        self.__update_system_buttons(self.button_statistic)
        self.stackedWidget.setCurrentWidget(self.page_statistic)

    def __button_settings_clicked(self, event):
        self.__update_system_buttons(self.button_settings)
        self.stackedWidget.setCurrentWidget(self.page_settings)

    # SETTINGS
    def __get_theme(self, theme=str):
        with open('data/themes.json') as file:
            data = json.load(file, strict=False)
        return data[theme]

    # OTHERS
    def __update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['button_device'])
        self.button_database.setStyleSheet(self.theme['button_database'])
        self.button_statistic.setStyleSheet(self.theme['button_statistic'])
        self.button_settings.setStyleSheet(self.theme['button_settings'])
        button.setStyleSheet(self.theme[button.objectName()] +
                             "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")

    def __get_departments_from_database(self):
        with models.get_session() as session:
            departments = session.query(models.Department).all()
        return departments

    def __get_employees_from_database(self):
        with models.get_session() as session:
            employees = session.query(models.Employee).all()
        return employees

    def __get_statistics_from_database(self):
        with models.get_session() as session:
            statistics = session.query(models.Statistic).all()
        return statistics

    def __load_employees_to_table(self):
        self.table_persons.removeRow(0)
        for row_position, employee in enumerate(self.__get_employees_from_database()):
            self.table_persons.insertRow(row_position)
            item = QTableWidgetItem()
            item.setData(Qt.EditRole, employee.id)
            item.setTextAlignment(Qt.AlignCenter)
            self.table_persons.setItem(row_position, 1, item)
            self.table_persons.setItem(row_position, 2, self.__get_item_image(employee.face))
            self.table_persons.setItem(row_position, 3, QTableWidgetItem(employee.name))
            self.table_persons.setItem(row_position, 4, QTableWidgetItem(employee.name_department))
            self.table_persons.setItem(row_position, 5, QTableWidgetItem(str(employee.gender)))
            self.table_persons.setItem(row_position, 6, QTableWidgetItem(str(employee.phone_number)))
        self.table_persons.resizeColumnsToContents()
        self.table_persons.resizeRowsToContents()

    def __get_item_image(self, path_image=str):
        item = QTableWidgetItem()
        if os.path.isfile(f'nginx/html{path_image}'):
            pixmap = QPixmap(QImage(f'nginx/html{path_image}'))
        else:
            pixmap = QPixmap(QImage('data/resources/icons/user.png'))
        pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio)
        item.setData(Qt.DecorationRole, pixmap)
        return item

    def __load_departments_to_table(self):
        self.table_department.removeRow(0)
        for row_position, department in enumerate(self.__get_departments_from_database()):
            self.table_department.insertRow(row_position)
            self.table_department.setItem(row_position, 0, QTableWidgetItem(department.name))
        self.table_persons.resizeColumnsToContents()
        self.table_persons.resizeRowsToContents()

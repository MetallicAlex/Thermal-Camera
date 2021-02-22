import json
import os
import webbrowser as wb

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect, \
    QTableWidgetItem, QLabel, QCheckBox, QHeaderView
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt

from form_main_designer import Ui_MainWindow
from form_profile import FormProfile
from form_devices import FormDevices
import models
from widget.platforms.subscribe_platform import SubscribePlatform


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.form_profile = FormProfile()
        self.theme = self.__get_theme('dark theme')
        self.subscribe_platform = SubscribePlatform()
        self.subscribe_platform.set_host_port('192.168.1.2', client_name='SP')
        self.thread = QtCore.QThread()
        # SETTINGS
        self.__load_devices_info_to_table()
        self.__load_employees_to_table()
        # self.__load_departments_to_table()
        self.__load_statistics_to_table()
        self.stackedWidget.setCurrentWidget(self.page_device)
        self.button_device.setStyleSheet(self.theme['system-button'] +
                                         "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")
        # SYSTEM BUTTONS, HEADER FRAME AND SIZEGRIP
        self.button_close.clicked.connect(lambda: self.close())
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.button_maximize_restore.clicked.connect(lambda: self.showMaximized())
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
        self.button_search_device.clicked.connect(self.__button_search_device_clicked)
        self.button_edit_device.clicked.connect(self.__button_edit_device_clicked)
        # PAGE DATABASE
        self.button_add_person.clicked.connect(self.__button_add_person_clicked)
        self.button_edit_person.clicked.connect(self.__button_edit_person_clicked)
        self.button_delete_person.clicked.connect(self.__button_delete_person_clicked)
        # PAGE STATISTIC
        self.subscribe_platform.moveToThread(self.thread)
        self.subscribe_platform.statistic.connect(self.__add_statistic_to_table)
        self.thread.started.connect(self.subscribe_platform.run)
        self.thread.start()

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

    # EVENTS-DATABASE
    def __button_add_person_clicked(self, event):
        self.form_profile = FormProfile()
        self.form_profile.exec_()
        if self.form_profile.dialog_result == 1:
            with models.get_session() as session:
                session.add(self.form_profile.employee)
            row_position = self.table_persons.rowCount()
            self.table_persons.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_persons.setCellWidget(row_position, 0, item)
            self.table_persons.setItem(row_position, 1, self.__get_item_to_cell(self.form_profile.employee.id))
            self.table_persons.setItem(row_position, 2, self.__get_item_image(self.form_profile.employee.face))
            self.table_persons.setItem(row_position, 3, QTableWidgetItem(self.form_profile.employee.name))
            self.table_persons.setItem(row_position, 4, QTableWidgetItem(self.form_profile.employee.name_department))
            self.table_persons.setItem(row_position, 5, QTableWidgetItem(str(self.form_profile.employee.gender)))
            self.table_persons.setItem(row_position, 6, QTableWidgetItem(str(self.form_profile.employee.phone_number)))
            self.table_persons.resizeColumnsToContents()
            self.table_persons.resizeRowsToContents()

    def __button_edit_person_clicked(self, event):
        with models.get_session() as session:
            employee = session.query(models.Employee) \
                .filter(models.Employee.id == int(self.table_persons.item(self.table_persons.currentRow(), 1).text())) \
                .scalar()
            self.form_profile = FormProfile(employee)
            self.form_profile.exec_()
            if self.form_profile.dialog_result == 1:
                session.query(models.Employee).filter(models.Employee.id == employee.id) \
                    .update({models.Employee.name: self.form_profile.employee.name,
                             models.Employee.id: self.form_profile.employee.id,
                             models.Employee.name_department: self.form_profile.employee.name_department,
                             models.Employee.face: self.form_profile.employee.face,
                             models.Employee.gender: self.form_profile.employee.gender,
                             models.Employee.phone_number: self.form_profile.employee.phone_number})
                row_position = self.table_persons.currentRow()
                self.table_persons.setItem(row_position, 1, self.__get_item_to_cell(self.form_profile.employee.id))
                self.table_persons.setItem(row_position, 2, self.__get_item_image(self.form_profile.employee.face))
                self.table_persons.setItem(row_position, 3, QTableWidgetItem(self.form_profile.employee.name))
                self.table_persons.setItem(row_position, 4,
                                           QTableWidgetItem(self.form_profile.employee.name_department))
                self.table_persons.setItem(row_position, 5, QTableWidgetItem(str(self.form_profile.employee.gender)))
                self.table_persons.setItem(row_position, 6,
                                           QTableWidgetItem(str(self.form_profile.employee.phone_number)))
                self.table_persons.resizeColumnsToContents()
                self.table_persons.resizeRowsToContents()

    def __button_delete_person_clicked(self, event):
        with models.get_session() as session:
            employee = session.query(models.Employee) \
                .filter(models.Employee.id == int(self.table_persons.item(self.table_persons.currentRow(), 1).text())) \
                .scalar()
            session.delete(employee)
            self.table_persons.removeRow(self.table_persons.currentRow())

    # EVENTS-DEVICE
    def __button_search_device_clicked(self, event):
        self.form_devices = FormDevices()
        self.form_devices.exec_()

    def __button_edit_device_clicked(self, event):
        wb.open_new_tab(f'http://{self.table_devices.item(self.table_devices.currentRow(), 3).text()}:7080')

    # SETTINGS
    def __get_theme(self, theme=str):
        with open('data/themes.json') as file:
            data = json.load(file, strict=False)
        return data[theme]

    # DEVICES
    def __get_devices_info(self):
        with open('data/devices.json') as file:
            data = json.load(file, strict=False)
        return data

    def __load_devices_info_to_table(self):
        self.devices = self.__get_devices_info()
        for row_position, device in enumerate(self.devices):
            self.table_devices.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_devices.setCellWidget(row_position, 0, item)
            self.table_devices.setItem(row_position, 1, QTableWidgetItem(device['name']))
            self.table_devices.setItem(row_position, 2, QTableWidgetItem(device['serial']))
            self.table_devices.setItem(row_position, 3, QTableWidgetItem(device['ip']))
        # self.table_devices.resizeColumnsToContents()
        # self.table_devices.resizeRowsToContents()

    # DATABASE
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
            statistics = session.query(models.Statistic, models.Employee.name) \
                .filter(models.Statistic.id_employee == models.Employee.id).all()
        return statistics

    def __load_employees_to_table(self):
        for row_position, employee in enumerate(self.__get_employees_from_database()):
            self.table_persons.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_persons.setCellWidget(row_position, 0, item)
            self.table_persons.setItem(row_position, 1, self.__get_item_to_cell(employee.id))
            self.table_persons.setItem(row_position, 2, self.__get_item_image(employee.face))
            self.table_persons.setItem(row_position, 3, QTableWidgetItem(employee.name))
            self.table_persons.setItem(row_position, 4, QTableWidgetItem(employee.name_department))
            self.table_persons.setItem(row_position, 5, QTableWidgetItem(str(employee.gender)))
            self.table_persons.setItem(row_position, 6, QTableWidgetItem(str(employee.phone_number)))
        self.table_persons.resizeColumnsToContents()
        self.table_persons.resizeRowsToContents()

    def __load_departments_to_table(self):
        for row_position, department in enumerate(self.__get_departments_from_database()):
            self.table_department.insertRow(row_position)
            self.table_department.setItem(row_position, 0, QTableWidgetItem(department.name))
        self.table_persons.resizeColumnsToContents()
        self.table_persons.resizeRowsToContents()

    def __load_statistics_to_table(self):
        for row_position, statistic in enumerate(self.__get_statistics_from_database()):
            statistic, employee_name = statistic
            self.table_statistics.insertRow(row_position)
            self.table_statistics.setItem(row_position, 0, self.__get_item_to_cell(statistic.id_employee))
            self.table_statistics.setItem(row_position, 1, QTableWidgetItem(employee_name))
            self.table_statistics.setItem(row_position, 2, QTableWidgetItem(str(statistic.time)))
            self.table_statistics.setItem(row_position, 3, self.__get_item_to_cell(float(statistic.temperature)))
            self.table_statistics.setItem(row_position, 4, self.__get_item_to_cell(float(statistic.similar)))
        self.table_statistics.sortByColumn(2, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()

    # STATISTIC
    @QtCore.pyqtSlot(object)
    def __add_statistic_to_table(self, statistic):
        row_position = self.table_statistics.rowCount() - 1
        print(statistic)
        self.table_statistics.insertRow(row_position)
        with models.get_session() as session:
            employee_name = session.query(models.Employee.name)\
                .filter(models.Employee.id == statistic.id_employee).scalar()
        self.table_statistics.setItem(row_position, 0, self.__get_item_to_cell(statistic.id_employee))
        self.table_statistics.setItem(row_position, 1, QTableWidgetItem(employee_name))
        self.table_statistics.setItem(row_position, 2, QTableWidgetItem(str(statistic.time)))
        self.table_statistics.setItem(row_position, 3, self.__get_item_to_cell(float(statistic.temperature)))
        self.table_statistics.setItem(row_position, 4, self.__get_item_to_cell(float(statistic.similar)))
        self.table_statistics.sortByColumn(2, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        self.table_statistics.update()

    # OTHERS
    def __update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['system-button'])
        self.button_database.setStyleSheet(self.theme['system-button'])
        self.button_statistic.setStyleSheet(self.theme['system-button'])
        self.button_settings.setStyleSheet(self.theme['system-button'])
        button.setStyleSheet(self.theme['system-button'] +
                             "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")

    def __get_item_image(self, path_image=str):
        item = QTableWidgetItem()
        if os.path.isfile(f'nginx/html{path_image}'):
            pixmap = QPixmap(QImage(f'nginx/html{path_image}'))
        else:
            pixmap = QPixmap(QImage('data/resources/icons/user.png'))
        pixmap = pixmap.scaled(150, 200, Qt.KeepAspectRatio)
        item.setData(Qt.DecorationRole, pixmap)
        return item

    def __get_item_to_cell(self, value):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        item.setTextAlignment(Qt.AlignCenter)
        return item

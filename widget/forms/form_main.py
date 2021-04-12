import json
import os
import socket
import datetime
import time
from typing import Union

import numpy as np
import webbrowser as wb

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect, \
    QTableWidgetItem, QLabel, QCheckBox, QHeaderView
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt

from widget.forms.form_main_designer import Ui_MainWindow
from widget.forms.form_profile import FormProfile
from widget.forms.form_devices import FormDevices
import widget.models as models
from widget.management import DBManagement, DeviceManagement
from widget.platforms.subscribe_platform import SubscribePlatform
from widget.platforms.publish_platform import PublishPlatform


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        start = time.time()
        super().__init__()
        self.setupUi(self)
        # APPLICATIONS
        # self.start_nginx()
        # DATA
        self.device_management = DeviceManagement()
        self.device_management.find_host_info()
        self.database_management = DBManagement()
        self.form_profile = FormProfile()
        self.theme = self._get_theme('dark theme')
        self.host_name, self.host_ip = self._get_host_name_ip()
        if self.host_ip is not None:
            self.subscribe_platform = SubscribePlatform()
            self.subscribe_platform.set_host_port(self.host_ip, client_name='SP1')
            self.thread = QtCore.QThread()
            self.subscribe_platform.moveToThread(self.thread)
            self.subscribe_platform.statistic.connect(self._add_statistic_to_table)
            self.subscribe_platform.device.connect(self._update_device_info)
            self.thread.started.connect(self.subscribe_platform.run)
            self.thread.start()
            self.publish_platform = PublishPlatform(self.host_ip, client_name='PP1')
            # self.publish_platform.set_device(self.devices[0]['serial'], self.devices[0]['token'])
            # self.publish_platform.query_profiles_data()
            # self.publish_platform.set_device('7101384284372', '724970388')
        # SETTINGS
        self._load_devices_info_to_table()
        self._load_profiles_to_table()
        self._load_departments_to_table()
        self._load_statistics_to_table(low=str(datetime.datetime.now().replace(hour=0, minute=0, second=0)),
                                       high=str(datetime.datetime.now().replace(hour=23, minute=59, second=59)))
        self.stackedWidget.setCurrentWidget(self.page_device)
        self.button_device.setStyleSheet(self.theme['system-button'] +
                                         "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")
        # SYSTEM BUTTONS, HEADER FRAME AND SIZEGRIP
        self.button_close.clicked.connect(lambda: self.close())
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")
        self.frame_header.mouseMoveEvent = self._frame_header_move_window
        self.frame_header.mousePressEvent = self._frame_header_mouse_press
        # MENU BUTTONS
        self.button_device.clicked.connect(self._button_device_clicked)
        self.button_database.clicked.connect(self._button_database_clicked)
        self.button_statistic.clicked.connect(self._button_statistic_clicked)
        self.button_settings.clicked.connect(self._button_settings_clicked)
        # PAGE DEVICE
        self.button_search_device.clicked.connect(self._button_search_device_clicked)
        self.button_configure_device.clicked.connect(self._button_configure_device_clicked)
        self.table_devices.horizontalHeader().sectionPressed.connect(self._checkbox_header_devices_pressed)
        # PAGE DATABASE
        self.button_add_profile.clicked.connect(self._button_add_profile_clicked)
        self.button_edit_profile.clicked.connect(self._button_edit_profile_clicked)
        self.button_delete_profile.clicked.connect(self._button_delete_profile_clicked)
        self.button_send_device.clicked.connect(self._button_send_device_clicked)
        self.button_add_department.clicked.connect(self._button_add_department_clicked)
        self.button_delete_department.clicked.connect(self._button_delete_department_clicked)
        self.button_add_profiles_group.clicked.connect(self._button_add_profiles_group_clicked)
        self.button_add_profile_images.clicked.connect(self._button_add_profile_images_clicked)
        self.table_profiles.horizontalHeader().sectionPressed.connect(self._checkbox_header_persons_pressed)
        self.table_departments.horizontalHeader().sectionPressed.connect(self._checkbox_header_departments_pressed)
        # PAGE STATISTIC
        self.button_search_statistics.clicked.connect(self._button_search_statistics_clicked)
        self.button_all_statistic.clicked.connect(self._button_all_statistic_clicked)
        self.button_report.clicked.connect(self._button_report_clicked)
        self.dateTimeEdit_start.setDateTime(datetime.datetime.now().replace(hour=0, minute=0))
        self.dateTimeEdit_end.setDateTime(datetime.datetime.now().replace(hour=23, minute=59))
        print(time.time() - start)

    # EVENTS
    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_device_clicked(self, event):
        self._update_system_buttons(self.button_device)
        self.stackedWidget.setCurrentWidget(self.page_device)

    def _button_database_clicked(self, event):
        self._update_system_buttons(self.button_database)
        self.stackedWidget.setCurrentWidget(self.page_database)

    def _button_statistic_clicked(self, event):
        self._update_system_buttons(self.button_statistic)
        self.stackedWidget.setCurrentWidget(self.page_statistic)

    def _button_settings_clicked(self, event):
        self._update_system_buttons(self.button_settings)
        self.stackedWidget.setCurrentWidget(self.page_settings)

    # EVENTS-DATABASE
    def _button_add_profile_clicked(self, event):
        self.form_profile = FormProfile()
        self.form_profile.exec_()
        if self.form_profile.dialog_result == 1:
            self.database_management.add_profiles(self.form_profile.profile)
            row_position = self.table_profiles.rowCount()
            self.table_profiles.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_profiles.setCellWidget(row_position, 0, item)
            self.table_profiles.setItem(row_position, 1, self._get_item_to_cell(self.form_profile.profile.id))
            self.table_profiles.setItem(row_position, 2, self._get_item_image(self.form_profile.profile.face))
            self.table_profiles.setItem(row_position, 3, QTableWidgetItem(self.form_profile.profile.name))
            self.table_profiles.setItem(row_position, 4, QTableWidgetItem(self.form_profile.profile.name_department))
            self.table_profiles.setItem(row_position, 5, QTableWidgetItem(str(self.form_profile.profile.gender)))
            self.table_profiles.setItem(row_position, 6, QTableWidgetItem(str(self.form_profile.profile.phone_number)))
            self.table_profiles.resizeColumnsToContents()
            self.table_profiles.resizeRowsToContents()

    def _button_edit_profile_clicked(self, event):
        id_profiles = [self.table_profiles.item(row_position, 1).text()
                       for row_position in range(self.table_profiles.rowCount())
                       if self.table_profiles.cellWidget(row_position, 0).isChecked()]
        indexes = [row_position for row_position in range(self.table_profiles.rowCount())
                   if self.table_profiles.cellWidget(row_position, 0).isChecked()]
        profiles = self.database_management.get_profiles(*id_profiles)
        for profile, profile_id, row_position in zip(profiles, id_profiles, indexes):
            self.form_profile = FormProfile(profile)
            self.form_profile.exec_()
            if self.form_profile.dialog_result == 1:
                self.database_management.edit_profile(profile_id, profile)
                self.table_profiles.setItem(row_position, 1, self._get_item_to_cell(self.form_profile.profile.id))
                self.table_profiles.setItem(row_position, 2, self._get_item_image(self.form_profile.profile.face))
                self.table_profiles.setItem(row_position, 3, QTableWidgetItem(self.form_profile.profile.name))
                self.table_profiles.setItem(row_position, 4,
                                            QTableWidgetItem(self.form_profile.profile.name_department))
                self.table_profiles.setItem(row_position, 5,
                                            QTableWidgetItem(str(self.form_profile.profile.gender)))
                self.table_profiles.setItem(row_position, 6,
                                            QTableWidgetItem(str(self.form_profile.profile.phone_number)))
            self.table_profiles.resizeColumnsToContents()
            self.table_profiles.resizeRowsToContents()

    def _button_delete_profile_clicked(self, event):
        button_reply = QMessageBox.question(self, 'Database Manager', 'Are you sure you want to delete persons?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if button_reply == QMessageBox.Yes:
            id_profiles = [int(self.table_profiles.item(row_position, 1).text())
                           for row_position in range(self.table_profiles.rowCount())
                           if self.table_profiles.cellWidget(row_position, 0).isChecked()]
            self.database_management.remove_profiles(*id_profiles)
            for row_position in range(self.table_profiles.rowCount() - 1, 0, -1):
                if self.table_profiles.cellWidget(row_position, 0).isChecked():
                    self.table_profiles.removeRow(row_position)

    def _button_send_device_clicked(self, event):
        if not self.table_profiles.horizontalHeaderItem(0).checkState():
            profile_ids = [int(self.table_profiles.item(row_position, 1).text())
                           for row_position in range(self.table_profiles.rowCount())
                           if self.table_profiles.cellWidget(row_position, 0).isChecked()]
        for device in self.devices:
            if device['state'] == 'online':
                print('online!')
                self.publish_platform.set_device(device['serial'], device['token'])
                if not self.table_profiles.horizontalHeaderItem(0).checkState():
                    self.publish_platform.add_profiles_data(profile_ids)
                else:
                    self.publish_platform.add_profiles_data()

    def _button_add_department_clicked(self, event):
        pass

    def _button_delete_department_clicked(self, event):
        pass

    def _button_add_profiles_group_clicked(self, event):
        pass

    def _button_add_profile_images_clicked(self, event):
        pass

    # EVENTS-DEVICE
    def _button_search_device_clicked(self, event):
        devices_ip = [device['ip'] for device in self.devices]
        self.form_devices = FormDevices(devices_ip)
        self.form_devices.exec_()

    def _button_configure_device_clicked(self, event):
        devices_ip = [self.table_devices.item(row_position, 5).text()
                      for row_position in range(self.table_devices.rowCount())
                      if self.table_devices.cellWidget(row_position, 0).isChecked()
                      and self.table_devices.item(row_position, 6).text() == 'online']
        print(devices_ip)
        for device_ip in devices_ip:
            wb.open_new_tab(f'http://{device_ip}:7080')

    # EVENTS-STATISTICS
    def _button_search_statistics_clicked(self, event):
        if self.radiobutton_time.isChecked():
            self._load_statistics_to_table(low=self.dateTimeEdit_start.text(),
                                           high=self.dateTimeEdit_end.text())
        elif self.radiobutton_temperature.isChecked():
            self._load_statistics_to_table(low=self.doubleSpinBox_min_temperature.value(),
                                           high=self.doubleSpinBox_max_temperature.value())

    def _button_all_statistic_clicked(self, event):
        self._load_statistics_to_table()

    def _button_report_clicked(self, event):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'JSON File (*.json);')
        if filename:
            self.database_management.create_passage_report(filename)

    def _checkbox_header_persons_pressed(self, index):
        if index == 0:
            list_checked_buttons = np.array([self.table_profiles.cellWidget(row_position, 0).isChecked()
                                             for row_position in range(self.table_profiles.rowCount())])
            if np.all(list_checked_buttons):
                for row_position in range(self.table_profiles.rowCount()):
                    self.table_profiles.cellWidget(row_position, 0).setCheckState(Qt.Unchecked)
                self._set_header_column_icon(self.table_profiles, False)
            else:
                for row_position in range(self.table_profiles.rowCount()):
                    self.table_profiles.cellWidget(row_position, 0).setCheckState(Qt.Checked)
                self._set_header_column_icon(self.table_profiles, True)

    def _checkbox_header_devices_pressed(self, index):
        if index == 0:
            list_checked_buttons = np.array([self.table_devices.cellWidget(row_position, 0).isChecked()
                                             for row_position in range(self.table_devices.rowCount())])
            if np.all(list_checked_buttons):
                for row_position in range(self.table_devices.rowCount()):
                    self.table_devices.cellWidget(row_position, 0).setCheckState(Qt.Unchecked)
                self._set_header_column_icon(self.table_devices, False)
            else:
                for row_position in range(self.table_devices.rowCount()):
                    self.table_devices.cellWidget(row_position, 0).setCheckState(Qt.Checked)
                self._set_header_column_icon(self.table_devices, True)

    def _checkbox_header_departments_pressed(self, index):
        if index == 0:
            list_checked_buttons = np.array([self.table_departments.cellWidget(row_position, 0).isChecked()
                                             for row_position in range(self.table_departments.rowCount())])
            if np.all(list_checked_buttons):
                for row_position in range(self.table_departments.rowCount()):
                    self.table_departments.cellWidget(row_position, 0).setCheckState(Qt.Unchecked)
                self._set_header_column_icon(self.table_departments, False)
            else:
                for row_position in range(self.table_departments.rowCount()):
                    self.table_departments.cellWidget(row_position, 0).setCheckState(Qt.Checked)
                self._set_header_column_icon(self.table_departments, True)

    # SETTINGS
    def _get_theme(self, theme=str):
        with open('data/themes.json') as file:
            data = json.load(file, strict=False)
        return data[theme]

    # DEVICES
    def _get_devices_info(self):
        with open('data/devices.json') as file:
            data = json.load(file, strict=False)
        return data

    @QtCore.pyqtSlot(dict)
    def _update_device_info(self, data):
        print('RUN BASIC')
        for row_position in range(self.table_devices.rowCount()):
            if self.table_devices.item(row_position, 3).text() == data['device_id']:
                self.devices[row_position]['name'] = data['datas']['basic_parameters']['dev_name']
                item = QTableWidgetItem(data['datas']['basic_parameters']['dev_name'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 1, item)
                self.devices[row_position]['model'] = data['datas']['version_info']['dev_model']
                item = QTableWidgetItem(data['datas']['version_info']['dev_model'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 2, item)
                item = QTableWidgetItem(data['device_id'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 3, item)
                self.devices[row_position]['ip'] = data['datas']['network_cofnig']['ip_addr']
                item = QTableWidgetItem(data['datas']['network_cofnig']['ip_addr'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 5, item)
                item = QTableWidgetItem('online')
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 6, item)
                self.devices[row_position]['state'] = 'online'
                break

    def _get_host_name_ip(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            return host_name, host_ip
        except:
            QMessageBox.information('Unable to get Hostname and IP')
            return None

    def _load_devices_info_to_table(self):
        self.devices = self._get_devices_info()
        state = 'not online'
        for row_position, device in enumerate(self.devices):
            self.table_devices.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_devices.setCellWidget(row_position, 0, item)
            item = QTableWidgetItem(device['name'])
            item.setTextAlignment(Qt.AlignCenter)
            self.table_devices.setItem(row_position, 2, item)
            item = QTableWidgetItem(device['serial'])
            item.setTextAlignment(Qt.AlignCenter)
            self.table_devices.setItem(row_position, 3, item)
            item = QTableWidgetItem(device['mac'])
            item.setTextAlignment(Qt.AlignCenter)
            self.table_devices.setItem(row_position, 4, item)
            item = QTableWidgetItem(device['ip'])
            item.setTextAlignment(Qt.AlignCenter)
            self.table_devices.setItem(row_position, 5, item)
            self.devices[row_position]['state'] = state
            item = QTableWidgetItem(state)
            item.setTextAlignment(Qt.AlignCenter)
            self.table_devices.setItem(row_position, 6, item)
            self.publish_platform.set_device(device['serial'], device['token'])
            self.publish_platform.get_device_info()
        self.table_devices.resizeColumnToContents(0)
        self.table_devices.resizeColumnToContents(2)
        self.table_devices.resizeColumnToContents(6)
        self.table_devices.resizeRowsToContents()

    # DATABASE
    def _load_profiles_to_table(self):
        for row_position, profile in enumerate(self.database_management.get_profiles()):
            self.table_profiles.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_profiles.setCellWidget(row_position, 0, item)
            self.table_profiles.setItem(row_position, 1, self._get_item_to_cell(profile.id))
            self.table_profiles.setItem(row_position, 2, self._get_item_image(profile.face))
            self.table_profiles.setItem(row_position, 3, QTableWidgetItem(profile.name))
            self.table_profiles.setItem(row_position, 4, QTableWidgetItem(profile.name_department))
            self.table_profiles.setItem(row_position, 5, QTableWidgetItem(str(profile.gender)))
            self.table_profiles.setItem(row_position, 6, QTableWidgetItem(str(profile.phone_number)))
            self.comboBox_profiles.addItem(profile.name)
        self.table_profiles.resizeColumnsToContents()
        self.table_profiles.resizeRowsToContents()

    def _load_departments_to_table(self):
        for row_position, department in enumerate(self.database_management.get_departments()):
            self.table_departments.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_departments.setCellWidget(row_position, 0, item)
            self.table_departments.setItem(row_position, 1, QTableWidgetItem(department.name))
        self.table_departments.resizeColumnToContents(0)
        self.table_departments.resizeRowsToContents()

    def _load_statistics_to_table(self, low: Union[str, float] = None,
                                  high: Union[str, float] = None,
                                  identifiers: list = None):
        self.table_statistics.setRowCount(0)
        for row_position, statistic in enumerate(self.database_management.get_statistics(
                low=low,
                high=high,
                identifiers=identifiers,
                profile_name=True)
        ):
            statistic, name = statistic
            self.table_statistics.insertRow(row_position)
            self.table_statistics.setItem(row_position, 0, self._get_item_to_cell(statistic.id_profile))
            self.table_statistics.setItem(row_position, 1, QTableWidgetItem(name))
            self.table_statistics.setItem(row_position, 2, QTableWidgetItem(str(statistic.time)))
            self.table_statistics.setItem(row_position, 3, self._get_item_to_cell(float(statistic.temperature)))
            self.table_statistics.setItem(row_position, 4, self._get_item_to_cell(float(statistic.similar)))
        # self.table_statistics.sortByColumn(2, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        # self.table_statistics.viewport().update()

    # STATISTIC
    @QtCore.pyqtSlot(object)
    def _add_statistic_to_table(self, statistic: models.Statistic):
        row_position = self.table_statistics.rowCount() - 1
        self.table_statistics.insertRow(row_position)
        self.table_statistics.setItem(row_position, 0, self._get_item_to_cell(statistic.id_profile))
        self.table_statistics.setItem(row_position, 1,
                                      QTableWidgetItem(self.database_management.get_profile_name(statistic.id_profile)))
        self.table_statistics.setItem(row_position, 2, QTableWidgetItem(str(statistic.time)))
        self.table_statistics.setItem(row_position, 3, self._get_item_to_cell(float(statistic.temperature)))
        self.table_statistics.setItem(row_position, 4, self._get_item_to_cell(float(statistic.similar)))
        # self.table_statistics.sortByColumn(2, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        self.table_statistics.update()

    # OTHERS
    def _update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['system-button'])
        self.button_database.setStyleSheet(self.theme['system-button'])
        self.button_statistic.setStyleSheet(self.theme['system-button'])
        self.button_settings.setStyleSheet(self.theme['system-button'])
        button.setStyleSheet(self.theme['system-button'] +
                             "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")

    def _get_item_image(self, path_image=str):
        item = QTableWidgetItem()
        if os.path.isfile(f'nginx/html{path_image}'):
            pixmap = QPixmap(QImage(f'nginx/html{path_image}'))
        else:
            pixmap = QPixmap(QImage('data/resources/icons/user.png'))
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        item.setData(Qt.DecorationRole, pixmap)
        return item

    def _get_item_to_cell(self, value):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _set_header_column_icon(self, table: QtWidgets.QTableWidget, checked: bool):
        item = QtWidgets.QTableWidgetItem()
        icon10 = QtGui.QIcon()
        if checked:
            icon10.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-check-circle.png"),
                             QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setCheckState(Qt.Checked)
        else:
            icon10.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-uncheck-circle.png"),
                             QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setCheckState(Qt.Unchecked)
        item.setIcon(icon10)
        table.setHorizontalHeaderItem(0, item)

    # NGINX
    def start_nginx(self):
        os.system('nginx\\nginx.exe')

    def quit_nginx(self):
        os.system('nginx\\nginx.exe -s quit')

import json
import os
import copy
import multiprocessing
import datetime
import time
import natsort
from typing import Union
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QSizeGrip, QGraphicsDropShadowEffect, \
    QTableWidgetItem, QLabel, QCheckBox, QHeaderView
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt

from widget.forms.form_main_designer import Ui_MainWindow
from widget.forms.form_profile import FormProfile
from widget.forms.form_devices import FormDevices
from widget.forms.form_configuration import FormConfiguration
from widget.forms.form_device_database_view import FormDeviceDBView
from widget.forms.form_stranger_table import FormStrangerTable
from widget.forms.messagebox import DepartmentMessageBox, WarningMessageBox, InformationMessageBox
import widget.models as models
from widget.management import DBManagement, DeviceManagement
from widget.database_visualization import DBVisualization
from widget.mqtt.subscribe_platform import SubscribePlatform
from widget.mqtt.publish_platform import PublishPlatform


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        start = time.time()
        super().__init__()
        self.setupUi(self)
        # APPLICATIONS
        self.start_nginx()
        # DATA
        self.app_path = os.path.dirname(os.getcwd())
        with open(f'{self.app_path}/widget/setting.json') as file:
            self.settings = json.load(file, strict=False)
        print(self.settings)
        self.device_management = DeviceManagement()
        self.device_management.find_host_info()
        self.device_management.port = 7777
        self.database_management = DBManagement()
        self.devices = self.database_management.get_devices()
        self.theme = self._get_theme('dark theme')
        self.number_device_profiles = 0
        self.last_page = False
        self.publish_platform = PublishPlatform(self.device_management.host, client_name='PP1')
        # SETTINGS
        # self.pie_current_day = DBVisualization()
        # self.pie_current_day.create_pie_chart_temperatures(title='Passage of people for the current day',
        #                                                    current_day=datetime.date.today().strftime('%Y/%m/%d'))
        # self.pie_current_all_time = DBVisualization(width=10, height=4)
        # self.pie_current_all_time.create_pie_chart_temperatures()
        # self.pie_current_all_time.figure.savefig(f'{self.app_path}/widget/data/temp/temp.png')
        # self.label_pie_number_person_all_time.setPixmap(
        #     QPixmap(QImage(f'{self.app_path}/{self.settings["paths"]["temp"]}/temp.png'))
        # )
        self.label_pie_number_person_all_time.setScaledContents(True)
        self.comboBox_profiles.addItem('All Profiles')
        self.radiobutton_time.setChecked(True)
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
        self.button_delete_device.clicked.connect(self._button_delete_device_clicked)
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
        self.button_create_pattern.clicked.connect(self._button_create_pattern_clicked)
        self.button_device_database_view.clicked.connect(self._button_device_database_view_clicked)
        self.table_profiles.horizontalHeader().sectionPressed.connect(self._checkbox_header_persons_pressed)
        self.table_departments.horizontalHeader().sectionPressed.connect(self._checkbox_header_departments_pressed)
        # PAGE STATISTIC
        self.button_search_statistics.clicked.connect(self._button_search_statistics_clicked)
        self.button_all_statistic.clicked.connect(self._button_all_statistic_clicked)
        self.button_report.clicked.connect(self._button_report_clicked)
        self.button_strangers_statistic.clicked.connect(self._button_stranger_statistics_clicked)
        self.dateTimeEdit_start.setDateTime(datetime.datetime.now().replace(hour=0, minute=0))
        self.dateTimeEdit_end.setDateTime(datetime.datetime.now().replace(hour=23, minute=59))
        # DATA
        if self.device_management.host is not None:
            self.subscribe_platform = SubscribePlatform()
            self.subscribe_platform.set_host_port(self.device_management.host, client_name='SP1')
            self.thread = QtCore.QThread()
            self.subscribe_platform.moveToThread(self.thread)
            self.subscribe_platform.statistic.connect(self._get_record)
            self.subscribe_platform.device.connect(self._update_device_info)
            self.subscribe_platform.profiles.connect(self._get_profiles_from_device)
            self.subscribe_platform.token.connect(self._get_token)
            self.thread.started.connect(self.subscribe_platform.run)
            self.thread.start()
        self._load_devices_info_to_table()
        print(time.time() - start)

    # EVENTS
    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_close_clicked(self, event):
        pass

    def _button_device_clicked(self, event):
        self._update_system_buttons(self.button_device)
        self.stackedWidget.setCurrentWidget(self.page_device)

    def _button_database_clicked(self, event):
        self._update_system_buttons(self.button_database)
        self.comboBox_databases.clear()
        self.comboBox_databases.addItems([
            device.id for device in self.devices if device.online
        ])
        self.stackedWidget.setCurrentWidget(self.page_database)

    def _button_statistic_clicked(self, event):
        self._update_system_buttons(self.button_statistic)
        self.stackedWidget.setCurrentWidget(self.page_statistic)

    def _button_settings_clicked(self, event):
        self._update_system_buttons(self.button_settings)
        self.stackedWidget.setCurrentWidget(self.page_settings)

    # EVENTS-DATABASE
    def _button_add_profile_clicked(self, event):
        form_profile = FormProfile()
        form_profile.exec_()
        if form_profile.dialog_result == 0:
            self.database_management.add_profiles(form_profile.profile)
            row_position = self.table_profiles.rowCount()
            self._add_update_profile_row(row_position, form_profile.profile)
            self.comboBox_profiles.addItem(form_profile.profile.name)
            self.table_profiles.resizeColumnsToContents()
            self.table_profiles.resizeRowsToContents()

    def _button_edit_profile_clicked(self, event):
        for row_position in range(self.table_profiles.rowCount()):
            if self.table_profiles.cellWidget(row_position, 0).isChecked():
                profile = self.database_management.get_profile(self.table_profiles.item(row_position, 1).text())
                form_profile = FormProfile(profile)
                form_profile.exec_()
                if form_profile.dialog_result == 0:
                    self.database_management.update_profile(profile.id, form_profile.profile)
                    self._add_update_profile_row(row_position, form_profile.profile)
                    self.comboBox_profiles.setItemText(row_position + 1, form_profile.profile.name)
        self.table_profiles.resizeColumnsToContents()
        self.table_profiles.resizeRowsToContents()

    def _button_delete_profile_clicked(self, event):
        messagebox = WarningMessageBox()
        messagebox.label_title.setText('Warning - Delete Profiles')
        messagebox.label_info.setText('Are you sure you want to delete profiles?')
        messagebox.exec_()
        if messagebox.dialog_result == 0:
            id_profiles = []
            for row_position in range(self.table_profiles.rowCount() - 1, -1, -1):
                if self.table_profiles.cellWidget(row_position, 0).isChecked():
                    id_profiles.append(self.table_profiles.item(row_position, 1).text())
                    self.table_profiles.removeRow(row_position)
                    self.comboBox_profiles.removeItem(row_position + 1)
            self.database_management.remove_profiles(*id_profiles)

    def _button_send_device_clicked(self, event):
        if self.comboBox_databases.currentText() == '':
            messagebox = InformationMessageBox()
            messagebox.setWindowTitle('Information')
            messagebox.label_title.setText('Information - Send to Device')
            messagebox.label_info.setText('No connected devices')
            messagebox.exec_()
        else:
            for dev in self.devices:
                if dev.id == self.comboBox_databases.currentText():
                    device = dev
                    break
            self.publish_platform.set_device(device.id, device.token)
            if not self.table_profiles.horizontalHeaderItem(0).checkState():
                profile_ids = [
                    self.table_profiles.item(row_position, 1).text()
                    for row_position in range(self.table_profiles.rowCount())
                    if self.table_profiles.cellWidget(row_position, 0).isChecked()
                ]
                if len(profile_ids) <= 0:
                    messagebox = InformationMessageBox()
                    messagebox.setWindowTitle('Information')
                    messagebox.label_title.setText('Information - Send to Device')
                    messagebox.label_info.setText(f'Choose who to add to the device'
                                                  f' {self.comboBox_databases.currentText()}.')
                    messagebox.exec_()
                else:
                    self.publish_platform.add_profiles_data(profile_ids)
            else:
                self.publish_platform.add_profiles_data()

    def _button_add_department_clicked(self, event):
        messagebox = DepartmentMessageBox()
        messagebox.exec_()
        if messagebox.dialog_result == 0:
            row_position = self.table_departments.rowCount()
            self.table_departments.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_departments.setCellWidget(row_position, 0, item)
            self.table_departments.setItem(row_position, 1, QTableWidgetItem(messagebox.department))
            self.database_management.add_departments(messagebox.department)

    def _button_delete_department_clicked(self, event):
        messagebox = WarningMessageBox()
        messagebox.label_title.setText('Warning - Department')
        messagebox.label_info.setText('Are you sure you want to delete departments?')
        messagebox.exec_()
        if messagebox.dialog_result == 0:
            remove_departments = []
            for row_position in range(self.table_departments.rowCount() - 1, -1, -1):
                if self.table_departments.cellWidget(row_position, 0).isChecked():
                    remove_departments.append(self.table_departments.item(row_position, 1).text())
                    self.table_departments.removeRow(row_position)
            self.database_management.remove_departments(*remove_departments)

    def _button_add_profiles_group_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Profiles Group', '', 'CSV File (*.csv)')
        if filename:
            self.database_management.add_profiles_from_pattern(filename)
            self._load_profiles_to_table()

    def _button_add_profile_images_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Profile Images', '', 'ZIP File (*.zip)')
        if filename:
            self.database_management.add_profiles_from_images(filename)
            self._load_profiles_to_table()

    def _button_device_database_view_clicked(self, event):
        self.profile_ids = []
        self.last_page = False
        for device in self.devices:
            if device.id == self.comboBox_databases.currentText():
                self.publish_platform.set_device(device.id, device.token)
                self.publish_platform.query_profiles_data(-1)
                break

    def _button_create_pattern_clicked(self, event):
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Pattern', '', 'CSV File (*.csv)')
        if filename:
            self.database_management.create_profiles_pattern(filename)

    # EVENTS-DEVICE
    def _button_search_device_clicked(self, event):
        devices = self.database_management.get_devices()
        result = self.device_management.find_devices(binding_devices=devices)
        if result == -1:
            messagebox = InformationMessageBox()
            messagebox.label_info.setText('Ethernet is not connected')
            messagebox.setWindowTitle('Information')
            messagebox.exec_()
        elif result == 0 and len(self.device_management.devices) == 0:
            messagebox = InformationMessageBox()
            messagebox.label_info.setText('Device is not found')
            messagebox.setWindowTitle('Information')
            messagebox.exec_()
        else:
            self.form_devices = FormDevices(self.device_management.devices)
            self.form_devices.exec_()
            if self.form_devices.dialog_result == 0:
                self.device_management.devices = self.form_devices.devices
                for device in self.device_management.devices:
                    self.publish_platform.set_device(device.id)
                    self.publish_platform.bind_device()

    def _button_configure_device_clicked(self, event):
        for row_position, device in enumerate(self.devices):
            if self.table_devices.cellWidget(row_position, 0).isChecked() and device.online:
                form_configuration = FormConfiguration(device)
                form_configuration.exec_()
                if form_configuration.dialog_result == 0:
                    self.devices[row_position] = form_configuration.device
                    self.publish_platform.set_device(device.id, device.token)
                    self.publish_platform.update_remote_configuration(
                        volume=device.volume,
                        screen_brightness=device.brightness,
                        light_supplementary=device.light_supplementary
                    )
                    self.publish_platform.update_temperature_configuration(
                        temperature_check=device.temperature_check,
                        stranger_passage=device.stranger_passage,
                        mask_detection=device.mask_detection,
                        alarm_temperature=device.temperature_alarm,
                        temperature_compensation=device.temperature_compensation,
                        record_save_time=device.record_save_time,
                        save_record=device.record_save,
                        save_jpeg=device.save_jpeg
                    )

    def _button_delete_device_clicked(self, event):
        remove_devices = []
        remove_rows = []
        for row_position, device in enumerate(self.devices):
            if self.table_devices.cellWidget(row_position, 0).isChecked():
                if device.online:
                    messagebox = WarningMessageBox()
                    messagebox.setWindowTitle(device.id)
                    messagebox.label_title.setText(device.id)
                    messagebox.label_info.setText('Are you sure want to delete this device?')
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        self.publish_platform.set_device(device.id, device.token)
                        self.publish_platform.unbind_device()
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
                else:
                    messagebox = WarningMessageBox()
                    messagebox.setWindowTitle(device.id)
                    messagebox.label_title.setText(device.id)
                    messagebox.label_info.setText('This device is not connected.\n'
                                                  'If you delete device now, then you need'
                                                  ' to reset it to factory settings later\n'
                                                  'Are you sure want to delete this device?')
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
        for device in remove_devices:
            self.devices.remove(device)
        for remove_row in sorted(remove_rows, reverse=True):
            self.table_devices.removeRow(remove_row)

    # EVENTS-STATISTICS
    def _button_search_statistics_clicked(self, event):
        if self.comboBox_profiles.currentText() == 'All Profiles':
            identifier = None
        else:
            profile = self.database_management.get_profile_by_name(self.comboBox_profiles.currentText())
            identifier = profile.id
        if self.radiobutton_time.isChecked():
            low = self.dateTimeEdit_start.text()
            high = self.dateTimeEdit_end.text()
        elif self.radiobutton_temperature.isChecked():
            low = self.doubleSpinBox_min_temperature.value()
            high = self.doubleSpinBox_max_temperature.value()
        self._load_statistics_to_table(
            low=low,
            high=high,
            identifiers=identifier
        )
        start = time.time()
        process = multiprocessing.Process(
            target=MainForm._update_plots,
            args=(
                copy.copy(self.app_path),
            )
        )
        process.start()
        process.join()
        self.label_pie_number_person_all_time.setPixmap(
            QPixmap(
                QImage(f'{self.app_path}/{self.settings["paths"]["temp"]}/temp.png')
            )
        )
        print(time.time() - start)

    def _button_all_statistic_clicked(self, event):
        if self.comboBox_profiles.currentText() == 'All Profiles':
            identifier = None
        else:
            profile = self.database_management.get_profile_by_name(self.comboBox_profiles.currentText())
            identifier = profile.id
        self._load_statistics_to_table(identifiers=identifier)

    def _button_report_clicked(self, event):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'JSON File (*.json);')
        if filename:
            self.database_management.create_passage_report(filename)

    def _button_stranger_statistics_clicked(self, event):
        statistics = self.database_management.get_stranger_statistics()
        print(statistics)
        form_stranger_table = FormStrangerTable(statistics)
        form_stranger_table.exec_()

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
    @QtCore.pyqtSlot(dict)
    def _update_device_info(self, data):
        for row_position in range(self.table_devices.rowCount()):
            if self.table_devices.item(row_position, 3).text() == data['device_id']:
                self.devices[row_position].name = data['datas']['basic_parameters']['dev_name']
                item = QTableWidgetItem(data['datas']['basic_parameters']['dev_name'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 1, item)
                self.devices[row_position].model = data['datas']['version_info']['dev_model']
                item = QTableWidgetItem(data['datas']['version_info']['dev_model'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 2, item)
                item = QTableWidgetItem(data['device_id'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 3, item)
                self.devices[row_position].ip_address = data['datas']['network_cofnig']['ip_addr']
                item = QTableWidgetItem(data['datas']['network_cofnig']['ip_addr'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 5, item)
                item = QTableWidgetItem('online')
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 6, item)
                self.devices[row_position].online = True
                # REMOTE CONFIG
                self.devices[row_position].volume = data['datas']['remote_config']['volume_cur']
                self.devices[row_position].brightness = data['datas']['remote_config']['screen_brightness_cur']
                self.devices[row_position].light_supplementary = data['datas']['remote_config']['light_supplementary']
                # TEMPERATURE CONFIG
                self.devices[row_position].temperature_check = data['datas']['fun_param']['temp_dec_en']
                self.devices[row_position].stranger_passage = data['datas']['fun_param']['stranger_pass_en']
                self.devices[row_position].mask_detection = data['datas']['fun_param']['make_check_en']
                self.devices[row_position].temperature_alarm = data['datas']['fun_param']['alarm_temp']
                self.devices[row_position].temperature_compensation = data['datas']['fun_param']['temp_comp']
                self.devices[row_position].record_save_time = data['datas']['fun_param']['record_save_time']
                self.devices[row_position].record_save = data['datas']['fun_param']['save_record']
                self.devices[row_position].save_jpeg = data['datas']['fun_param']['save_jpeg']
                self.database_management.update_device(self.devices[row_position].id, self.devices[row_position])
                break

    @QtCore.pyqtSlot(str)
    def _get_token(self, token: str):
        token = token.split('_')
        device_id = token[0]
        token = token[1]
        for device in self.device_management.devices:
            if device_id == device.id:
                device.token = token
                device.online = True
                self.database_management.add_devices(device)
                self.devices.append(device)
                self.device_management.remove_device(device)
                self._add_device_row(device)
                self.publish_platform.set_device(device.id, device.token)
                self.publish_platform.get_device_info()

    def _load_devices_info_to_table(self):
        for device in self.devices:
            self._add_device_row(device)
            self.publish_platform.set_device(device.id, device.token)
            self.publish_platform.get_device_info()
        self.table_devices.resizeColumnToContents(0)
        self.table_devices.resizeColumnToContents(2)
        self.table_devices.resizeColumnToContents(6)
        self.table_devices.resizeRowsToContents()

    def _add_device_row(self, device: models.Device):
        row_position = self.table_devices.rowCount()
        print(row_position)
        self.table_devices.insertRow(row_position)
        item = QCheckBox()
        item.setCheckState(Qt.Unchecked)
        self.table_devices.setCellWidget(row_position, 0, item)
        item = QTableWidgetItem(device.name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 1, item)
        item = QTableWidgetItem(device.model)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 2, item)
        item = QTableWidgetItem(device.id)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 3, item)
        item = QTableWidgetItem(device.mac_address)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 4, item)
        item = QTableWidgetItem(device.ip_address)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 5, item)
        if device.online:
            state = 'online'
        else:
            state = 'not online'
        item = QTableWidgetItem(state)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 6, item)

    # DATABASE
    def _load_profiles_to_table(self):
        start = time.time()
        self.table_profiles.setRowCount(0)
        profiles = self.database_management.get_profiles()
        print(f'[DATABASE][PROFILES] {time.time() - start}')
        start = time.time()
        for row_position, profile in enumerate(profiles):
            self._add_update_profile_row(row_position, profile)
            self.comboBox_profiles.addItem(profile.name)
        self.table_profiles.resizeColumnsToContents()
        self.table_profiles.resizeRowsToContents()
        print(f'[VISUAL][PROFILES] {time.time() - start}')

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
        start = time.time()
        self.table_statistics.setRowCount(0)
        statistics = self.database_management.get_statistics(
            low=low,
            high=high,
            identifiers=identifiers,
            profile_name=True
        )
        print(f'[DATABASE][STATISTICS] {time.time() - start}')
        start = time.time()
        for row_position, statistic in enumerate(statistics):
            statistic, name = statistic
            self._add_statistic_row(row_position, statistic, name)
        # self.table_statistics.sortByColumn(2, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        # self.table_statistics.viewport().update()
        print(f'[VISUAL][STATISTICS] {time.time() - start}')

    def _add_statistic_row(self, row_position: int, statistic: models.Statistic, name: str):
        self.table_statistics.insertRow(row_position)
        self.table_statistics.setItem(row_position, 0, self._get_item_to_cell(statistic.id_profile))
        self.table_statistics.setItem(row_position, 1, QTableWidgetItem(name))
        item = QTableWidgetItem(str(statistic.time))
        if statistic.face is not None and os.path.exists(f'snapshot{statistic.face}'):
            item.setToolTip(f'<br><img src="snapshot{statistic.face}" width="240" height="426" alt="lorem"')
        else:
            item.setToolTip('No Image')
        self.table_statistics.setItem(row_position, 2, item)
        self.table_statistics.setItem(row_position, 3, self._get_item_to_cell(float(statistic.temperature)))
        self.table_statistics.setItem(row_position, 4, self._get_item_to_cell(float(statistic.similar)))

    def _add_update_profile_row(self, row_position: int, profile: models.Profile):
        if row_position > self.table_profiles.rowCount() - 1:
            self.table_profiles.insertRow(row_position)
        item = QCheckBox()
        item.setCheckState(Qt.Unchecked)
        self.table_profiles.setCellWidget(row_position, 0, item)
        self.table_profiles.setItem(row_position, 1, QTableWidgetItem(profile.id))
        self.table_profiles.setItem(row_position, 2, self._get_item_image(profile.face))
        self.table_profiles.setItem(row_position, 3, QTableWidgetItem(profile.name))
        self.table_profiles.setItem(row_position, 4, QTableWidgetItem(str(profile.name_department)))
        self.table_profiles.setItem(row_position, 5, QTableWidgetItem(str(profile.gender)))
        self.table_profiles.setItem(row_position, 6, QTableWidgetItem(str(profile.phone_number)))

    @QtCore.pyqtSlot(object)
    def _get_profiles_from_device(self, data):
        if isinstance(data, dict):
            self.number_device_profiles = data['total_num']
            number_pages = np.int(np.ceil(self.number_device_profiles / 100))
            print(number_pages)
            for page in range(number_pages):
                self.publish_platform.query_profiles_data(page)
            self.last_page = True
        elif isinstance(data, list):
            for profile in data:
                self.profile_ids.append(profile['user_id'])
            if self.last_page:
                profiles = [
                    models.Profile(identifier=profile_id,
                                   name='User')
                    for profile_id in self.profile_ids
                ]
                current_profiles = set(self.database_management.get_profiles(*self.profile_ids))
                profiles = set(profiles)
                remove_profiles = list(profiles - current_profiles)
                if len(remove_profiles) > 0:
                    self.publish_platform.remove_profiles_data(*[
                        profile.id
                        for profile in remove_profiles
                    ])
                current_profiles = natsort.natsorted(list(current_profiles), key=lambda x: x.id)
                form_device_db_view = FormDeviceDBView(list(current_profiles))
                form_device_db_view.label_title.setText(f'DB View - Device {self.comboBox_databases.currentText()}')
                form_device_db_view.exec_()
                if form_device_db_view.dialog_result == 0:
                    if len(form_device_db_view.remove_profile_ids) > 0:
                        self.publish_platform.remove_profiles_data(*form_device_db_view.remove_profile_ids)

    # STATISTIC
    @QtCore.pyqtSlot(object)
    def _get_record(self, statistic: models.Statistic):
        row_position = self.table_statistics.rowCount()
        self._add_statistic_row(row_position,
                                statistic,
                                self.database_management.get_profile_name(statistic.id_profile))

    # OTHERS
    def _update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_device.setStyleSheet(self.theme['system-button'])
        self.button_database.setStyleSheet(self.theme['system-button'])
        self.button_statistic.setStyleSheet(self.theme['system-button'])
        self.button_settings.setStyleSheet(self.theme['system-button'])
        button.setStyleSheet(self.theme['system-button'] +
                             "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")

    @staticmethod
    def _update_plots(app_path: str):
        db_visualisation = DBVisualization(width=10, height=4)
        db_visualisation.create_pie_chart_temperatures()
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/temp.png')

    def _get_item_image(self, path_image=str):
        item = QTableWidgetItem()
        if os.path.isfile(f'nginx/html{path_image}'):
            pixmap = QPixmap(QImage(f'nginx/html{path_image}'))
            image = f'<br><img src="nginx/html{path_image}" width="360" alt="lorem"'
        else:
            pixmap = QPixmap(QImage('data/resources/icons/user.png'))
            image = 'No Image'
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        item.setData(Qt.DecorationRole, pixmap)
        item.setToolTip(image)
        return item

    def _get_item_to_cell(self, value):
        item = QTableWidgetItem()
        item.setData(Qt.EditRole, value)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _set_header_column_icon(self, table: QtWidgets.QTableWidget, checked: bool):
        item = QtWidgets.QTableWidgetItem()
        icon = QtGui.QIcon()
        if checked:
            icon.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-check-circle.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setCheckState(Qt.Checked)
        else:
            icon.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-uncheck-circle.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setCheckState(Qt.Unchecked)
        item.setIcon(icon)
        table.setHorizontalHeaderItem(0, item)

    # NGINX
    def start_nginx(self):
        path = os.path.abspath('nginx')
        # print(path)
        # subprocess.run([f"{path}\\start", "nginx"])
        # os.system(f'{path}\\start nginx')
        print(path)
        self.p = QtCore.QProcess()
        self.p.setWorkingDirectory(f'{path}')
        self.p.start('nginx.exe')

    def quit_nginx(self):
        os.system('nginx\\nginx.exe -s quit')

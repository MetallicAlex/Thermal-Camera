import base64
import json
import os
import re
import multiprocessing
import datetime
import time
import copy
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from widget.forms.form_main_designer import Ui_MainWindow
from widget.forms.form_list_device import FormDeviceList
from widget.forms.messagebox import ExportMessageBox, WarningMessageBox, InformationMessageBox
from widget.forms.toggle_button import AnimatedToggle
import widget.models as models
from widget.management import DBManagement, DeviceManagement
from widget.database_visualization import DBVisualization
from widget.mqtt.subscribe_platform import SubscribePlatform
from widget.mqtt.publish_platform import PublishPlatform
from widget.setting import Setting
from widget.email_utils import send_email


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        start = time.time()
        super().__init__()
        self.setupUi(self)
        self._create_toggle_buttons()
        self.setWindowIcon(QtGui.QIcon('byAlex.png'))
        self.blur_effect = QtWidgets.QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.blur_effect.setEnabled(False)
        self.setGraphicsEffect(self.blur_effect)
        # self._hide_buttons_search_device()
        # APPLICATIONS
        # self.start_nginx()
        # DATA
        self.is_new_devices_table = False
        self.is_table_device_profiles_loaded = False
        self.selected_profile = None
        self.selected_department = None
        self.selected_name = None
        self.filter_params = {
            'start': None,
            'end': None,
            'min': self.doubleSpinBox_min_temperature.value(),
            'max': self.doubleSpinBox_max_temperature.value(),
            'name': None
        }
        self.app_path = os.path.dirname(os.getcwd())
        self.setting = Setting(f'{self.app_path}/widget/setting.json')
        self.translate_ui()
        self.device_management = DeviceManagement()
        self.device_management.find_host_info()
        self.device_management.port = 7777
        self.database_management = DBManagement()
        self.database_management.setting = self.setting
        self.devices = self.database_management.get_devices()
        self.number_device_profiles = 0
        self.last_page = False
        self.image_filename = None
        self.publish_platform = PublishPlatform(self.device_management.host, client_name='PP1')
        # SETTINGS
        if self.setting.data['lang'] == 'ru':
            self.comboBox_langs.setCurrentText('Русский')
        elif self.setting.data['lang'] == 'en':
            self.comboBox_langs.setCurrentText('English')
        self.lineEdit_sender.setText(self.setting.data['sender'])
        self.lineEdit_receiver.setText(self.setting.data['receiver'])
        self.lineEdit_subject.setText(self.setting.data['subject'])
        config = self.database_management.get_smtp_config(self.setting.data['sender'])
        if config:
            self.lineEdit_server.setText(config.host)
            self.lineEdit_login.setText(config.user)
            self.lineEdit_port.setText(str(config.port))
            self.lineEdit_password.setText(config.password)
            self.toggle_ehlo.setChecked(config.use_ehlo)
            self.toggle_tls.setChecked(config.use_tls)
            self.toggle_ssl.setChecked(config.use_ssl)
            self.config = config
        else:
            self.lineEdit_server.setText('')
            self.lineEdit_login.setText('')
            self.lineEdit_port.setText('')
            self.lineEdit_password.setText('')
            self.toggle_ehlo.setChecked(False)
            self.toggle_tls.setChecked(False)
            self.toggle_ssl.setChecked(False)
            self.config = None
        self.label_chart1.setScaledContents(True)
        self.label_chart2.setScaledContents(True)
        self.style_unpressed_button = self.button_control.styleSheet()
        departments = [
            department.name
            for department in self.database_management.get_departments()
        ]
        self.comboBox_department.addItems(['---', *departments])
        self.comboBox_gender.addItems(
            [
                self.setting.lang['gender']['unknown'],
                self.setting.lang['gender']['male'],
                self.setting.lang['gender']['female']
            ]
        )
        self.database_visualization = DBVisualization(lang=self.setting.lang['charts'], width=10, height=6)
        self.database_visualization.create_pie_chart_temperatures(
            title=self.setting.lang['charts']['pie_title1'],
            threshold=self.doubleSpinBox_alarm_temperature.value(),
            stat_time=(
                datetime.datetime.now().replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.datetime.now().replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        self.database_visualization.save(f'{self.app_path}/{self.setting.paths["temp"]}/pie_day.png')
        self.label_pie_number_person_day.setPixmap(
            QPixmap(
                QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_day.png')
            )
        )
        self.database_visualization.create_pie_chart_temperatures(
            title=self.setting.lang['charts']['pie_title2'],
            threshold=self.doubleSpinBox_alarm_temperature.value()
        )
        self.database_visualization.save(f'{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png')
        self.label_pie_number_person_all_time.setPixmap(
            QPixmap(
                QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png')
            )
        )
        self.label_pie_number_person_day.setToolTip(
            f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/pie_day.png"'
        )
        self.label_pie_number_person_all_time.setToolTip(
            f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png"'
        )
        self.label_pie_number_person_day.setScaledContents(True)
        self.label_pie_number_person_all_time.setScaledContents(True)
        self.dateTimeEdit_start.setDateTime(datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0))
        self.dateTimeEdit_end.setDateTime(datetime.datetime.now().replace(hour=23, minute=59, second=59))
        self.filter_params['start'] = self.dateTimeEdit_start.text()
        self.filter_params['end'] = self.dateTimeEdit_end.text()
        self._load_profiles_to_table()
        self._load_departments_to_table()
        self._load_statistics_to_table(
            stat_time=(self.dateTimeEdit_start.text(), self.dateTimeEdit_end.text())
        )
        self._load_statistics_to_control(
            stat_time=(
                datetime.datetime.now().replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.datetime.now().replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        self.stackedWidget.setCurrentWidget(self.page_control)
        self._update_system_buttons(self.button_control)
        # SYSTEM BUTTONS, HEADER FRAME AND SIZEGRIP
        self.button_close.clicked.connect(self._button_close_clicked)
        self.button_minimize.clicked.connect(lambda: self.showMinimized())
        self.frame_header.mouseMoveEvent = self._frame_header_move_window
        self.frame_header.mousePressEvent = self._frame_header_mouse_press
        # MENU BUTTONS
        self.button_control.clicked.connect(self._button_control_clicked)
        self.button_device.clicked.connect(self._button_device_clicked)
        self.button_database.clicked.connect(self._button_database_clicked)
        self.button_statistic.clicked.connect(self._button_statistic_clicked)
        self.button_settings.clicked.connect(self._button_settings_clicked)
        # PAGE DEVICE
        self.button_update_device_info.clicked.connect(self._button_update_device_info_clicked)
        self.button_configure_device.clicked.connect(self._button_configure_device_clicked)
        self.button_delete_device.clicked.connect(self._button_delete_device_clicked)
        self.button_add_devices.clicked.connect(self._button_add_new_device_clicked)
        self.table_devices.itemSelectionChanged.connect(self._device_selected_row)
        self.table_devices.horizontalHeader().sectionPressed.connect(self._checkbox_header_devices_pressed)
        self.horizontalSlider_volume.valueChanged.connect(self._horizontal_slider_volume_value_changed)
        self.horizontalSlider_brightness.valueChanged.connect(self._horizontal_slider_brightness_value_changed)
        # PAGE DATABASE
        self.button_add_profile.clicked.connect(self._button_add_profile_clicked)
        self.button_edit_profile.clicked.connect(self._button_edit_profile_clicked)
        self.button_delete_profile.clicked.connect(self._button_delete_profile_clicked)
        self.button_load_photo.clicked.connect(self._button_load_photo_clicked)
        self.button_send_device.clicked.connect(self._button_send_device_clicked)
        self.button_example_data.clicked.connect(self._button_create_pattern_clicked)
        self.button_export_profiles_data.clicked.connect(self._button_export_profiles_data)
        self.button_import_data.clicked.connect(self._button_import_profiles_data_clicked)
        self.button_import_photos.clicked.connect(self._button_import_photos_clicked)
        self.button_add_department.clicked.connect(self._button_add_department_clicked)
        self.button_edit_department.clicked.connect(self._button_edit_department_clicked)
        self.button_delete_department.clicked.connect(self._button_delete_department_clicked)
        self.button_device_database_view.clicked.connect(self._button_device_database_view_clicked)
        self.button_delete_device_profiles.clicked.connect(self._button_delete_device_profiles)
        self.table_profiles.horizontalHeader().sectionPressed.connect(self._checkbox_header_profiles_pressed)
        self.table_profiles.itemSelectionChanged.connect(self._profile_selected_row)
        self.table_device_profiles.horizontalHeader().sectionPressed.connect(
            self._checkbox_header_device_profiles_pressed
        )
        self.table_departments.horizontalHeader().sectionPressed.connect(self._checkbox_header_departments_pressed)
        self.table_departments.itemSelectionChanged.connect(self._department_selected_row)
        # PAGE STATISTIC
        self.button_statistics_filter.clicked.connect(self._button_statistics_filter_clicked)
        self.button_export_statistics_data.clicked.connect(self._button_export_statistics_data_clicked)
        self.table_statistics.itemSelectionChanged.connect(self._statistic_selected_row)
        # PAGE SETTINGS
        self.button_apply_setting.clicked.connect(self._button_apply_setting_clicked)
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
            self.subscribe_platform.information.connect(self._get_update_device_information)
            self.subscribe_platform.profiles_loading.connect(self._get_loading_photos_result)
            self.subscribe_platform.removed_profiles.connect(self._get_remove_profiles_information)
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
        self.thread.quit()
        self.close()

    def _horizontal_slider_volume_value_changed(self):
        self.label_volume.setText(f'{self.setting.lang["volume"]}: {self.horizontalSlider_volume.value()}')

    def _horizontal_slider_brightness_value_changed(self):
        self.label_brightness.setText(f'{self.setting.lang["brightness"]}: {self.horizontalSlider_brightness.value()}')

    def _button_control_clicked(self, event):
        self._update_system_buttons(self.button_control)
        self.stackedWidget.setCurrentWidget(self.page_control)

    def _button_device_clicked(self, event):
        self._update_system_buttons(self.button_device)
        self.stackedWidget.setCurrentWidget(self.page_device)

    def _button_database_clicked(self, event):
        self._update_system_buttons(self.button_database)
        self.comboBox_databases.clear()
        devices = [device.serial_number for device in self.devices if device.online]
        self.comboBox_databases.addItems(devices)
        self.stackedWidget.setCurrentWidget(self.page_database)

    def _button_statistic_clicked(self, event):
        self._update_system_buttons(self.button_statistic)
        self.stackedWidget.setCurrentWidget(self.page_statistic)

    def _button_settings_clicked(self, event):
        self._update_system_buttons(self.button_settings)
        self.stackedWidget.setCurrentWidget(self.page_settings)

    # EVENTS-DATABASE
    def _profile_selected_row(self):
        self.image_filename = None
        row_position = self.table_profiles.currentIndex().row()
        if row_position > -1:
            if self.table_profiles.item(row_position, 1).text() == '---':
                self.lineEdit_personnel_number.setText('')
            else:
                self.lineEdit_personnel_number.setText(self.table_profiles.item(row_position, 1).text())
            if self.table_profiles.item(row_position, 2).text() == '---':
                self.lineEdit_profile_name.setText('')
            else:
                self.lineEdit_profile_name.setText(self.table_profiles.item(row_position, 2).text())
            self.label_show_photo.setToolTip(self.table_profiles.item(row_position, 3).toolTip())
            if self.table_profiles.item(row_position, 5).text() == '---':
                self.lineEdit_passport.setText('')
            else:
                self.lineEdit_passport.setText(self.table_profiles.item(row_position, 5).text())
            if self.table_profiles.item(row_position, 6).text() == '---':
                self.comboBox_department.setCurrentText('---')
            else:
                self.comboBox_department.setCurrentText(self.table_profiles.item(row_position, 6).text())
            if self.table_profiles.item(row_position, 7).text()[0] \
                    == self.setting.lang['table_profiles']['unknown'][0]:
                self.comboBox_gender.setCurrentIndex(0)
            elif self.table_profiles.item(row_position, 7).text()[0] \
                    == self.setting.lang['table_profiles']['male'][0]:
                self.comboBox_gender.setCurrentIndex(1)
            elif self.table_profiles.item(row_position, 7).text()[0] \
                    == self.setting.lang['table_profiles']['female'][0]:
                self.comboBox_gender.setCurrentIndex(2)
            if self.table_profiles.item(row_position, 8).text() == '---':
                self.plainTextEdit_information.setPlainText('')
            else:
                self.plainTextEdit_information.setPlainText(self.table_profiles.item(row_position, 8).text())
            if self.table_profiles.item(row_position, 4).text() == self.setting.lang['employee']:
                self.selected_profile = self.database_management.get_profile(
                    personnel_number=self.table_profiles.item(row_position, 1).text()
                )
                self.toggle_visitor.setChecked(False)
            else:
                self.selected_profile = self.database_management.get_profile(
                    passport=self.table_profiles.item(row_position, 5).text()
                )
                self.toggle_visitor.setChecked(True)
        else:
            self.lineEdit_personnel_number.setText('')
            self.lineEdit_profile_name.setText('')
            self.lineEdit_passport.setText('')
            self.comboBox_department.setCurrentText('---')
            self.comboBox_gender.setCurrentIndex(0)
            self.toggle_visitor.setChecked(False)
            self.plainTextEdit_information.setPlainText('')

    def _button_add_profile_clicked(self, event):
        text = ''
        personnel_number = None
        profile_name = None
        passport = None
        image = None
        department = None
        information = None
        if not self.toggle_visitor.isChecked():
            if self.database_management.is_personnel_number_duplicate(self.lineEdit_personnel_number.text()):
                text = self.setting.lang['message']['add_profile']['pers_number_exist']
            elif self.lineEdit_personnel_number.text() == '':
                text = self.setting.lang['message']['add_profile']['pers_number_not']
            else:
                personnel_number = self.lineEdit_personnel_number.text()
        else:
            if self.lineEdit_passport.text() == '':
                text = self.setting.lang['message']['add_profile']['passport_not']
        if self.lineEdit_passport.text() != '' \
                and self.database_management.is_passport_duplicate(self.lineEdit_passport.text()):
            text += self.setting.lang['message']['add_profile']['passport_exist']
        else:
            passport = self.lineEdit_passport.text()
        if self.lineEdit_profile_name.text() == '':
            text += self.setting.lang['message']['add_profile']['name_not']
        else:
            profile_name = self.lineEdit_profile_name.text()
        if self.comboBox_department.currentText() != '---':
            department = self.comboBox_department.currentText()
        gender = self.comboBox_gender.currentIndex()
        if self.plainTextEdit_information.toPlainText() != '':
            information = self.plainTextEdit_information.toPlainText()
        if text == '':
            if self.image_filename:
                rng = np.random.default_rng()
                image = '/static/images/' + np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                while os.path.exists(f'{self.app_path}/{self.setting.paths["nginx"]}/html{image}'):
                    image = '/static/images/' + np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                pixmap = QPixmap(
                    QImage(self.image_filename)
                )
                pixmap.save(f'{self.app_path}/{self.setting.paths["nginx"]}/html{image}', 'jpg')
            profile = models.Profile()
            profile.visitor = self.toggle_visitor.isChecked()
            profile.name = profile_name
            profile.gender = gender
            if personnel_number:
                profile.personnel_number = personnel_number
            if passport:
                profile.passport = passport
            if image:
                profile.face = image
            if department:
                profile.id_department = self.database_management.get_department_by_name(department).id
            if information:
                profile.information = information
            self.database_management.add_profiles(profile)
            self._add_update_profile_row(self.table_profiles.rowCount(), profile)
            self.table_profiles.resizeRowsToContents()
            self.table_profiles.resizeColumnToContents(1)
            self.table_profiles.resizeColumnToContents(2)
            self.table_profiles.resizeColumnToContents(3)
            self.table_profiles.resizeColumnToContents(4)
            self.table_profiles.resizeColumnToContents(5)
            self.table_profiles.resizeColumnToContents(6)
            self.table_profiles.resizeColumnToContents(7)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['add_profile']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_edit_profile_clicked(self, event):
        personnel_number = None
        profile_name = None
        passport = None
        image = None
        department = None
        information = None
        text = ''
        if self.selected_profile is not None:
            if not self.toggle_visitor.isChecked():
                if self.database_management.is_personnel_number_duplicate(self.lineEdit_personnel_number.text()) \
                        and self.selected_profile.personnel_number != self.lineEdit_personnel_number.text():
                    text = self.setting.lang['message']['edit_profile']['pers_number_exist']
                elif self.lineEdit_personnel_number.text() == '':
                    text = self.setting.lang['message']['edit_profile']['pers_number_not']
                else:
                    personnel_number = self.lineEdit_personnel_number.text()
            else:
                if self.lineEdit_passport.text() == '':
                    text = self.setting.lang['message']['edit_profile']['passport_not']
            if self.lineEdit_passport.text() != '' \
                    and self.database_management.is_passport_duplicate(self.lineEdit_passport.text()) \
                    and self.selected_profile.passport != self.lineEdit_passport.text():
                text += self.setting.lang['message']['edit_profile']['passport_exist']
            elif self.lineEdit_passport.text() != '':
                passport = self.lineEdit_passport.text()
            if self.lineEdit_profile_name.text() == '':
                text += self.setting.lang['message']['edit_profile']['name_not']
            else:
                profile_name = self.lineEdit_profile_name.text()
            if self.comboBox_department.currentText() != '---':
                department = self.comboBox_department.currentText()
            gender = self.comboBox_gender.currentIndex()
            if self.plainTextEdit_information.toPlainText() != '':
                information = self.plainTextEdit_information.toPlainText()
        else:
            text = self.setting.lang['message']['edit_profile']['profile_not']
        if text == '':
            if self.image_filename:
                if self.selected_profile.face:
                    image = self.selected_profile.face
                else:
                    rng = np.random.default_rng()
                    image = '/static/images/' + np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                    while os.path.exists(f'{self.app_path}/{self.setting.paths["nginx"]}/html{image}'):
                        image = '/static/images/'\
                                + np.array2string(rng.integers(10, size=16), separator='')[1:-1] + '.jpg'
                pixmap = QPixmap(
                    QImage(self.image_filename)
                )
                pixmap.save(f'{self.app_path}/{self.setting.paths["nginx"]}/html{image}', 'jpg')
            self.selected_profile.name = profile_name
            self.selected_profile.gender = gender
            self.selected_profile.visitor = self.toggle_visitor.isChecked()
            self.selected_profile.personnel_number = personnel_number
            self.selected_profile.passport = passport
            if image:
                self.selected_profile.face = image
            if department:
                self.selected_profile.id_department = self.database_management.get_department_by_name(department).id
            else:
                self.selected_profile.id_department = department
            self.selected_profile.information = information
            self.database_management.update_profile(self.selected_profile.id, self.selected_profile)
            self._add_update_profile_row(self.table_profiles.selectedIndexes()[0].row(), self.selected_profile)
            self.table_profiles.resizeRowsToContents()
            self.table_profiles.resizeColumnToContents(1)
            self.table_profiles.resizeColumnToContents(2)
            self.table_profiles.resizeColumnToContents(3)
            self.table_profiles.resizeColumnToContents(4)
            self.table_profiles.resizeColumnToContents(5)
            self.table_profiles.resizeColumnToContents(6)
            self.table_profiles.resizeColumnToContents(7)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['edit_profile']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_profile_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = WarningMessageBox(self.setting.lang['warning'])
        messagebox.label_title.setText(self.setting.lang['message']['delete_profile']['title'])
        messagebox.label_info.setText(self.setting.lang['message']['delete_profile']['info'])
        messagebox.exec_()
        self.blur_effect.setEnabled(False)
        if messagebox.dialog_result == 0:
            profiles = self.database_management.get_profiles()
            id_profiles = []
            for row_position in range(self.table_profiles.rowCount() - 1, -1, -1):
                if self.table_profiles.cellWidget(row_position, 0).isChecked():
                    id_profiles.append(profiles[row_position].id)
                    self.table_profiles.removeRow(row_position)
            if len(id_profiles) > 0:
                self.database_management.remove_profiles(*id_profiles)

    def _button_load_photo_clicked(self, event):
        self.image_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, self.setting.lang['dialog']['load_photo'], '',
            'Image File (*.bmp | *.jpg | *.jpeg | *.jfif | *.png);;'
        )
        if self.image_filename:
            self.label_show_photo.setToolTip(f'<br><img src="{self.image_filename}" width="360" alt="lorem"')

    def _button_send_device_clicked(self, event):
        devices = [
            device
            for device in self.devices
            if device.online
        ]
        profiles = self.database_management.get_profiles()
        profile_identifiers = [
            profiles[row_position].id
            for row_position in range(self.table_profiles.rowCount())
            if self.table_profiles.cellWidget(row_position, 0).isChecked()
        ]
        if self.table_profiles.horizontalHeaderItem(0).checkState() == Qt.Unchecked and len(profile_identifiers) <= 0:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['send_profiles']['title'])
            messagebox.label_info.setText(self.setting.lang['message']['send_profiles']['profile_not'])
            messagebox.exec_()
            self.blur_effect.setEnabled(False)
        elif len(devices) > 0:
            self.blur_effect.setEnabled(True)
            form_device_list = FormDeviceList(devices, self.setting.lang['device_list'])
            form_device_list.exec_()
            self.blur_effect.setEnabled(False)
            if form_device_list.dialog_result == 0:
                for device in form_device_list.devices:
                    self.publish_platform.set_device(device.serial_number, device.token)
                    self.publish_platform.add_profiles_data(profile_identifiers)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['send_profiles']['title'])
            messagebox.label_info.setText(self.setting.lang['message']['send_profiles']['device_not'])
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_create_pattern_clicked(self, event):
        filename, _ = QFileDialog.getSaveFileName(self, self.setting.lang['dialog']['example_data'],
                                                  '', 'CSV File (*.csv)')
        if filename:
            self.database_management.create_profiles_pattern(filename)

    def _button_export_profiles_data(self, event):
        filename, _ = QFileDialog.getSaveFileName(self, self.setting.lang['dialog']['export_profiles_data'], '',
                                                  'JSON File (*.json);;'
                                                  'CSV File (*.csv)'
                                                  )
        if filename:
            self.database_management.export_profiles_data(filename)

    def _button_import_profiles_data_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, self.setting.lang['dialog']['import_profiles_data'], '',
                                                  'CSV File (*.csv)')
        if filename:
            self.database_management.import_profiles_data(filename)
            self._load_profiles_to_table()
            self._load_departments_to_table()
            self.comboBox_department.clear()
            departments = [
                department.name
                for department in self.database_management.get_departments()
            ]
            self.comboBox_department.addItems(['---', *departments])

    def _button_import_photos_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, self.setting.lang['dialog']['import_photos'],
                                                  '', 'ZIP File (*.zip)')
        if filename:
            self.database_management.import_photos(filename)
            self._load_profiles_to_table()

    def _department_selected_row(self):
        row_position = self.table_departments.currentIndex().row()
        if row_position > -1:
            self.selected_department = self.database_management.get_department_by_name(
                self.table_departments.item(row_position, 1).text()
            )
            self.lineEdit_department_name.setText(self.selected_department.name)
            self.lineEdit_department_location.setText(self.selected_department.location)
        else:
            self.lineEdit_department_name.setText('')
            self.lineEdit_department_location.setText('')

    def _button_add_department_clicked(self, event):
        text = ''
        if self.lineEdit_department_name.text() != '':
            if not self.database_management.is_department_duplicate(self.lineEdit_department_name.text()):
                department = models.Department()
                department.name = self.lineEdit_department_name.text()
                if self.lineEdit_department_location.text() != '':
                    department.location = self.lineEdit_department_location.text()
            else:
                text = self.setting.lang['message']['add_department']['name_exist']
        else:
            text = self.setting.lang['message']['add_department']['name_not']
        if text == '':
            self.database_management.add_departments(department)
            self._add_update_department_row(self.table_departments.rowCount(), department)
            self.comboBox_department.addItem(department.name)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['add_department']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_edit_department_clicked(self, event):
        text = ''
        if self.selected_department is not None:
            name = self.selected_department.name
            if self.lineEdit_department_name.text() != '':
                self.selected_department.name = self.lineEdit_department_name.text()
            else:
                self.selected_department.name = None
            if self.lineEdit_department_location.text() != '':
                self.selected_department.location = self.lineEdit_department_location.text()
            else:
                self.selected_department.location = None
        else:
            text = self.setting.lang['message']['edit_department']['department_not']
        if text == '':
            self.database_management.update_department(self.selected_department.id, self.selected_department)
            self._add_update_department_row(self.table_departments.selectedIndexes()[0].row(), self.selected_department)
            self.comboBox_department.setItemText(
                self.table_departments.selectedIndexes()[0].row() + 1,
                self.selected_department.name
            )
            for row in range(self.table_profiles.rowCount()):
                if self.table_profiles.item(row, 6).text() == name:
                    item = QTableWidgetItem(self.selected_department.name)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table_profiles.setItem(row, 6, item)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['edit_department']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_department_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = WarningMessageBox(self.setting.lang['warning'])
        messagebox.label_title.setText(self.setting.lang['message']['delete_department']['title'])
        messagebox.label_info.setText(self.setting.lang['message']['delete_department']['info'])
        messagebox.exec_()
        if messagebox.dialog_result == 0:
            departments = self.database_management.get_departments()
            id_departments = []
            for row_position in range(self.table_departments.rowCount() - 1, -1, -1):
                if self.table_departments.cellWidget(row_position, 0).isChecked():
                    id_departments.append(departments[row_position].id)
                    self.table_departments.removeRow(row_position)
                    self.comboBox_department.removeItem(row_position + 1)
                    for row in range(self.table_profiles.rowCount()):
                        if self.table_profiles.item(row, 6).text() == departments[row_position].name:
                            item = QTableWidgetItem('---')
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table_profiles.setItem(row, 6, item)
            if len(id_departments) > 0:
                self.database_management.remove_departments(*id_departments)
        self.blur_effect.setEnabled(False)

    def _button_device_database_view_clicked(self, event):
        if self.comboBox_databases.currentText() != '':
            for device in self.devices:
                if device.serial_number == self.comboBox_databases.currentText():
                    self.publish_platform.set_device(device.id, device.token)
                    self.publish_platform.query_profiles_data(-1)
                    break
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['db_device_view']['title'])
            messagebox.label_info.setText(self.setting.lang['message']['db_device_view']['info'])
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_device_profiles(self, event):
        text = ''
        if not self.is_table_device_profiles_loaded:
            text = self.setting.lang['message']['delete_profiles_device']['load_not']
        elif self.comboBox_databases.currentText() == '':
            text = self.setting.lang['message']['delete_profiles_device']['connect_not']
        if text == '':
            for device in self.devices:
                if device.serial_number == self.comboBox_databases.currentText():
                    self.blur_effect.setEnabled(True)
                    messagebox = WarningMessageBox(self.setting.lang['warning'])
                    messagebox.label_title.setText(self.setting.lang['message']['delete_profiles_device']['title'])
                    messagebox.label_info.setText(self.setting.lang['message']['delete_profiles_device']['info'])
                    messagebox.exec_()
                    self.blur_effect.setEnabled(False)
                    if messagebox.dialog_result == 0:
                        remove_profiles = []
                        for row_position in range(self.table_device_profiles.rowCount() - 1, -1, -1):
                            if self.table_device_profiles.cellWidget(row_position, 0).isChecked():
                                remove_profiles.append(str(self.profile_identifiers.pop(row_position)))
                                self.table_device_profiles.removeRow(row_position)
                        self.publish_platform.set_device(device.id, device.token)
                        self.publish_platform.remove_profiles_data(*remove_profiles)
                    break
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['delete_profiles_device']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    # EVENTS-DEVICE
    def _button_update_device_info_clicked(self, event):
        for device in self.devices:
            self.publish_platform.set_device(device.serial_number, device.token)
            self.publish_platform.get_device_info()

    def _button_add_new_device_clicked(self, event):
        text = ''
        if not re.search('\d+.\d+.\d+.\d+', self.lineEdit_ip_new_deivce.text()):
            text += self.setting.lang['message']['add_new_device']['not_ip']
        if self.lineEdit_new_device_password.text() == '':
            text += self.setting.lang['message']['add_new_device']['not_password']
        if self.lineEdit_new_device_port.text() == '':
            port = 7080
        else:
            port = int(self.lineEdit_new_device_port.text())
        if text == '':
            device = self.device_management.get_device_basic(
                self.lineEdit_ip_new_deivce.text(),
                base64.standard_b64encode(self.lineEdit_new_device_password.text().encode('utf-8')).decode('utf-8'),
                port
            )
            if device is None:
                text = self.setting.lang['message']['add_new_device']['not_correct']
            else:
                for device_from_db in self.devices:
                    if device_from_db.serial_number == device.serial_number:
                        text = self.setting.lang['message']['add_new_device']['connected']
                if text == '':
                    self.publish_platform.set_device(device.serial_number)
                    self.publish_platform.bind_device()
        if text != '':
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['add_new_device']['title'])
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_cancel_new_devices_clicked(self, event):
        self._hide_buttons_search_device()
        self.device_management.clear_devices()
        self.table_devices.setRowCount(0)
        self._load_devices_info_to_table()
        self.is_new_devices_table = False

    def _button_configure_device_clicked(self, event):
        rows = self.table_devices.selectedIndexes()
        if rows:
            row_position = rows[0].row()
            device = self.devices[row_position]
            self.device_configuration = {
                'row': row_position,
                'basic_config': {},
                'network_config': {},
                'remote_config': {},
                'temperature_config': {}
            }
            if device.online:
                self.publish_platform.set_device(device.serial_number, device.token)
                print(device.password)
                print(self.lineEdit_device_password.text())
                if device.name != self.lineEdit_device_name.text() \
                        or device.password != self.lineEdit_device_password.text():
                    self.device_configuration['basic_config']['name'] = copy.copy(device.name)
                    self.device_configuration['basic_config']['password'] = copy.copy(device.password)
                    device.name = self.lineEdit_device_name.text()
                    device.password = self.lineEdit_device_password.text()
                    self.table_devices.item(row_position, 2).setText(device.name)
                    self.publish_platform.update_basic_configuration(name=device.name, password=device.password)
                if device.volume != self.horizontalSlider_volume.value() \
                        or device.brightness != self.horizontalSlider_brightness.value() \
                        or device.light_supplementary != self.toggle_light.isChecked():
                    self.device_configuration['remote_config']['volume'] = copy.copy(device.volume)
                    self.device_configuration['remote_config']['brightness'] = copy.copy(device.brightness)
                    self.device_configuration['remote_config']['light'] = copy.copy(device.light_supplementary)
                    device.volume = self.horizontalSlider_volume.value()
                    device.brightness = self.horizontalSlider_brightness.value()
                    device.light_supplementary = self.toggle_light.isChecked()
                    self.publish_platform.update_remote_configuration(
                        volume=device.volume,
                        screen_brightness=device.brightness,
                        light_supplementary=device.light_supplementary
                    )
                if device.record_save_time != int(self.lineEdit_record_time.text()) \
                        or device.temperature_check != self.toggle_check_temperature.isChecked() \
                        or device.mask_detection != self.toggle_check_mask.isChecked() \
                        or device.stranger_passage != self.toggle_strangers_passage.isChecked() \
                        or device.save_jpeg != self.toggle_save_face.isChecked() \
                        or device.record_save != self.toggle_save_record.isChecked():
                    self.device_configuration['temperature_config']['check_temp'] = copy.copy(device.temperature_check)
                    self.device_configuration['temperature_config']['check_mask'] = copy.copy(device.mask_detection)
                    self.device_configuration['temperature_config']['stranger_passage'] = copy.copy(
                        device.stranger_passage)
                    self.device_configuration['temperature_config']['face_save'] = copy.copy(device.save_jpeg)
                    self.device_configuration['temperature_config']['record_save'] = copy.copy(device.record_save)
                    self.device_configuration['temperature_config']['record_time'] = copy.copy(device.record_save_time)
                    device.temperature_check = self.toggle_check_temperature.isChecked()
                    device.mask_detection = self.toggle_check_mask.isChecked()
                    device.stranger_passage = self.toggle_strangers_passage.isChecked()
                    device.save_jpeg = self.toggle_save_face.isChecked()
                    device.record_save = self.toggle_save_record.isChecked()
                    device.record_save_time = int(self.lineEdit_record_time.text())
                    device.temperature_alarm = self.doubleSpinBox_alarm_temperature.value()
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
                if device.ip_address != self.lineEdit_ip_address.text() \
                        or device.subnet_mask != self.lineEdit_subnet_mask.text() \
                        or device.gateway != self.lineEdit_gateway.text() \
                        or device.ddns1 != self.lineEdit_ddns1.text() \
                        or device.ddns2 != self.lineEdit_ddns2.text() \
                        or device.dhcp != self.toggle_dhcp.isChecked():
                    self.device_configuration['network_config']['ip_address'] = copy.copy(device.ip_address)
                    self.device_configuration['network_config']['subnet_mask'] = copy.copy(device.subnet_mask)
                    self.device_configuration['network_config']['gateway'] = copy.copy(device.gateway)
                    self.device_configuration['network_config']['ddns1'] = copy.copy(device.ddns1)
                    self.device_configuration['network_config']['ddns2'] = copy.copy(device.ddns2)
                    self.device_configuration['network_config']['dhcp'] = copy.copy(device.dhcp)
                    device.ip_address = self.lineEdit_ip_address.text()
                    device.subnet_mask = self.lineEdit_subnet_mask.text()
                    device.gateway = self.lineEdit_gateway.text()
                    device.ddns1 = self.lineEdit_ddns1.text()
                    device.ddns2 = self.lineEdit_ddns2.text()
                    device.dhcp = self.toggle_dhcp.isChecked()
                    self.publish_platform.update_network_configuration(
                        ip_address=device.ip_address,
                        gateway=device.gateway,
                        net_mask=device.subnet_mask,
                        DDNS1=device.ddns1,
                        DDNS2=device.ddns2,
                        DHCP=device.dhcp
                    )
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText(self.setting.lang['message']['configure_device']['title'])
            messagebox.label_info.setText(self.setting.lang['message']['configure_device']['info'])
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_device_clicked(self, event):
        remove_devices = []
        remove_rows = []
        self.blur_effect.setEnabled(True)
        for row_position, device in enumerate(self.devices):
            if self.table_devices.cellWidget(row_position, 0).isChecked():
                messagebox = WarningMessageBox(self.setting.lang['warning'])
                messagebox.setWindowTitle(f'{self.setting.lang["message"]["delete_device"]["delete"]}'
                                          f' {device.serial_number}: {device.ip_address}')
                messagebox.label_title.setText(f'{self.setting.lang["message"]["delete_device"]["delete"]}'
                                               f' {device.serial_number}: {device.ip_address}')
                if device.online:
                    text = self.setting.lang['message']['delete_device']['info_connect']
                    messagebox.label_info.setText(text)
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        self.publish_platform.set_device(device.id, device.token)
                        self.publish_platform.unbind_device()
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
                else:
                    text = self.setting.lang['message']['delete_device']['info_not_connect']
                    messagebox.label_info.setText(text)
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
        self.blur_effect.setEnabled(False)
        for device in remove_devices:
            self.devices.remove(device)
        for remove_row in sorted(remove_rows, reverse=True):
            self.table_devices.removeRow(remove_row)

    def _device_selected_row(self):
        if not self.is_new_devices_table:
            row_position = self.table_devices.currentIndex().row()
            if row_position > -1:
                self.lineEdit_device_name.setText(self.devices[row_position].name)
                self.lineEdit_ip_address.setText(self.devices[row_position].ip_address)
                if self.devices[row_position].online:
                    self.lineEdit_device_password.setText(self.devices[row_position].password)
                    self.lineEdit_subnet_mask.setText(self.devices[row_position].subnet_mask)
                    self.lineEdit_gateway.setText(self.devices[row_position].gateway)
                    self.lineEdit_ddns1.setText(self.devices[row_position].ddns1)
                    self.lineEdit_ddns2.setText(self.devices[row_position].ddns2)
                    self.toggle_dhcp.setChecked(self.devices[row_position].dhcp)
                    self.horizontalSlider_volume.setValue(self.devices[row_position].volume)
                    self.horizontalSlider_brightness.setValue(self.devices[row_position].brightness)
                    self.toggle_light.setChecked(self.devices[row_position].light_supplementary)
                    self.toggle_check_mask.setChecked(self.devices[row_position].mask_detection)
                    self.toggle_check_temperature.setChecked(self.devices[row_position].temperature_check)
                    self.toggle_strangers_passage.setChecked(self.devices[row_position].stranger_passage)
                    self.toggle_save_record.setChecked(self.devices[row_position].record_save)
                    self.toggle_save_face.setChecked(self.devices[row_position].save_jpeg)
                    self.lineEdit_record_time.setText(str(self.devices[row_position].record_save_time))
                else:
                    self.lineEdit_device_password.setText('')
                    self.lineEdit_subnet_mask.setText('')
                    self.lineEdit_gateway.setText('')
                    self.lineEdit_ddns1.setText('')
                    self.lineEdit_ddns2.setText('')
                    self.horizontalSlider_volume.setValue(0)
                    self.horizontalSlider_brightness.setValue(45)
                    self.toggle_light.setChecked(False)
                    self.toggle_check_mask.setChecked(False)
                    self.toggle_check_temperature.setChecked(False)
                    self.toggle_strangers_passage.setChecked(False)
                    self.toggle_save_record.setChecked(False)
                    self.toggle_save_face.setChecked(False)
                    self.lineEdit_record_time.setText('')
            else:
                self.lineEdit_device_name.setText('')
                self.lineEdit_ip_address.setText('')
                self.lineEdit_device_password.setText('')
                self.lineEdit_subnet_mask.setText('')
                self.lineEdit_gateway.setText('')
                self.lineEdit_ddns1.setText('')
                self.lineEdit_ddns2.setText('')
                self.horizontalSlider_volume.setValue(0)
                self.horizontalSlider_brightness.setValue(45)
                self.toggle_light.setChecked(False)
                self.toggle_check_mask.setChecked(False)
                self.toggle_check_temperature.setChecked(False)
                self.toggle_strangers_passage.setChecked(False)
                self.toggle_save_record.setChecked(False)
                self.toggle_save_face.setChecked(False)
                self.lineEdit_record_time.setText('')

    # EVENTS-STATISTICS
    def _button_statistics_filter_clicked(self, event):
        self.table_statistics.setSortingEnabled(False)
        self.selected_name = None
        self.filter_params['start'] = self.dateTimeEdit_start.text()
        self.filter_params['end'] = self.dateTimeEdit_end.text()
        self.filter_params['min'] = self.doubleSpinBox_min_temperature.value()
        self.filter_params['max'] = self.doubleSpinBox_max_temperature.value()
        if self.lineEdit_profile_name_filter.text() != '':
            self.filter_params['name'] = self.lineEdit_profile_name_filter.text()
        else:
            self.filter_params['name'] = None
        self._load_statistics_to_table(
            stat_time=(self.filter_params['start'], self.filter_params['end']),
            temperature=(self.filter_params['min'], self.filter_params['max']),
            name=self.filter_params['name']
        )
        self.table_statistics.setSortingEnabled(True)

    def _button_export_statistics_data_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = ExportMessageBox(self.setting.lang['export'])
        messagebox.label_title.setText(self.setting.lang['dialog']['export_stats_data'])
        messagebox.exec_()
        start = time.time()
        if messagebox.dialog_result != -1:
            process = multiprocessing.Process(
                target=MainForm._create_report,
                args=(messagebox.dialog_result, messagebox.filename, self.filter_params)
            )
            process.start()
            process.join()
        self.blur_effect.setEnabled(False)
        print(f'[EXPORT][STATISTIC] {time.time() - start}')

    def _statistic_selected_row(self):
        row_position = self.table_statistics.currentIndex().row()
        if row_position > -1:
            if self.selected_name != self.table_statistics.item(row_position, 2).text() \
                    and self.table_statistics.item(row_position, 2).text() != '---':
                identifier = self.database_management.get_statistic(
                    time=self.table_statistics.item(row_position, 0).text(),
                ).id_profile
                process = multiprocessing.Process(
                    target=MainForm._update_plots_statistics,
                    args=(
                        self.setting.lang['charts'],
                        self.app_path,
                        identifier,
                        (self.filter_params['start'], self.filter_params['end']),
                        (self.filter_params['min'], self.filter_params['max']),
                    )
                )
                process.start()
                process.join()
                self.label_chart1.setPixmap(
                    QPixmap(
                        QImage(f'{self.app_path}/{self.setting.paths["temp"]}/chart1.png')
                    )
                )
                self.label_chart2.setPixmap(
                    QPixmap(
                        QImage(f'{self.app_path}/{self.setting.paths["temp"]}/chart2.png')
                    )
                )
                self.label_chart1.setToolTip(
                    f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/chart1.png"'
                )
                self.label_chart2.setToolTip(
                    f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/chart2.png"'
                )
                self.selected_name = self.table_statistics.item(row_position, 2).text()

    def _checkbox_header_profiles_pressed(self, index):
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

    def _checkbox_header_device_profiles_pressed(self, index):
        if index == 0:
            list_checked_buttons = np.array([self.table_device_profiles.cellWidget(row_position, 0).isChecked()
                                             for row_position in range(self.table_device_profiles.rowCount())])
            if np.all(list_checked_buttons):
                for row_position in range(self.table_device_profiles.rowCount()):
                    self.table_device_profiles.cellWidget(row_position, 0).setCheckState(Qt.Unchecked)
                self._set_header_column_icon(self.table_device_profiles, False)
            else:
                for row_position in range(self.table_device_profiles.rowCount()):
                    self.table_device_profiles.cellWidget(row_position, 0).setCheckState(Qt.Checked)
                self._set_header_column_icon(self.table_device_profiles, True)

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
                item = QTableWidgetItem(self.setting.lang['table_devices']['online'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 1, item)
                self.devices[row_position].online = True
                self.devices[row_position].name = data['datas']['basic_parameters']['dev_name']
                item = QTableWidgetItem(data['datas']['basic_parameters']['dev_name'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 2, item)
                item = QTableWidgetItem(data['device_id'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 3, item)
                self.devices[row_position].type_device = data['datas']['version_info']['dev_model']
                item = QTableWidgetItem(data['datas']['version_info']['dev_model'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 4, item)
                self.devices[row_position].ip_address = data['datas']['network_cofnig']['ip_addr']
                item = QTableWidgetItem(data['datas']['network_cofnig']['ip_addr'])
                item.setTextAlignment(Qt.AlignCenter)
                self.table_devices.setItem(row_position, 8, item)
                # BASIC CONFIG
                self.devices[row_position].password = base64.standard_b64decode(
                    data['datas']['basic_parameters']['dev_pwd'].encode('utf-8')
                ).decode('utf-8')
                # NETWORK CONFIG
                self.devices[row_position].gateway = data['datas']['network_cofnig']['gateway']
                self.devices[row_position].subnet_mask = data['datas']['network_cofnig']['net_mask']
                self.devices[row_position].ddns1 = data['datas']['network_cofnig']['DDNS1']
                self.devices[row_position].ddns2 = data['datas']['network_cofnig']['DDNS2']
                self.devices[row_position].dhcp = data['datas']['network_cofnig']['DHCP']
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

    @QtCore.pyqtSlot(tuple)
    def _get_remove_profiles_information(self, result: tuple):
        self.blur_effect.setEnabled(True)
        messagebox = InformationMessageBox()
        messagebox.label_title.setText(f'{self.setting.lang["message"]["res_remove"]["title"]} {result[3]}')
        messagebox.label_info.setText(f'{self.setting.lang["message"]["res_remove"]["success"]}: {result[0]}\n'
                                      f'{self.setting.lang["message"]["res_remove"]["failure"]}: {result[1]}\n'
                                      f'{result[2]}')
        messagebox.exec_()
        self.blur_effect.setEnabled(False)

    @QtCore.pyqtSlot(tuple)
    def _get_update_device_information(self, text: tuple):
        self.blur_effect.setEnabled(True)
        messagebox = InformationMessageBox()
        device = self.devices[self.device_configuration['row']]
        if text[2] == -1:
            color = 'background-color: #B9400C;'
            information = self.setting.lang['message'][text[0]]['failure']
            if text[0] == 'basic_config':
                device.name = self.device_configuration['basic_config']['name']
                self.lineEdit_device_name.setText(self.device_configuration['basic_config']['name'])
                device.password = self.device_configuration['basic_config']['password']
                self.lineEdit_device_password.setText(self.device_configuration['basic_config']['password'])
            elif text[0] == 'remote_config':
                device.volume = self.device_configuration['remote_config']['volume']
                self.horizontalSlider_volume.setValue(self.device_configuration['remote_config']['volume'])
                device.brightness = self.device_configuration['remote_config']['brightness']
                self.horizontalSlider_brightness.setValue(self.device_configuration['remote_config']['brightness'])
                device.light_supplementary = self.device_configuration['remote_config']['light']
                self.toggle_light.setChecked(self.device_configuration['remote_config']['light'])
            elif text[0] == 'temperature_config':
                device.temperature_check = self.device_configuration['temperature_config']['check_temp']
                self.toggle_check_temperature.setChecked(self.device_configuration['temperature_config']['check_temp'])
                device.mask_detection = self.device_configuration['temperature_config']['check_mask']
                self.toggle_check_mask.setChecked(self.device_configuration['temperature_config']['check_mask'])
                device.stranger_passage = self.device_configuration['temperature_config']['stranger_passage']
                self.toggle_strangers_passage.setChecked(
                    self.device_configuration['temperature_config']['stranger_passage']
                )
                device.save_jpeg = self.device_configuration['temperature_config']['face_save']
                self.toggle_save_face.setChecked(self.device_configuration['temperature_config']['face_save'])
                device.record_save = self.device_configuration['temperature_config']['record_save']
                self.toggle_save_record.setChecked(self.device_configuration['temperature_config']['record_save'])
                device.record_save_time = self.device_configuration['temperature_config']['record_time']
                self.lineEdit_record_time.setText(str(self.device_configuration['temperature_config']['record_time']))
            elif text[0] == 'network_config':
                device.ip_address = self.device_configuration['network_config']['ip_address']
                self.lineEdit_ip_address.setText(self.device_configuration['network_config']['ip_address'])
                device.subnet_mask = self.device_configuration['network_config']['subnet_mask']
                self.lineEdit_subnet_mask.setText(self.device_configuration['network_config']['subnet_mask'])
                device.gateway = self.device_configuration['network_config']['gateway']
                self.lineEdit_gateway.setText(self.device_configuration['network_config']['gateway'])
                device.ddns1 = self.device_configuration['network_config']['ddns1']
                self.lineEdit_ddns1.setText(self.device_configuration['network_config']['ddns1'])
                device.ddns2 = self.device_configuration['network_config']['ddns2']
                self.lineEdit_ddns2.setText(self.device_configuration['network_config']['ddns2'])
                device.dhcp = self.device_configuration['network_config']['dhcp']
                self.toggle_dhcp.setChecked(self.device_configuration['network_config']['dhcp'])
        else:
            color = 'background-color: #0CB53B;'
            information = self.setting.lang['message'][text[0]]['success']
        messagebox.label_title.setText(f"{self.setting.lang['message'][text[0]]['title']}: {text[1]}")
        messagebox.label_info.setText(information)
        messagebox.frame_center.setStyleSheet(color)
        messagebox.frame_title.setStyleSheet(color)
        messagebox.exec_()
        self.blur_effect.setEnabled(False)

    @QtCore.pyqtSlot(tuple)
    def _get_token(self, token: tuple):
        device_id = token[0]
        token = token[1]
        for device in self.device_management.devices:
            if device_id == device.serial_number:
                device.token = token
                device.online = True
                self.database_management.add_devices(device)
                self.devices.append(device)
                self.device_management.remove_device(device)
                self._add_device_row(device)
                self.publish_platform.set_device(device.serial_number, device.token)
                self.publish_platform.get_device_info()

    def _load_devices_info_to_table(self):
        for device in self.devices:
            self._add_device_row(device)
            self.publish_platform.set_device(device.serial_number, device.token)
            self.publish_platform.get_device_info()
        self.table_devices.resizeColumnToContents(0)
        self.table_devices.resizeColumnToContents(1)
        self.table_devices.resizeColumnToContents(2)
        self.table_devices.resizeColumnToContents(3)
        self.table_devices.resizeColumnToContents(4)
        self.table_devices.resizeColumnToContents(5)
        self.table_devices.resizeColumnToContents(6)
        self.table_devices.resizeColumnToContents(7)
        self.table_devices.resizeRowsToContents()

    def _add_device_row(self, device: models.Device):
        row_position = self.table_devices.rowCount()
        self.table_devices.insertRow(row_position)
        item = QCheckBox()
        item.setStyleSheet('background-color: #91D1EE;')
        item.setCheckState(Qt.Unchecked)
        self.table_devices.setCellWidget(row_position, 0, item)
        if device.online:
            state = self.setting.lang['table_devices']['online']
        else:
            state = self.setting.lang['table_devices']['offline']
        item = QTableWidgetItem(state)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 1, item)
        name = device.name
        if name == '' or name is None:
            name = '---'
        item = QTableWidgetItem(name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 2, item)
        serial_number = device.serial_number
        if serial_number == '' or serial_number is None:
            serial_number = '---'
        item = QTableWidgetItem(serial_number)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 3, item)
        device_type = device.device_type
        if device_type == '' or device_type is None:
            device_type = '---'
        item = QTableWidgetItem(device_type)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 4, item)
        model = device.model
        if model == '' or model is None:
            model = '---'
        item = QTableWidgetItem(model)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 5, item)
        version = device.firmware_version
        if version == '' or version is None:
            version = '---'
        item = QTableWidgetItem(version)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 6, item)
        item = QTableWidgetItem(device.mac_address)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 7, item)
        item = QTableWidgetItem(device.ip_address)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 8, item)

    # DATABASE
    def _load_profiles_to_table(self):
        start = time.time()
        self.table_profiles.setRowCount(0)
        profiles = self.database_management.get_profiles()
        print(f'[DATABASE][PROFILES] {time.time() - start}')
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(len(profiles))
        start = time.time()
        for row_position, profile in enumerate(profiles):
            self._add_update_profile_row(row_position, profile)
            self.progressBar.setValue(self.progressBar.value() + 1)
        self.table_profiles.resizeColumnToContents(0)
        self.table_profiles.resizeColumnToContents(1)
        self.table_profiles.resizeColumnToContents(2)
        self.table_profiles.resizeColumnToContents(3)
        self.table_profiles.resizeColumnToContents(4)
        self.table_profiles.resizeColumnToContents(5)
        self.table_profiles.resizeColumnToContents(6)
        self.table_profiles.resizeColumnToContents(7)
        self.table_profiles.resizeRowsToContents()
        print(f'[VISUAL][PROFILES] {time.time() - start}')

    def _load_departments_to_table(self):
        start = time.time()
        self.table_departments.setRowCount(0)
        for row_position, department in enumerate(self.database_management.get_departments()):
            self._add_update_department_row(row_position, department)
        self.table_departments.resizeColumnToContents(0)
        self.table_departments.resizeRowsToContents()
        print(f'[VISUAL][DEPARTMENTS] {time.time() - start}')

    def _load_statistics_to_table(self,
                                  stat_time: tuple = None,
                                  temperature: float = None,
                                  name: str = None,
                                  identifiers: list = None
                                  ):
        start = time.time()
        self.table_statistics.setRowCount(0)
        statistics = self.database_management.get_statistics_name_serial_number(
            time=stat_time,
            temperature=temperature,
            identifiers=identifiers,
            name=name
        )
        if len(statistics) > 0:
            self.progressBar.setMaximum(len(statistics))
            self.progressBar.setValue(0)
        else:
            self.progressBar.setMaximum(1)
            self.progressBar.setValue(1)
        print(f'[DATABASE][STATISTICS] {time.time() - start}')
        start = time.time()
        for row_position, (statistic, name, serial_number) in enumerate(statistics):
            self._add_statistic_row(row_position, statistic, name, serial_number)
            self.progressBar.setValue(row_position + 1)
        # self.table_statistics.sortByColumn(0, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        print(f'[VISUAL][STATISTICS] {time.time() - start}')

    def _load_statistics_to_control(self,
                                    stat_time: tuple = None,
                                    temperature: float = None
                                    ):
        start = time.time()
        self.table_control.setRowCount(0)
        statistics = self.database_management.get_statistics(
            time=stat_time,
            temperature=temperature
        )
        statistics.sort(key=lambda x: x.time)
        if len(statistics) > 0:
            self.progressBar.setMaximum(len(statistics))
            self.progressBar.setValue(0)
        else:
            self.progressBar.setMaximum(1)
            self.progressBar.setValue(1)
        print(f'[DATABASE][CONTROL] {time.time() - start}')
        start = time.time()
        for row_position, statistic in enumerate(statistics):
            self._add_statistic_row_to_control(statistic)
            self.progressBar.setValue(row_position + 1)
        print(f'[VISUAL][CONTROL] {time.time() - start}')

    def _add_statistic_row_to_control(self, statistic: models.Statistic):
        self.table_control.insertRow(0)
        item = QTableWidgetItem(str(statistic.time))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 0, item)
        if statistic.id_device:
            item = QTableWidgetItem(self.database_management.get_device_serial_number(statistic.id_device))
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 1, item)
        if statistic.id_profile:
            item = QTableWidgetItem(self.database_management.get_profile_name(statistic.id_profile))
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 2, item)
        item = QTableWidgetItem(self.setting.lang['image'])
        if statistic.face is not None and os.path.exists(f'snapshot{statistic.face}'):
            item.setToolTip(f'<br><img src="snapshot{statistic.face}" width="240" height="426" alt="lorem"')
        else:
            item.setToolTip(self.setting.lang['no_image'])
        self.table_control.setItem(0, 3, item)
        item = QTableWidgetItem(str(statistic.temperature))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 4, item)
        mask = self.database_management.get_mask(statistic.mask)
        item = QTableWidgetItem(self.setting.lang['mask'][mask.mask])
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 5, item)
        item = QTableWidgetItem(f'{int(float(statistic.similar) * 100)} %')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 6, item)
        self.table_control.resizeColumnsToContents()
        self.table_control.resizeRowsToContents()

    def _add_statistic_row(self, row_position: int, statistic: models.Statistic, name: str, serial_number: str):
        self.table_statistics.insertRow(row_position)
        self.table_statistics.setItem(row_position, 0, QTableWidgetItem(str(statistic.time)))
        if serial_number:
            item = QTableWidgetItem(serial_number)
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 1, item)
        if name:
            item = QTableWidgetItem(name)
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 2, item)
        item = QTableWidgetItem(self.setting.lang['image'])
        if statistic.face is not None and os.path.exists(f'snapshot{statistic.face}'):
            item.setToolTip(f'<br><img src="snapshot{statistic.face}" width="240" height="426" alt="lorem"')
        else:
            item.setToolTip(self.setting.lang['no_image'])
        self.table_statistics.setItem(row_position, 3, item)
        item = QTableWidgetItem(str(statistic.temperature))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 4, item)
        mask = self.database_management.get_mask(statistic.mask)
        item = QTableWidgetItem(self.setting.lang['mask'][mask.mask])
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 5, item)
        item = QTableWidgetItem(f'{int(statistic.similar * 100)} %')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 6, item)

    def _add_update_department_row(self, row_position: int, department: models.Department):
        if row_position > self.table_departments.rowCount() - 1:
            self.table_departments.insertRow(row_position)
        item = QCheckBox()
        item.setStyleSheet('background-color: #91D1EE;')
        item.setCheckState(Qt.Unchecked)
        self.table_departments.setCellWidget(row_position, 0, item)
        item = QTableWidgetItem(department.name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_departments.setItem(row_position, 1, item)
        if department.location is None:
            item = QTableWidgetItem('---')
        else:
            item = QTableWidgetItem(department.location)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_departments.setItem(row_position, 2, item)

    def _add_update_profile_row(self, row_position: int, profile: models.Profile):
        if row_position > self.table_profiles.rowCount() - 1:
            self.table_profiles.insertRow(row_position)
        item = QCheckBox()
        item.setStyleSheet('background-color: #91D1EE;')
        item.setCheckState(Qt.Unchecked)
        self.table_profiles.setCellWidget(row_position, 0, item)
        if profile.personnel_number:
            item = QTableWidgetItem(profile.personnel_number)
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 1, item)
        self.table_profiles.setItem(row_position, 2, QTableWidgetItem(profile.name))
        item = QTableWidgetItem(self.setting.lang['image'])
        if os.path.isfile(f'nginx/html{profile.face}'):
            image = f'<br><img src="nginx/html{profile.face}" width="360" alt="lorem"'
        else:
            image = self.setting.lang['no_image']
        item.setToolTip(image)
        self.table_profiles.setItem(row_position, 3, item)
        if profile.visitor:
            user = self.setting.lang['visitor']
        else:
            user = self.setting.lang['employee']
        item = QTableWidgetItem(user)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 4, item)
        if profile.passport is not None:
            passport = profile.passport
        else:
            passport = '---'
        item = QTableWidgetItem(passport)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 5, item)
        gender = self.database_management.get_gender(profile.gender)
        if gender.id == 0:
            gender = self.setting.lang['table_profiles']['unknown']
        elif gender.id == 1:
            gender = self.setting.lang['table_profiles']['male']
        elif gender.id == 2:
            gender = self.setting.lang['table_profiles']['female']
        item = QTableWidgetItem(gender)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 7, item)
        department = self.database_management.get_department(profile.id_department)
        if department:
            department_name = department.name
        else:
            department_name = '---'
        item = QTableWidgetItem(department_name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 6, item)
        if profile.information is not None and profile.information != '':
            information = profile.information
        else:
            information = '---'
        item = QTableWidgetItem(information)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 8, item)

    def _add_device_profile_row(self, profile: models.Profile):
        row_position = self.table_device_profiles.rowCount()
        self.table_device_profiles.insertRow(row_position)
        item = QCheckBox()
        item.setStyleSheet('background-color: #91D1EE;')
        item.setCheckState(Qt.Unchecked)
        self.table_device_profiles.setCellWidget(row_position, 0, item)
        if profile.personnel_number:
            item = QTableWidgetItem(profile.personnel_number)
        else:
            item = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 1, item)
        self.table_device_profiles.setItem(row_position, 2, QTableWidgetItem(profile.name))
        item = QTableWidgetItem(self.setting.lang['image'])
        if os.path.isfile(f'nginx/html{profile.face}'):
            image = f'<br><img src="nginx/html{profile.face}" width="360" alt="lorem"'
        else:
            image = self.setting.lang['no_image']
        item.setToolTip(image)
        self.table_device_profiles.setItem(row_position, 3, item)
        if profile.visitor:
            user = self.setting.lang['visitor']
        else:
            user = self.setting.lang['employee']
        item = QTableWidgetItem(user)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 4, item)
        if profile.passport is not None:
            passport = profile.passport
        else:
            passport = '---'
        item = QTableWidgetItem(passport)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 5, item)
        gender = self.database_management.get_gender(profile.gender)
        if gender.id == 0:
            gender = self.setting.lang['table_profiles']['unknown']
        elif gender.id == 1:
            gender = self.setting.lang['table_profiles']['male']
        elif gender.id == 2:
            gender = self.setting.lang['table_profiles']['female']
        item = QTableWidgetItem(gender)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 7, item)
        department = self.database_management.get_department(profile.id_department)
        if department:
            department_name = department.name
        else:
            department_name = '---'
        item = QTableWidgetItem(department_name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 6, item)
        if profile.information is not None and profile.information != '':
            information = profile.information
        else:
            information = '---'
        item = QTableWidgetItem(information)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 8, item)

    @QtCore.pyqtSlot(tuple)
    def _get_loading_photos_result(self, result: tuple):
        self.blur_effect.setEnabled(True)
        messagebox = InformationMessageBox()
        messagebox.label_title.setText(self.setting.lang['message']['res_add']['title'])
        messagebox.label_info.setText(f'{self.setting.lang["message"]["res_add"]["success"]}: {result[0]}\n'
                                      f'{self.setting.lang["message"]["res_add"]["failure"]}: {result[1]}\n'
                                      f'{result[2]}')
        messagebox.exec_()
        self.blur_effect.setEnabled(False)

    @QtCore.pyqtSlot(object)
    def _get_profiles_from_device(self, data):
        if isinstance(data, dict):
            self.profile_identifiers = []
            self.table_device_profiles.setRowCount(0)
            self.number_device_profiles = data['total_num']
            number_pages = np.int(np.ceil(self.number_device_profiles / 100))
            for page in range(number_pages):
                self.publish_platform.query_profiles_data(page)
            self.last_page = True
        elif isinstance(data, list):
            for profile in data:
                self.profile_identifiers.append(int(profile['user_id']))
            if self.last_page:
                remove_profiles = []
                self.progressBar.setValue(0)
                self.progressBar.setMaximum(len(self.profile_identifiers))
                for identifier in self.profile_identifiers:
                    profile = self.database_management.get_profile(identifier=identifier)
                    if profile:
                        self._add_device_profile_row(profile)
                    else:
                        remove_profiles.append(str(identifier))
                    self.progressBar.setValue(self.progressBar.value() + 1)
                self.is_table_device_profiles_loaded = True
                if len(remove_profiles) > 0:
                    self.publish_platform.remove_profiles_data(*remove_profiles)
                self.table_device_profiles.resizeColumnToContents(0)
                self.table_device_profiles.resizeColumnToContents(1)
                self.table_device_profiles.resizeColumnToContents(2)
                self.table_device_profiles.resizeColumnToContents(3)
                self.table_device_profiles.resizeColumnToContents(4)
                self.table_device_profiles.resizeColumnToContents(5)
                self.table_device_profiles.resizeColumnToContents(6)
                self.table_device_profiles.resizeColumnToContents(7)
                self.table_device_profiles.resizeRowsToContents()

    # STATISTIC
    @QtCore.pyqtSlot(object)
    def _get_record(self, statistic: models.Statistic):
        self._add_statistic_row_to_control(statistic)
        process = multiprocessing.Process(
            target=MainForm._update_plots,
            args=(
                self.setting.lang['charts'],
                self.app_path,
                self.doubleSpinBox_alarm_temperature.value(),
            )
        )
        process.start()
        process.join()
        self.label_pie_number_person_day.setPixmap(
            QPixmap(
                QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_day.png')
            )
        )
        self.label_pie_number_person_day.setToolTip(
            f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/pie_day.png"'
        )
        self.label_pie_number_person_all_time.setPixmap(
            QPixmap(
                QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png')
            )
        )
        self.label_pie_number_person_all_time.setToolTip(
            f'<br><img src="{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png"'
        )
        if self.toggle_notice.isChecked()\
                and self.config is not None\
                and float(statistic.temperature) >= self.doubleSpinBox_alarm_temperature.value():
            if statistic.id_profile:
                user = f'{self.setting.lang["profile"]}:' \
                       f' {self.database_management.get_profile_name(statistic.id_profile)}'
            else:
                user = self.setting.lang['stranger']
            image = None
            if statistic.face:
                image = [f'{self.app_path}/{self.setting.paths["snapshot"]}/{statistic.face}']
            text = f'{statistic.time}\n' \
                   f'{user}\n' \
                   f'{self.setting.lang["temp"]}: {statistic.temperature}'
            send_email(
                subject=self.lineEdit_subject.text(),
                text=text,
                to_recipients=[self.lineEdit_receiver.text()],
                config=self.config,
                images=image
            )

    # OTHERS
    def _update_system_buttons(self, button=QtWidgets.QPushButton):
        self.button_control.setStyleSheet(self.style_unpressed_button)
        self.button_device.setStyleSheet(self.style_unpressed_button)
        self.button_database.setStyleSheet(self.style_unpressed_button)
        self.button_statistic.setStyleSheet(self.style_unpressed_button)
        self.button_settings.setStyleSheet(self.style_unpressed_button)
        button.setStyleSheet(button.styleSheet() + 'QPushButton{ border-right: 15px solid #87B9E0;}')

    @staticmethod
    def _create_report(dialog_result: int,
                       filename: str,
                       parameters: dict
                       ):
        db_management = DBManagement()
        if dialog_result == 1:
            db_management.export_stats_data(
                filename,
                time=(parameters['start'], parameters['end']),
                temperature=(parameters['min'], parameters['max']),
                name=parameters['name']
            )
        elif dialog_result == 2:
            db_management.export_stats_data_passage(
                filename,
                time=(parameters['start'], parameters['end']),
                temperature=(parameters['min'], parameters['max']),
                name=parameters['name']
            )
        elif dialog_result == 3:
            db_management.export_stats_data_temperatures(
                filename,
                time=(parameters['start'], parameters['end']),
                temperature=(parameters['min'], parameters['max']),
                name=parameters['name']
            )

    @staticmethod
    def _update_plots(lang: dict, app_path: str, threshold: float):
        db_visualisation = DBVisualization(width=10, height=6, lang=lang)
        db_visualisation.create_pie_chart_temperatures(threshold=threshold, title=lang['pie_title2'])
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/pie_all_time.png')
        db_visualisation.create_pie_chart_temperatures(
            title=lang['pie_title1'],
            stat_time=(
                datetime.datetime.today().replace(hour=0, minute=0, second=0),
                datetime.datetime.today().replace(hour=23, minute=59, second=59)
            ),
            threshold=threshold
        )
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/pie_day.png')

    @staticmethod
    def _update_plots_statistics(lang: dict, app_path: str, identifier: int, stat_time: tuple, temperature: tuple):
        db_visualisation = DBVisualization(width=10, height=6, lang=lang)
        db_visualisation.create_line_graph_temperatures(
            identifier=identifier,
            time=stat_time,
            temperature=temperature
        )
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/chart1.png')
        db_visualisation.create_map_temperatures(
            identifier=identifier,
            time=stat_time,
            temperature=temperature
        )
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/chart2.png')

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

    # SETTING-EVENTS
    def _button_apply_setting_clicked(self):
        if self.comboBox_langs.currentText() == 'Русский':
            self.setting.data['lang'] = 'ru'
        elif self.comboBox_langs.currentText() == 'English':
            self.setting.data['lang'] = 'en'
        config = self.database_management.get_smtp_config(self.lineEdit_sender.text())
        if config is None:
            config = models.SMTPConfig()
        config.host = self.lineEdit_server.text()
        if self.lineEdit_port.text().isnumeric():
            config.port = int(self.lineEdit_port.text())
        config.user = self.lineEdit_login.text()
        config.password = self.lineEdit_password.text()
        config.default_sender = self.lineEdit_sender.text()
        config.use_tls = self.toggle_tls.isChecked()
        config.use_ehlo = self.toggle_ehlo.isChecked()
        config.use_ssl = self.toggle_ssl.isChecked()
        if config.id:
            self.database_management.update_config(config.id, config)
        else:
            self.database_management.add_smtp_config(config)
        self.config = config
        self.setting.data['sender'] = self.lineEdit_sender.text()
        self.setting.data['receiver'] = self.lineEdit_receiver.text()
        self.setting.data['subject'] = self.lineEdit_subject.text()
        self.setting.save()
        self.translate_ui()

    def _hide_buttons_search_device(self):
        self.button_cancel_new_devices.hide()
        self.button_add_devices.hide()
        self.button_configure_device.show()
        self.label_device_name.show()
        self.lineEdit_device_name.show()
        self.label_volume.show()
        self.horizontalSlider_volume.show()
        self.label_brightness.show()
        self.horizontalSlider_brightness.show()
        self.label_light.show()
        self.toggle_light.show()
        self.label_ip_address.show()
        self.lineEdit_ip_address.show()
        self.label_subnet_mask.show()
        self.lineEdit_subnet_mask.show()
        self.label_gateway.show()
        self.lineEdit_gateway.show()
        self.label_ddns1.show()
        self.lineEdit_ddns1.show()
        self.label_ddns2.show()
        self.lineEdit_ddns2.show()
        self.label_dhcp.show()
        self.toggle_dhcp.show()
        self.label_check_temperature.show()
        self.toggle_check_temperature.show()
        self.label_check_mask.show()
        self.toggle_check_mask.show()
        self.label_strangers_passage.show()
        self.toggle_strangers_passage.show()
        self.label_save_face.show()
        self.toggle_save_face.show()
        self.label_save_record.show()
        self.toggle_save_record.show()
        self.label_record_time.show()
        self.lineEdit_record_time.show()

    def _show_buttons_search_device(self):
        self.button_cancel_new_devices.show()
        self.button_add_devices.show()
        self.button_configure_device.hide()
        self.label_device_name.hide()
        self.lineEdit_device_name.hide()
        self.label_volume.hide()
        self.horizontalSlider_volume.hide()
        self.label_brightness.hide()
        self.horizontalSlider_brightness.hide()
        self.label_light.hide()
        self.toggle_light.hide()
        self.label_ip_address.hide()
        self.lineEdit_ip_address.hide()
        self.label_subnet_mask.hide()
        self.lineEdit_subnet_mask.hide()
        self.label_gateway.hide()
        self.lineEdit_gateway.hide()
        self.label_ddns1.hide()
        self.lineEdit_ddns1.hide()
        self.label_ddns2.hide()
        self.lineEdit_ddns2.hide()
        self.label_dhcp.hide()
        self.toggle_dhcp.hide()
        self.label_check_temperature.hide()
        self.toggle_check_temperature.hide()
        self.label_check_mask.hide()
        self.toggle_check_mask.hide()
        self.label_strangers_passage.hide()
        self.toggle_strangers_passage.hide()
        self.label_save_face.hide()
        self.toggle_save_face.hide()
        self.label_save_record.hide()
        self.toggle_save_record.hide()
        self.label_record_time.hide()
        self.lineEdit_record_time.hide()

    def translate_ui(self):
        self.dateTimeEdit_start.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.dateTimeEdit_end.setDisplayFormat('yyyy-MM-dd HH:mm')
        # SYSTEM
        self.setWindowTitle(self.setting.lang['title'])
        self.label_title.setText(self.setting.lang['title'])
        self.button_close.setToolTip(self.setting.lang['btn_close'])
        self.button_minimize.setToolTip(self.setting.lang['btn_minimize'])
        self.button_control.setText(self.setting.lang['btn_control'])
        self.button_device.setText(self.setting.lang['btn_devices'])
        self.button_database.setText(self.setting.lang['btn_database'])
        self.button_statistic.setText(self.setting.lang['btn_statistic'])
        self.button_settings.setText(self.setting.lang['btn_settings'])
        # PAGE CONTROL
        self.label_alarm_temperature.setText(self.setting.lang['alarm_temp'])
        self.label_notice.setText(self.setting.lang['notice'])
        self.table_control.horizontalHeaderItem(0).setText(self.setting.lang['table_control']['datetime'])
        self.table_control.horizontalHeaderItem(1).setText(self.setting.lang['table_control']['device'])
        self.table_control.horizontalHeaderItem(2).setText(self.setting.lang['table_control']['name'])
        self.table_control.horizontalHeaderItem(3).setText(self.setting.lang['table_control']['photo'])
        self.table_control.horizontalHeaderItem(4).setText(self.setting.lang['table_control']['temp'])
        self.table_control.horizontalHeaderItem(5).setText(self.setting.lang['table_control']['mask'])
        self.table_control.horizontalHeaderItem(6).setText(self.setting.lang['table_control']['similar'])
        # PAGE DEVICES
        self.button_update_device_info.setText(self.setting.lang['btn_search_device'])
        self.button_delete_device.setText(self.setting.lang['btn_delete_device'])
        self.button_configure_device.setText(self.setting.lang['btn_configure_device'])
        self.button_add_devices.setText(self.setting.lang['btn_add_new_device'])
        self.label_device_name.setText(self.setting.lang['device_name'])
        self.label_volume.setText(f'{self.setting.lang["volume"]}: 0')
        self.label_brightness.setText(f'{self.setting.lang["brightness"]}: 45')
        self.label_light.setText(self.setting.lang['light'])
        self.label_ip_address.setText(self.setting.lang['ip_address'])
        self.label_ip_new_device.setText(self.setting.lang['ip_address'])
        self.label_new_device_port.setText(self.setting.lang['port'])
        self.label_device_password.setText(self.setting.lang['password'])
        self.label_new_device_password.setText(self.setting.lang['password'])
        self.label_subnet_mask.setText(self.setting.lang['subnet_mask'])
        self.label_gateway.setText(self.setting.lang['gateway'])
        self.label_ddns1.setText(self.setting.lang['ddns1'])
        self.label_ddns2.setText(self.setting.lang['ddns2'])
        self.label_dhcp.setText(self.setting.lang['dhcp'])
        self.label_check_temperature.setText(self.setting.lang['check_temp'])
        self.label_check_mask.setText(self.setting.lang['check_mask'])
        self.label_strangers_passage.setText(self.setting.lang['strangers_passage'])
        self.label_save_record.setText(self.setting.lang['save_record'])
        self.label_save_face.setText(self.setting.lang['save_face'])
        self.label_record_time.setText(self.setting.lang['record_time'])
        self.table_devices.horizontalHeaderItem(1).setText(self.setting.lang['table_devices']['state'])
        self.table_devices.horizontalHeaderItem(2).setText(self.setting.lang['table_devices']['name'])
        self.table_devices.horizontalHeaderItem(3).setText(self.setting.lang['table_devices']['serial_number'])
        self.table_devices.horizontalHeaderItem(4).setText(self.setting.lang['table_devices']['type'])
        self.table_devices.horizontalHeaderItem(5).setText(self.setting.lang['table_devices']['model'])
        self.table_devices.horizontalHeaderItem(6).setText(self.setting.lang['table_devices']['firmware'])
        self.table_devices.horizontalHeaderItem(7).setText(self.setting.lang['table_devices']['mac_address'])
        self.table_devices.horizontalHeaderItem(8).setText(self.setting.lang['table_devices']['ip_address'])
        # PAGE DATABASE
        self.tabWidget.setTabText(0, self.setting.lang['tab_profiles'])
        self.tabWidget.setTabText(1, self.setting.lang['tab_departments'])
        self.tabWidget.setTabText(2, self.setting.lang['tab_db_device'])
        # PAGE DATABASE - PROFILES
        self.button_add_profile.setText(self.setting.lang['btn_add_profile'])
        self.button_edit_profile.setText(self.setting.lang['btn_edit_profile'])
        self.button_delete_profile.setText(self.setting.lang['btn_delete_profile'])
        self.button_send_device.setText(self.setting.lang['btn_send_device'])
        self.button_example_data.setText(self.setting.lang['btn_example_data'])
        self.button_import_data.setText(self.setting.lang['btn_import_data'])
        self.button_import_photos.setText(self.setting.lang['btn_import_photos'])
        self.button_export_profiles_data.setText(self.setting.lang['btn_export_profiles_data'])
        self.button_load_photo.setText(self.setting.lang['btn_load_photo'])
        self.label_personnel_number.setText(self.setting.lang['pers_number'])
        self.label_profile_name.setText(self.setting.lang['profile_name'])
        self.label_passport.setText(self.setting.lang['passport'])
        self.label_department.setText(self.setting.lang['department_text'])
        self.label_gender.setText(self.setting.lang['gender_text'])
        self.label_visitor.setText(self.setting.lang['visitor'])
        self.label_information.setText(self.setting.lang['info'])
        self.label_show_photo.setText(self.setting.lang['show_photo'])
        self.table_profiles.horizontalHeaderItem(1).setText(self.setting.lang['table_profiles']['pers_number'])
        self.table_profiles.horizontalHeaderItem(2).setText(self.setting.lang['table_profiles']['name'])
        self.table_profiles.horizontalHeaderItem(3).setText(self.setting.lang['table_profiles']['photo'])
        self.table_profiles.horizontalHeaderItem(4).setText(self.setting.lang['table_profiles']['user'])
        self.table_profiles.horizontalHeaderItem(5).setText(self.setting.lang['table_profiles']['passport'])
        self.table_profiles.horizontalHeaderItem(6).setText(self.setting.lang['table_profiles']['department'])
        self.table_profiles.horizontalHeaderItem(7).setText(self.setting.lang['table_profiles']['gender'])
        self.table_profiles.horizontalHeaderItem(8).setText(self.setting.lang['table_profiles']['info'])
        # PAGE DATABASE - DEPARTMENT
        self.button_add_department.setText(self.setting.lang['btn_add_department'])
        self.button_edit_department.setText(self.setting.lang['btn_edit_department'])
        self.button_delete_department.setText(self.setting.lang['btn_delete_department'])
        self.label_department_location.setText(self.setting.lang['location'])
        self.label_department_name.setText(self.setting.lang['department_text'])
        self.table_departments.horizontalHeaderItem(1).setText(self.setting.lang['table_departments']['name'])
        self.table_departments.horizontalHeaderItem(2).setText(self.setting.lang['table_departments']['location'])
        # PAGE DATABASE - DB DEVICE
        self.button_device_database_view.setText(self.setting.lang['btn_device_db_view'])
        self.button_delete_device_profiles.setText(self.setting.lang['btn_delete_device_profile'])
        self.table_device_profiles.horizontalHeaderItem(1).setText(self.setting.lang['table_profiles']['pers_number'])
        self.table_device_profiles.horizontalHeaderItem(2).setText(self.setting.lang['table_profiles']['name'])
        self.table_device_profiles.horizontalHeaderItem(3).setText(self.setting.lang['table_profiles']['photo'])
        self.table_device_profiles.horizontalHeaderItem(4).setText(self.setting.lang['table_profiles']['user'])
        self.table_device_profiles.horizontalHeaderItem(5).setText(self.setting.lang['table_profiles']['passport'])
        self.table_device_profiles.horizontalHeaderItem(6).setText(self.setting.lang['table_profiles']['department'])
        self.table_device_profiles.horizontalHeaderItem(7).setText(self.setting.lang['table_profiles']['gender'])
        self.table_device_profiles.horizontalHeaderItem(8).setText(self.setting.lang['table_profiles']['info'])
        # PAGE STATISTIC
        self.button_statistics_filter.setText(self.setting.lang['btn_filter'])
        self.button_export_statistics_data.setText(self.setting.lang['btn_export_stats_data'])
        self.label_start_time.setText(self.setting.lang['from'])
        self.label_end_time.setText(self.setting.lang['to'])
        self.label_min_temperature.setText(self.setting.lang['from'])
        self.label_max_temperature.setText(self.setting.lang['to'])
        self.label_profile_name_filter.setText(self.setting.lang['name'])
        self.table_statistics.horizontalHeaderItem(0).setText(self.setting.lang['table_control']['datetime'])
        self.table_statistics.horizontalHeaderItem(1).setText(self.setting.lang['table_control']['device'])
        self.table_statistics.horizontalHeaderItem(2).setText(self.setting.lang['table_control']['name'])
        self.table_statistics.horizontalHeaderItem(3).setText(self.setting.lang['table_control']['photo'])
        self.table_statistics.horizontalHeaderItem(4).setText(self.setting.lang['table_control']['temp'])
        self.table_statistics.horizontalHeaderItem(5).setText(self.setting.lang['table_control']['mask'])
        self.table_statistics.horizontalHeaderItem(6).setText(self.setting.lang['table_control']['similar'])
        # PAGE SETTINGS
        self.button_apply_setting.setText(self.setting.lang['btn_apply_setting'])
        self.label_lang.setText(self.setting.lang['lang'])
        self.label_server.setText(self.setting.lang['server'])
        self.label_sender.setText(self.setting.lang['sender'])
        self.label_login.setText(self.setting.lang['login'])
        self.label_port.setText(self.setting.lang['port'])
        self.label_password.setText(self.setting.lang['password'])
        self.label_subject.setText(self.setting.lang['subject'])
        self.label_receiver.setText(self.setting.lang['receiver'])
        self.label_statusbar.setText('')
        self.table_statistics.setSortingEnabled(True)

    def _create_shadows(self):
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setBlurRadius(10)
        self.label_pie_number_person_day.setGraphicsEffect(shadow)
        shadow2 = QtWidgets.QGraphicsDropShadowEffect()
        shadow2.setXOffset(0)
        shadow2.setYOffset(5)
        shadow2.setBlurRadius(10)
        self.label_pie_number_person_all_time.setGraphicsEffect(shadow2)
        shadow3 = QtWidgets.QGraphicsDropShadowEffect()
        shadow3.setXOffset(0)
        shadow3.setYOffset(5)
        shadow3.setBlurRadius(10)
        self.table_control.setGraphicsEffect(shadow3)
        shadow4 = QtWidgets.QGraphicsDropShadowEffect()
        shadow4.setXOffset(0)
        shadow4.setYOffset(5)
        shadow4.setBlurRadius(10)
        self.table_devices.setGraphicsEffect(shadow4)
        shadow5 = QtWidgets.QGraphicsDropShadowEffect()
        shadow5.setXOffset(0)
        shadow5.setYOffset(5)
        shadow5.setBlurRadius(10)
        self.table_profiles.setGraphicsEffect(shadow5)
        shadow6 = QtWidgets.QGraphicsDropShadowEffect()
        shadow6.setXOffset(0)
        shadow6.setYOffset(5)
        shadow6.setBlurRadius(10)
        self.table_departments.setGraphicsEffect(shadow6)
        shadow7 = QtWidgets.QGraphicsDropShadowEffect()
        shadow7.setXOffset(0)
        shadow7.setYOffset(5)
        shadow7.setBlurRadius(10)
        self.table_device_profiles.setGraphicsEffect(shadow7)
        shadow8 = QtWidgets.QGraphicsDropShadowEffect()
        shadow8.setXOffset(0)
        shadow8.setYOffset(5)
        shadow8.setBlurRadius(10)
        self.table_statistics.setGraphicsEffect(shadow8)

    def _create_toggle_buttons(self):
        # PAGE DATABASE
        self.toggle_visitor = AnimatedToggle(self.tab_profiles, checked_color='#309ED9')
        self.toggle_visitor.setGeometry(QtCore.QRect(560, 60, 60, 40))
        # PAGE CONTROL
        self.toggle_notice = AnimatedToggle(self.page_control, checked_color='#309ED9')
        self.toggle_notice.setGeometry(QtCore.QRect(160, 70, 60, 40))
        # PAGE DEVICE
        self.toggle_light = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_light.setGeometry(QtCore.QRect(200, 650, 60, 40))
        self.toggle_dhcp = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_dhcp.setGeometry(QtCore.QRect(555, 650, 60, 40))
        self.toggle_check_temperature = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_check_temperature.setGeometry(QtCore.QRect(990, 440, 60, 40))
        self.toggle_check_mask = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_check_mask.setGeometry(QtCore.QRect(990, 480, 60, 40))
        self.toggle_strangers_passage = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_strangers_passage.setGeometry(QtCore.QRect(990, 520, 60, 40))
        self.toggle_save_record = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_save_record.setGeometry(QtCore.QRect(990, 560, 60, 40))
        self.toggle_save_face = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_save_face.setGeometry(QtCore.QRect(990, 600, 60, 40))
        # PAGE SETTINGS
        self.toggle_ehlo = AnimatedToggle(self.page_settings, checked_color='#309ED9')
        self.toggle_ehlo.setGeometry(QtCore.QRect(160, 430, 60, 40))
        self.toggle_tls = AnimatedToggle(self.page_settings, checked_color='#309ED9')
        self.toggle_tls.setGeometry(QtCore.QRect(160, 470, 60, 40))
        self.toggle_ssl = AnimatedToggle(self.page_settings, checked_color='#309ED9')
        self.toggle_ssl.setGeometry(QtCore.QRect(160, 510, 60, 40))

    # NGINX
    def start_nginx(self):
        path = os.path.abspath('nginx')
        # print(path)
        # os.system(f'{path}\start.bat')
        # # print(path)
        # # subprocess.run([f"{path}\\start", "nginx"])
        # # os.system(f'{path}\\start nginx')
        # print(path)
        self.p = QtCore.QProcess()
        self.p.setWorkingDirectory(f'{path}')
        self.p.start('start.bat')

    def quit_nginx(self):
        os.system('nginx\\nginx.exe -s quit')

import json
import os
import copy
import multiprocessing
import datetime
import time
import natsort
import copy
from typing import Union
import numpy as np
from sqlalchemy import null

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from widget.forms.form_main_designer import Ui_MainWindow
from widget.forms.form_device_database_view import FormDeviceDBView
from widget.forms.form_stranger_table import FormStrangerTable
from widget.forms.form_list_device import FormDeviceList
from widget.forms.messagebox import ExportMessageBox, WarningMessageBox, InformationMessageBox
from widget.forms.toggle_button import AnimatedToggle
import widget.models as models
from widget.management import DBManagement, DeviceManagement
from widget.database_visualization import DBVisualization
from widget.mqtt.subscribe_platform import SubscribePlatform
from widget.mqtt.publish_platform import PublishPlatform
from widget.setting import Setting


# MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        start = time.time()
        super().__init__()
        self.setupUi(self)
        self._create_toggle_buttons()
        self.blur_effect = QtWidgets.QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(15)
        self.blur_effect.setEnabled(False)
        self.setGraphicsEffect(self.blur_effect)
        self._hide_buttons_search_device()
        # APPLICATIONS
        # self.start_nginx()
        # DATA
        self.is_new_devices_table = False
        self.is_table_device_profiles_loaded = False
        self.selected_profile = None
        self.selected_department = None
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
        self.theme = self._get_theme('dark theme')
        self.number_device_profiles = 0
        self.last_page = False
        self.image_filename = None
        self.publish_platform = PublishPlatform(self.device_management.host, client_name='PP1')
        # SETTINGS
        departments = [
            department.name
            for department in self.database_management.get_departments()
        ]
        self.comboBox_gender.addItems([])
        self.comboBox_department.addItems(['---', *departments])
        self.comboBox_gender.addItems(
            [
                self.setting.lang['gender']['unknown'],
                self.setting.lang['gender']['male'],
                self.setting.lang['gender']['female']
            ]
        )
        # self.database_visualization = DBVisualization(width=10, height=6)
        # self.database_visualization.create_pie_chart_temperatures(
        #     title='Passage of people for the current day',
        #     current_day=datetime.date.today().strftime('%Y-%m-%d')
        # )
        # self.database_visualization.save(f'{self.app_path}/{self.setting.paths["temp"]}/pie_day.png')
        # self.label_pie_number_person_day.setPixmap(
        #     QPixmap(
        #         QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_day.png')
        #     )
        # )
        # self.database_visualization.create_pie_chart_temperatures()
        # self.database_visualization.save(f'{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png')
        # self.label_pie_number_person_all_time.setPixmap(
        #     QPixmap(
        #         QImage(f'{self.app_path}/{self.setting.paths["temp"]}/pie_all_time.png')
        #     )
        # )
        # self.label_pie_number_person_day.setScaledContents(True)
        # self.label_pie_number_person_all_time.setScaledContents(True)
        self.dateTimeEdit_end.setDateTime(datetime.datetime.now().replace(hour=23, minute=59, second=59))
        self.filter_params['start'] = self.dateTimeEdit_start.text()
        self.filter_params['end'] = self.dateTimeEdit_end.text()
        self._load_profiles_to_table()
        self._load_departments_to_table()
        self._load_statistics_to_table(
            stat_time=(self.dateTimeEdit_start.text(), self.dateTimeEdit_end.text())
        )
        self.stackedWidget.setCurrentWidget(self.page_control)
        # self.button_device.setStyleSheet(self.theme['system-button'] +
        #                                  "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")
        # SYSTEM BUTTONS, HEADER FRAME AND SIZEGRIP
        self.button_close.clicked.connect(lambda: self.close())
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
        self.button_search_device.clicked.connect(self._button_search_device_clicked)
        self.button_configure_device.clicked.connect(self._button_configure_device_clicked)
        self.button_delete_device.clicked.connect(self._button_delete_device_clicked)
        self.button_cancel_new_devices.clicked.connect(self._button_cancel_new_devices_clicked)
        self.button_add_devices.clicked.connect(self._button_add_new_devices_clicked)
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
        # self.dateTimeEdit_start.setDateTime(datetime.datetime.now().replace(hour=0, minute=0))
        # self.dateTimeEdit_end.setDateTime(datetime.datetime.now().replace(hour=23, minute=59))
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
        pass

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
        row_position = self.table_profiles.selectedIndexes()[0].row()
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
        if self.table_profiles.item(row_position, 4).text() == 'Сотрудник':
            self.selected_profile = self.database_management.get_profile(
                personnel_number=self.table_profiles.item(row_position, 1).text()
            )
            self.toggle_visitor.setChecked(False)
        else:
            self.selected_profile = self.database_management.get_profile(
                passport=self.table_profiles.item(row_position, 5).text()
            )
            self.toggle_visitor.setChecked(True)

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
                text = 'Такой табельный номер уже существует.\n'
            elif self.lineEdit_personnel_number.text() == '':
                text = 'Не введен табельный номер.\n'
            else:
                personnel_number = self.lineEdit_personnel_number.text()
        else:
            if self.lineEdit_passport.text() == '':
                text = 'Не введен паспорт.\n'
        if self.lineEdit_passport.text() != '' \
                and self.database_management.is_passport_duplicate(self.lineEdit_passport.text()):
            text += 'Такой номер паспорта уже существует.\n'
        else:
            passport = self.lineEdit_passport.text()
        if self.lineEdit_profile_name.text() == '':
            text += 'Не введено ФИО.\n'
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
            messagebox.label_title.setText('Добавление профиля')
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
                    text = 'Такой табельный номер уже существует.\n'
                elif self.lineEdit_personnel_number.text() == '':
                    text = 'Не введен табельный номер.\n'
                else:
                    personnel_number = self.lineEdit_personnel_number.text()
            else:
                if self.lineEdit_passport.text() == '':
                    text = 'Не введен паспорт.\n'
            if self.lineEdit_passport.text() != '' \
                    and self.database_management.is_passport_duplicate(self.lineEdit_passport.text()) \
                    and self.selected_profile.passport != self.lineEdit_passport.text():
                text += 'Такой номер паспорта уже существует.\n'
            else:
                passport = self.lineEdit_passport.text()
            if self.lineEdit_profile_name.text() == '':
                text += 'Не введено ФИО.\n'
            else:
                profile_name = self.lineEdit_profile_name.text()
            if self.comboBox_department.currentText() != '---':
                department = self.comboBox_department.currentText()
            gender = self.comboBox_gender.currentIndex()
            if self.plainTextEdit_information.toPlainText() != '':
                information = self.plainTextEdit_information.toPlainText()
        else:
            text = 'Не выбран профиль для изменения.'
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
            profile = {
                'name': profile_name,
                'gender': gender,
                'visitor': self.toggle_visitor.isChecked()
            }
            self.selected_profile.name = profile_name
            self.selected_profile.gender = gender
            self.selected_profile.visitor = self.toggle_visitor.isChecked()
            if personnel_number:
                self.selected_profile.personnel_number = personnel_number
                profile['personnel_number'] = personnel_number
            if passport:
                self.selected_profile.passport = passport
                profile['passport'] = passport
            if image:
                self.selected_profile.face = image
                profile['face'] = image
            if department:
                self.selected_profile.id_department = self.database_management.get_department_by_name(department).id
                profile['id_department'] = self.database_management.get_department_by_name(department).id
            if information:
                self.selected_profile.information = information
                profile['information'] = information
            self.database_management.update_profile(self.selected_profile.id, profile)
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
            messagebox.label_title.setText('Изменение профиля')
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_profile_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = WarningMessageBox()
        messagebox.label_title.setText('Удаление профилей')
        messagebox.label_info.setText('Вы точно хотите удалить профили?')
        messagebox.exec_()
        self.blur_effect.setEnabled(False)
        if messagebox.dialog_result == 0:
            profiles = self.database_management.get_profiles()
            id_profiles = []
            for row_position in range(self.table_profiles.rowCount() - 1, -1, -1):
                if self.table_profiles.cellWidget(row_position, 0).isChecked():
                    id_profiles.append(profiles[row_position].id)
                    self.table_profiles.removeRow(row_position)
            self.database_management.remove_profiles(*id_profiles)
            self.database_management.reset_profile_autoincrement()

    def _button_load_photo_clicked(self, event):
        self.image_filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Выберите фото', '',
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
            messagebox.label_title.setText('Отправка данных')
            messagebox.label_info.setText('Не выбраны пользователи\nдля отправки на устройство.')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)
        elif len(devices) > 0:
            self.blur_effect.setEnabled(True)
            form_device_list = FormDeviceList(devices)
            form_device_list.exec_()
            self.blur_effect.setEnabled(False)
            if form_device_list.dialog_result == 0:
                for device in form_device_list.devices:
                    self.publish_platform.set_device(device.serial_number, device.token)
                    self.publish_platform.add_profiles_data(profile_identifiers)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText('Отправка данных')
            messagebox.label_info.setText('Нет подключенных устройств')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_create_pattern_clicked(self, event):
        filename, _ = QFileDialog.getSaveFileName(self, 'Сохранить пример данных', '', 'CSV File (*.csv)')
        if filename:
            self.database_management.create_profiles_pattern(filename)

    def _button_export_profiles_data(self, event):
        filename, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл данных профиля', '',
                                                  'JSON File (*.json);;'
                                                  'CSV File (*.csv);'
                                                  )
        if filename:
            self.database_management.export_profiles_data(filename)

    def _button_import_profiles_data_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Profiles Group', '', 'CSV File (*.csv)')
        if filename:
            self.database_management.import_profiles_data(filename)
            self._load_profiles_to_table()

    def _button_import_photos_clicked(self, event):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Profile Images', '', 'ZIP File (*.zip)')
        if filename:
            self.database_management.import_photos(filename)
            self._load_profiles_to_table()

    def _department_selected_row(self):
        row_position = self.table_departments.selectedIndexes()[0].row()
        self.selected_department = self.database_management.get_department_by_name(
            self.table_departments.item(row_position, 1).text()
        )
        self.lineEdit_department_name.setText(self.selected_department.name)
        self.lineEdit_department_location.setText(self.selected_department.location)

    def _button_add_department_clicked(self, event):
        text = ''
        if self.lineEdit_department_name.text() != '':
            if not self.database_management.is_department_duplicate(self.lineEdit_department_name.text()):
                department = models.Department()
                department.name = self.lineEdit_department_name.text()
                if self.lineEdit_department_location.text() != '':
                    department.location = self.lineEdit_department_location.text()
            else:
                text = 'Такой отдел уже существует.'
        else:
            text = 'Не введено название отдела.'
        if text == '':
            self.database_management.add_departments(department)
            self._add_update_department_row(self.table_departments.rowCount(), department)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText('Добавление отдела')
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_edit_department_clicked(self, event):
        text = ''
        if self.selected_department is not None:
            if self.lineEdit_department_name.text() != '':
                self.selected_department.name = self.lineEdit_department_name.text()
            else:
                self.selected_department.name = null()
            if self.lineEdit_department_location.text() != '':
                self.selected_department.location = self.lineEdit_department_location.text()
            else:
                self.selected_department.location = null()
        else:
            text = 'Не выбран профиль для изменения.'
        if text == '':
            self.database_management.update_department(self.selected_department.id, self.selected_department)
            self._add_update_department_row(self.table_departments.selectedIndexes()[0].row(), self.selected_department)
        else:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_title.setText('Изменение отдела')
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_department_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = WarningMessageBox()
        messagebox.label_title.setText('Удаление отделов')
        messagebox.label_info.setText('Вы точно хотите удалить отделы?')
        messagebox.exec_()
        self.blur_effect.setEnabled(False)
        if messagebox.dialog_result == 0:
            departments = self.database_management.get_departments()
            id_departments = []
            for row_position in range(self.table_departments.rowCount() - 1, -1, -1):
                if self.table_departments.cellWidget(row_position, 0).isChecked():
                    id_departments.append(departments[row_position].id)
                    self.table_departments.removeRow(row_position)
            self.database_management.remove_departments(*id_departments)
            self.database_management.reset_department_autoincrement()

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
            messagebox.label_title.setText('Просмотр БД устройства')
            messagebox.label_info.setText('Нет подключенных устройств.')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_device_profiles(self, event):
        text = ''
        if not self.is_table_device_profiles_loaded:
            text = 'БД устройства не загружена.\n' \
                   'Выберите устройство\n' \
                   'и нажмите на кн. "Посмотреть"'
        elif self.comboBox_databases.currentText() == '':
            text = 'Нет подключенных устройств.'
        if text == '':
            for device in self.devices:
                if device.serial_number == self.comboBox_databases.currentText():
                    self.blur_effect.setEnabled(True)
                    messagebox = WarningMessageBox()
                    messagebox.label_title.setText('Удаление профилей устройства')
                    messagebox.label_info.setText('Вы точно хотите удалить профили?')
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
            messagebox.label_title.setText('Удаление профилей устройства')
            messagebox.label_info.setText(text)
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    # EVENTS-DEVICE
    def _button_search_device_clicked(self, event):
        self.is_new_devices_table = True
        devices = self.database_management.get_devices()
        self.device_management.clear_devices()
        result = self.device_management.find_devices(binding_devices=devices)
        if result == -1:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_info.setText('Ethernet не подключен.')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)
        elif result == 0 and len(self.device_management.devices) == 0:
            self.blur_effect.setEnabled(True)
            messagebox = InformationMessageBox()
            messagebox.label_info.setText('Устройства не найдены.')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)
        else:
            self._show_buttons_search_device()
            self.table_devices.setRowCount(0)
            for device in self.device_management.devices:
                self._add_device_row(device)

    def _button_add_new_devices_clicked(self, event):
        self._hide_buttons_search_device()
        devices = [
            device
            for row_position, device in enumerate(self.device_management.devices)
            if self.table_devices.cellWidget(row_position, 0).isChecked()
        ]
        self.table_devices.setRowCount(0)
        self._load_devices_info_to_table()
        self.is_new_devices_table = False
        for device in devices:
            self.devices.append(device)
            self.publish_platform.set_device(device.id)
            self.publish_platform.bind_device()

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
                if device.name != self.lineEdit_device_name.text():
                    self.device_configuration['basic_config']['name'] = copy.copy(device.name)
                    device.name = self.lineEdit_device_name.text()
                    self.table_devices.item(row_position, 2).setText(device.name)
                    self.publish_platform.update_basic_configuration(name=device.name)
                if device.volume != self.horizontalSlider_volume.value() \
                        or device.brightness != self.horizontalSlider_brightness.value()\
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
                        or device.temperature_check != self.toggle_check_temperature.isChecked()\
                        or device.mask_detection != self.toggle_check_mask.isChecked()\
                        or device.stranger_passage != self.toggle_strangers_passage.isChecked()\
                        or device.save_jpeg != self.toggle_save_face.isChecked()\
                        or device.record_save != self.toggle_save_record.isChecked():
                    self.device_configuration['temperature_config']['check_temp'] = copy.copy(device.temperature_check)
                    self.device_configuration['temperature_config']['check_mask'] = copy.copy(device.mask_detection)
                    self.device_configuration['temperature_config']['stranger_passage'] = copy.copy(device.stranger_passage)
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
                if device.ip_address != self.lineEdit_ip_address.text()\
                        or device.subnet_mask != self.lineEdit_subnet_mask.text()\
                        or device.gateway != self.lineEdit_gateway.text()\
                        or device.ddns1 != self.lineEdit_ddns1.text()\
                        or device.ddns2 != self.lineEdit_ddns2.text()\
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
            messagebox.label_title.setText('Настройка устройства')
            messagebox.label_info.setText('Не выделено устройство.')
            messagebox.exec_()
            self.blur_effect.setEnabled(False)

    def _button_delete_device_clicked(self, event):
        remove_devices = []
        remove_rows = []
        for row_position, device in enumerate(self.devices):
            if self.table_devices.cellWidget(row_position, 0).isChecked():
                messagebox = WarningMessageBox()
                messagebox.setWindowTitle(f'Удаление {device.serial_number}')
                messagebox.label_title.setText(f'Удаление {device.serial_number}')
                if device.online:
                    text = 'Вы точно хотите удалить устройство?'
                    messagebox.label_info.setText(text)
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        self.publish_platform.set_device(device.id, device.token)
                        self.publish_platform.unbind_device()
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
                else:
                    text = 'Устройство не подключено.\n' \
                           'Если удалите устройство, то нужно будет\nсбросить устройство к заводским настройкам.\n' \
                           'Вы точно хотите удалить устройство?'
                    messagebox.label_info.setText(text)
                    messagebox.exec_()
                    if messagebox.dialog_result == 0:
                        remove_devices.append(device)
                        remove_rows.append(row_position)
                        self.database_management.remove_devices(device.id)
        for device in remove_devices:
            self.devices.remove(device)
        for remove_row in sorted(remove_rows, reverse=True):
            self.table_devices.removeRow(remove_row)

    def _device_selected_row(self):
        if not self.is_new_devices_table:
            row_position = self.table_devices.selectedIndexes()[0].row()
            self.lineEdit_device_name.setText(self.devices[row_position].name)
            self.lineEdit_ip_address.setText(self.devices[row_position].ip_address)
            if self.devices[row_position].online:
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

    def _button_export_statistics_data_clicked(self, event):
        self.blur_effect.setEnabled(True)
        messagebox = ExportMessageBox()
        messagebox.label_title.setText('Экспорт статистики')
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
        messagebox.label_title.setText(f'Результат удаления профилей с {result[3]}')
        messagebox.label_info.setText(f'Кол-во удаленных профилей: {result[0]}\n'
                                      f'Кол-во не удаленных профилей: {result[1]}\n'
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
                self.lineEdit_device_name.text(self.device_configuration['basic_config']['name'])
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
        start = time.time()
        for row_position, profile in enumerate(profiles):
            self._add_update_profile_row(row_position, profile)
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
        for row_position in range(self.table_statistics.rowCount() - 1, -1, -1):
            self.table_statistics.removeRow(row_position)
        # self.table_statistics.setRowCount(0)
        statistics = self.database_management.get_statistics(
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
        for row_position, (statistic, name) in enumerate(statistics):
            self._add_statistic_row(row_position, statistic, name)
            self.progressBar.setValue(row_position + 1)
        # self.table_statistics.sortByColumn(0, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        print(f'[VISUAL][STATISTICS] {time.time() - start}')

    def _load_statistics_to_control(self,
                                    stat_time: tuple = None,
                                    temperature: float = None,
                                    name: str = None,
                                    identifiers: list = None
                                    ):
        start = time.time()
        # for row_position in range(self.table_statistics.rowCount() - 1, -1, -1):
        #     self.table_statistics.removeRow(row_position)
        self.table_statistics.setRowCount(0)
        statistics = self.database_management.get_statistics(
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
        for row_position, (statistic, name) in enumerate(statistics):
            self._add_statistic_row(row_position, statistic, name)
            self.progressBar.setValue(row_position + 1)
        # self.table_statistics.sortByColumn(0, Qt.DescendingOrder)
        self.table_statistics.resizeColumnsToContents()
        self.table_statistics.resizeRowsToContents()
        print(f'[VISUAL][CONTROL] {time.time() - start}')

    def _add_statistic_row(self, row_position: int, statistic: models.Statistic, name: str):
        self.table_statistics.insertRow(row_position)
        self.table_statistics.setItem(row_position, 0, QTableWidgetItem(str(statistic.time)))
        item = QTableWidgetItem(name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 1, item)
        item = QTableWidgetItem(self.setting.lang['image'])
        if statistic.face is not None and os.path.exists(f'snapshot{statistic.face}'):
            item.setToolTip(f'<br><img src="snapshot{statistic.face}" width="240" height="426" alt="lorem"')
        else:
            item.setToolTip(self.setting.lang['no_image'])
        self.table_statistics.setItem(row_position, 2, item)
        item = QTableWidgetItem(str(statistic.temperature))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 3, item)
        mask = self.database_management.get_mask(statistic.mask)
        item = QTableWidgetItem(mask.mask)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 4, item)
        item = QTableWidgetItem(f'{int(statistic.similar*100)} %')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_statistics.setItem(row_position, 5, item)

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
        item = QTableWidgetItem(profile.personnel_number)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_profiles.setItem(row_position, 1, item)
        self.table_profiles.setItem(row_position, 2, QTableWidgetItem(profile.name))
        item = QTableWidgetItem(self.setting.lang['image'])
        if os.path.isfile(f'nginx/html{profile.face}'):
            image = f'<br><img src="nginx/html{profile.face}" width="360" alt="lorem"'
        else:
            image = self.setting.lang['form_main']['page_database']['table_profiles']['tool_image_false']
        item.setToolTip(image)
        self.table_profiles.setItem(row_position, 3, item)
        if profile.visitor:
            user = 'Посетитель'
        else:
            user = 'Сотрудник'
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
        item = QTableWidgetItem(profile.personnel_number)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_device_profiles.setItem(row_position, 1, item)
        self.table_device_profiles.setItem(row_position, 2, QTableWidgetItem(profile.name))
        item = QTableWidgetItem(self.setting.lang['image'])
        if os.path.isfile(f'nginx/html{profile.face}'):
            image = f'<br><img src="nginx/html{profile.face}" width="360" alt="lorem"'
        else:
            image = self.setting.lang['form_main']['page_database']['table_profiles']['tool_image_false']
        item.setToolTip(image)
        self.table_device_profiles.setItem(row_position, 3, item)
        if profile.visitor:
            user = 'Посетитель'
        else:
            user = 'Сотрудник'
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
        messagebox.label_title.setText('Результат загрузки фото')
        messagebox.label_info.setText(f'Кол-во успешных загрузок: {result[0]}\n'
                                      f'Кол-во провальных загрузок: {result[1]}\n'
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
    def _get_record(self, statistic: Union[models.Statistic, models.StrangerStatistic]):
        self.table_control.insertRow(0)
        if isinstance(statistic, models.Statistic):
            item = QTableWidgetItem(self.database_management.get_profile_name(statistic.id_profile))
            item2 = QTableWidgetItem(f'{int(float(statistic.similar) * 100)} %')
        elif isinstance(statistic, models.StrangerStatistic):
            item = QTableWidgetItem('---')
            item2 = QTableWidgetItem('---')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 1, item)
        item = QTableWidgetItem(statistic.time)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 0, item)
        item = QTableWidgetItem(self.setting.lang['image'])
        if statistic.face is not None and os.path.exists(f'snapshot{statistic.face}'):
            item.setToolTip(f'<br><img src="snapshot{statistic.face}" width="240" height="426" alt="lorem"')
        else:
            item.setToolTip(self.setting.lang['no_image'])
        self.table_control.setItem(0, 2, item)
        item = QTableWidgetItem(str(statistic.temperature))
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 3, item)
        mask = self.database_management.get_mask(statistic.mask)
        item = QTableWidgetItem(self.setting.lang['mask'][mask.mask])
        item.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 4, item)
        item2.setTextAlignment(Qt.AlignCenter)
        self.table_control.setItem(0, 5, item2)
        self.table_control.resizeColumnsToContents()
        self.table_control.resizeRowsToContents()

    # OTHERS
    def _update_system_buttons(self, button=QtWidgets.QPushButton):
        # self.button_device.setStyleSheet(self.theme['system-button'])
        # self.button_database.setStyleSheet(self.theme['system-button'])
        # self.button_statistic.setStyleSheet(self.theme['system-button'])
        # self.button_settings.setStyleSheet(self.theme['system-button'])
        # button.setStyleSheet(self.theme['system-button'] +
        #                      "QPushButton{ border-right: 7px solid rgb(85, 170, 255);}")
        pass

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
    def _update_plots(app_path: str):
        db_visualisation = DBVisualization(width=9, height=4)
        db_visualisation.create_pie_chart_temperatures()
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/pie_all_time.png')
        db_visualisation.create_pie_chart_temperatures(
            title='Passage of people for the current day',
            current_day=datetime.date.today().strftime('%Y-%m-%d')
        )
        db_visualisation.figure.savefig(f'{app_path}/widget/data/temp/pie_day.png')

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
        self.label_email.setText(self.setting.lang['email'])
        self.table_control.horizontalHeaderItem(0).setText(self.setting.lang['table_control']['datetime'])
        self.table_control.horizontalHeaderItem(1).setText(self.setting.lang['table_control']['name'])
        self.table_control.horizontalHeaderItem(2).setText(self.setting.lang['table_control']['photo'])
        self.table_control.horizontalHeaderItem(3).setText(self.setting.lang['table_control']['temp'])
        self.table_control.horizontalHeaderItem(4).setText(self.setting.lang['table_control']['mask'])
        self.table_control.horizontalHeaderItem(5).setText(self.setting.lang['table_control']['similar'])
        # PAGE DEVICES
        self.button_search_device.setText(self.setting.lang['btn_search_device'])
        self.button_delete_device.setText(self.setting.lang['btn_delete_device'])
        self.button_configure_device.setText(self.setting.lang['btn_configure_device'])
        self.button_cancel_new_devices.setText(self.setting.lang['btn_cancel_new_device'])
        self.button_add_devices.setText(self.setting.lang['btn_add_new_device'])
        self.label_device_name.setText(self.setting.lang['device_name'])
        self.label_volume.setText(f'{self.setting.lang["volume"]}: 0')
        self.label_brightness.setText(f'{self.setting.lang["brightness"]}: 45')
        self.label_light.setText(self.setting.lang['light'])
        self.label_ip_address.setText(self.setting.lang['ip_address'])
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
        self.label_statusbar.setText("MetallicAlex")

    def _create_toggle_buttons(self):
        # PAGE DATABASE
        self.toggle_visitor = AnimatedToggle(self.tab_profiles, checked_color='#309ED9')
        self.toggle_visitor.setGeometry(QtCore.QRect(560, 60, 60, 40))
        # PAGE CONTROL
        self.toggle_notice = AnimatedToggle(self.page_control, checked_color='#309ED9')
        self.toggle_notice.setGeometry(QtCore.QRect(160, 70, 60, 40))
        # PAGE DEVICE
        self.toggle_light = AnimatedToggle(self.page_device, checked_color='#309ED9')
        self.toggle_light.setGeometry(QtCore.QRect(200, 610, 60, 40))
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

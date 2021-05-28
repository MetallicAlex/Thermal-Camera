import numpy as np

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox

from widget import models
from widget.forms.form_list_device_designer import Ui_ListDeviceForm


class FormDeviceList(QtWidgets.QDialog, Ui_ListDeviceForm):
    def __init__(self, devices: list, lang: dict):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.lang = lang
        self.translate()
        self.devices = devices
        for device in devices:
            self._add_device_row(device)
        self.table_devices.resizeColumnsToContents()
        # SETTINGS
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.table_devices.horizontalHeader().sectionPressed.connect(self._checkbox_header_devices_pressed)
        self.frame_title.mouseMoveEvent = self._frame_header_move_window
        self.frame_title.mousePressEvent = self._frame_header_mouse_press

    # EVENTS
    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_accept_clicked(self, event):
        self.dialog_result = 0
        devices = []
        for row_position, device in enumerate(self.devices):
            if self.table_devices.cellWidget(row_position, 0).isChecked():
                devices.append(device)
        self.devices = devices
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

    def _get_item_image(self, path_image=str):
        item = QTableWidgetItem()
        if os.path.isfile(f'nginx/html{path_image}'):
            pixmap = QPixmap(QImage(f'nginx/html{path_image}'))
        else:
            pixmap = QPixmap(QImage('data/resources/icons/user.png'))
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        item.setData(Qt.DecorationRole, pixmap)
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

    def _add_device_row(self, device: models.Device):
        row_position = self.table_devices.rowCount()
        self.table_devices.insertRow(row_position)
        item = QCheckBox()
        item.setStyleSheet('background-color: #91D1EE;')
        item.setCheckState(Qt.Unchecked)
        self.table_devices.setCellWidget(row_position, 0, item)
        name = device.name
        if name == '' or name is None:
            name = '---'
        item = QTableWidgetItem(name)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 1, item)
        serial_number = device.serial_number
        if serial_number == '' or serial_number is None:
            serial_number = '---'
        item = QTableWidgetItem(serial_number)
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 2, item)

    def translate(self):
        self.label_title.setText(self.lang['title'])
        self.table_devices.horizontalHeaderItem(1).setText(self.lang['name'])
        self.table_devices.horizontalHeaderItem(2).setText(self.lang['serial_number'])
        self.button_close.setToolTip(self.lang['btn_close'])
        self.button_accept.setText(self.lang['btn_add'])
        self.button_cancel.setText(self.lang['btn_cancel'])
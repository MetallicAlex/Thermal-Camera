import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QMessageBox

import widget.models as models
from widget.platforms.subscribe_platform import SubscribePlatform
from widget.platforms.publish_platform import PublishPlatform
from widget.forms.form_devices_designer import Ui_FormDevices


class FormDevices(QtWidgets.QDialog, Ui_FormDevices):
    def __init__(self, devices: list):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.devices = devices
        # SETTINGS
        self._load_devices_info_to_table()
        # SYSTEM BUTTONS, FRAME HEADER
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.frame_header.mouseMoveEvent = self._frame_header_move_window
        self.frame_header.mousePressEvent = self._frame_header_mouse_press
        # TABLE
        self.table_devices.horizontalHeader().sectionPressed.connect(self._checkbox_header_devices_pressed)

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
        self.devices = [
            device for row_position, device in enumerate(self.devices)
            if self.table_devices.cellWidget(row_position, 0).isChecked()
        ]
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

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

    def _load_devices_info_to_table(self):
        for row_position, device in enumerate(self.devices):
            self.table_devices.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_devices.setCellWidget(row_position, 0, item)
            self.table_devices.setItem(row_position, 1, QTableWidgetItem(device.name))
            self.table_devices.setItem(row_position, 2, QTableWidgetItem(device.model))
            self.table_devices.setItem(row_position, 3, QTableWidgetItem(device.id))
            self.table_devices.setItem(row_position, 4, QTableWidgetItem(device.mac_address))
            self.table_devices.setItem(row_position, 5, QTableWidgetItem(device.ip_address))
        self.table_devices.resizeColumnToContents(0)
        self.table_devices.resizeColumnToContents(2)
        self.table_devices.resizeColumnToContents(6)
        self.table_devices.resizeRowsToContents()

    def _set_header_column_icon(self, table=QtWidgets.QTableWidget, checked=bool):
        item = QtWidgets.QTableWidgetItem()
        icon = QtGui.QIcon()
        if checked:
            icon.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-check-circle.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-uncheck-circle.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        table.setHorizontalHeaderItem(0, item)

import re
import os
import socket
import requests
import numpy as np

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QCheckBox, QTableWidgetItem, QMessageBox

import widget.models as models
from widget.platforms.subscribe_platform import SubscribePlatform
from widget.platforms.publish_platform import PublishPlatform
from widget.forms.form_devices_designer import Ui_FormDevices

DEVICE_TOKEN_DEBUG = '1057628122'


class FormDevices(QtWidgets.QDialog, Ui_FormDevices):
    def __init__(self, devices_ip=list):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        self.devices = devices_ip
        self.host_name, self.host_ip = self._get_host_name_ip()
        if self.host_ip is not None:
            self.subscribe_platform = SubscribePlatform()
            self.subscribe_platform.set_host_port(self.host_ip, client_name='SP2')
            self.thread = QtCore.QThread()
            self.subscribe_platform.moveToThread(self.thread)
            self.subscribe_platform.device.connect(self._add_device_info)
            self.thread.started.connect(self.subscribe_platform.run)
            self.thread.start()
            self.publish_platform = PublishPlatform(self.host_ip, client_name='PP2')
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
        self.dialog_result = 1
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = 0
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

    @QtCore.pyqtSlot(dict)
    def _add_device_info(self, data):
        print('RUN NEW')
        row_position = self.table_devices.rowCount()
        self.table_devices.insertRow(row_position)
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
        item = QTableWidgetItem('not added')
        item.setTextAlignment(Qt.AlignCenter)
        self.table_devices.setItem(row_position, 6, item)
        #self.devices[row_position]['state'] = 'online'

    # OTHERS
    def _get_host_name_ip(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            return host_name, host_ip
        except:
            QMessageBox.information('Unable to get Hostname and IP')
            return None

    def _get_devices_info(self):
        os.system('chcp 437')
        with os.popen(f'arp -a -N {self.host_ip}') as file:
            data = file.read()
        devices = []
        for line in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', data):
            if 'dynamic' in line:
                devices.append(line[:2])
        return devices

    def _load_devices_info_to_table(self):
        devices = self._get_devices_info()
        devices = [(ip, mac_address) for ip, mac_address in devices if ip in self.devices]
        for row_position, device in enumerate(devices):
            device_ip, device_mac = device
            request = requests.get(f'http://{device_ip}:7080/ini.htm',
                                   headers={'Authorization': 'Basic YWRtaW46MTIzNDU='})
            if request.status_code == '200':
                pass
            self.table_devices.insertRow(row_position)
            item = QCheckBox()
            item.setCheckState(Qt.Unchecked)
            self.table_devices.setCellWidget(row_position, 0, item)
            self.table_devices.setItem(row_position, 4, QTableWidgetItem(device_mac))
            self.table_devices.setItem(row_position, 5, QTableWidgetItem(device_ip))
        self.table_devices.resizeColumnToContents(0)
        self.table_devices.resizeColumnToContents(2)
        self.table_devices.resizeColumnToContents(6)
        self.table_devices.resizeRowsToContents()

    def _set_header_column_icon(self, table=QtWidgets.QTableWidget, checked=bool):
        item = QtWidgets.QTableWidgetItem()
        icon10 = QtGui.QIcon()
        if checked:
            icon10.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-check-circle.png"),
                             QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon10.addPixmap(QtGui.QPixmap(":/24x24/data/resources/icons/24x24/cil-uncheck-circle.png"),
                             QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon10)
        table.setHorizontalHeaderItem(0, item)
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QTableWidgetItem, QCheckBox

from widget import models
from widget.management import DBManagement
from widget.models import Profile
from widget.forms.messagebox import WarningMessageBox
from widget.forms.form_device_database_view_designer import Ui_FormDeviceDatabaseView


class FormDeviceDBView(QtWidgets.QDialog, Ui_FormDeviceDatabaseView):
    def __init__(self, profiles: list):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.remove_profile_ids = []
        self.profiles = profiles
        # SETTINGS
        self._load_profiles_to_table()
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.button_delete.clicked.connect(self._button_delete_clicked)
        self.frame_header.mouseMoveEvent = self._frame_header_move_window
        self.frame_header.mousePressEvent = self._frame_header_mouse_press

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
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

    def _button_delete_clicked(self, event):
        messagebox = WarningMessageBox()
        messagebox.label_title.setText('Warning - Delete Profiles')
        messagebox.label_info.setText('Are you sure you want to delete profiles?')
        messagebox.exec_()
        if messagebox.dialog_result == 0:
            for row_position in range(self.table_profiles.rowCount() - 1, -1, -1):
                if self.table_profiles.cellWidget(row_position, 0).isChecked():
                    self.remove_profile_ids.append(self.table_profiles.item(row_position, 1).text())
                    self.table_profiles.removeRow(row_position)

    def _load_profiles_to_table(self):
        for row_position, profile in enumerate(self.profiles):
            self._add_profile_row(row_position, profile)
        self.table_profiles.resizeColumnsToContents()
        self.table_profiles.resizeRowsToContents()

    def _add_profile_row(self, row_position: int, profile: models.Profile):
        self.table_profiles.insertRow(row_position)
        item = QCheckBox()
        item.setCheckState(Qt.Unchecked)
        self.table_profiles.setCellWidget(row_position, 0, item)
        self.table_profiles.setItem(row_position, 1, QTableWidgetItem(profile.id))
        self.table_profiles.setItem(row_position, 2, self._get_item_image(profile.face))
        self.table_profiles.setItem(row_position, 3, QTableWidgetItem(profile.name))
        self.table_profiles.setItem(row_position, 4, QTableWidgetItem(profile.name_department))

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
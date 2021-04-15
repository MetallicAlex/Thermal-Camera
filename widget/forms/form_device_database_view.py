from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from widget.management import DBManagement
from widget.models import Profile
from widget.forms.messagebox import WarningMessageBox
from widget.forms.form_device_database_view_designer import Ui_FormDeviceDatabaseView


class FormDeviceDBView(QtWidgets.QDialog, Ui_FormDeviceDatabaseView):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        # SETTINGS
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
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
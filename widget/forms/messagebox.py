from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QPushButton
from widget.forms.department_messagebox import Ui_DepartmentMessageBox


class DepartmentMessageBox(QtWidgets.QDialog, Ui_DepartmentMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.frame_title.mouseMoveEvent = self._frame_header_move_window
        self.frame_title.mousePressEvent = self._frame_header_mouse_press

    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_accept_clicked(self, event):
        pass

    def _button_cancel_clicked(self, event):
        pass
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from widget.forms.messagebox_department import Ui_DepartmentMessageBox
from widget.forms.messagebox_warning import Ui_WarningMessageBox
from widget.forms.messagebox_information import Ui_InforamtionMessageBox


class DepartmentMessageBox(QtWidgets.QDialog, Ui_DepartmentMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        self.department = None
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
        self.dialog_result = 1
        self.department = self.lineEdit_department.text()

    def _button_cancel_clicked(self, event):
        self.dialog_result = 0
        self.department = None


class WarningMessageBox(QtWidgets.QDialog, Ui_WarningMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        self.department = None
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_yes.clicked.connect(self._button_yes_clicked)
        self.button_no.clicked.connect(self._button_no_clicked)
        self.frame_title.mouseMoveEvent = self._frame_header_move_window
        self.frame_title.mousePressEvent = self._frame_header_mouse_press

    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_yes_clicked(self, event):
        self.dialog_result = 1
        self.department = self.lineEdit_department.text()

    def _button_no_clicked(self, event):
        self.dialog_result = 0
        self.department = None


class InformationMessageBox(QtWidgets.QDialog, Ui_InforamtionMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        self.department = None
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_ok.clicked.connect(self._button_ok_clicked)
        self.frame_title.mouseMoveEvent = self._frame_header_move_window
        self.frame_title.mousePressEvent = self._frame_header_mouse_press

    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_ok_clicked(self, event):
        self.dialog_result = 1
        self.department = self.lineEdit_department.text()
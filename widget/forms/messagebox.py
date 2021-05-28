from widget.management import DBManagement

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPointF

from widget.forms.messagebox_warning import Ui_WarningMessageBox
from widget.forms.messagebox_information import Ui_InforamtionMessageBox
from widget.forms.messagebox_export import Ui_ExportMessageBox


class WarningMessageBox(QtWidgets.QDialog, Ui_WarningMessageBox):
    def __init__(self, lang: dict, parent=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.lang = lang
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
        self.dialog_result = 0
        self.close()

    def _button_no_clicked(self, event):
        self.dialog_result = -1
        self.close()

    def translate(self):
        self.button_close.setToolTip(self.lang['btn_close'])
        self.button_yes.setText(self.lang['btn_yes'])
        self.button_no.setText(self.lang['btn_no'])


class InformationMessageBox(QtWidgets.QDialog, Ui_InforamtionMessageBox):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        # SETTINGS
        # DATA
        self.dialog_result = -1
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
        self.close()


class ExportMessageBox(QtWidgets.QDialog, Ui_ExportMessageBox):
    def __init__(self, lang: dict, parent=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.lang = lang
        self.dialog_result = -1
        self.filename = None
        self.translate()
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_all.clicked.connect(self._button_all_clicked)
        self.button_passage.clicked.connect(self._button_passage_clicked)
        self.button_temperature.clicked.connect(self._button_temperature_clicked)
        self.frame_title.mouseMoveEvent = self._frame_header_move_window
        self.frame_title.mousePressEvent = self._frame_header_mouse_press

    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _button_all_clicked(self, event):
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.lang['all'],
                                                                 '',
                                                                 'JSON File (*.json);;'
                                                                 'CSV File (*.csv);')
        if self.filename:
            self.dialog_result = 1
            self.close()

    def _button_passage_clicked(self, event):
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.lang['passage'],
                                                                 '',
                                                                 'JSON File (*.json);;'
                                                                 'CSV File (*.csv);')
        if self.filename:
            self.dialog_result = 2
            self.close()

    def _button_temperature_clicked(self, event):
        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.lang['temperature'],
                                                                 '',
                                                                 'JSON File (*.json);;'
                                                                 'CSV File (*.csv);')
        if self.filename:
            self.dialog_result = 3
            self.close()

    def translate(self):
        self.button_close.setToolTip(self.lang['btn_close'])
        self.button_all.setText(self.lang['btn_all'])
        self.button_passage.setText(self.lang['btn_passage'])
        self.button_temperature.setText(self.lang['btn_temperature'])

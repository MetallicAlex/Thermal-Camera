from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

from widget.forms.form_stranger_table_designer import Ui_FormStrangerTable


class FormStrangerTable(QtWidgets.QDialog, Ui_FormStrangerTable):
    def __init__(self, statistics: list):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        # SETTINGS
        self._load_statistics_to_table(statistics)
        # SYSTEM BUTTONS, FRAME HEADER
        self.button_close.clicked.connect(lambda: self.close())
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

    def _load_statistics_to_table(self, statistics: list):
        for row_position, statistic in enumerate(statistics):
            self.table_statistics.insertRow(row_position)
            self.table_statistics.setItem(row_position, 0, QTableWidgetItem(str(statistic.time)))
            self.table_statistics.setItem(row_position, 1, QTableWidgetItem(str(statistic.temperature)))

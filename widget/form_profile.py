from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

import models
from form_profile_designer import Ui_FormProfile


class FormProfile(QtWidgets.QDialog, Ui_FormProfile):
    def __init__(self, employee=None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = 0
        self.employee = employee
        # SETTINGS
        if self.employee is not None:
            self._set_employee_data()
        # SYSTEM BUTTONS, HEADER FRAME, CHOOSE FILE
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.button_choose_file.clicked.connect(self._button_choose_file_clicked)
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
        self.dialog_result = 1
        pixmap = QPixmap(QImage(self.file_name))
        pixmap.save(f'nginx/html/static/images/{self.lineEdit_name.text()}.jpg')
        self.employee = models.Employee(id=int(self.lineEdit_id.text()),
                                        name=self.lineEdit_name.text(),
                                        name_department=self.comboBox_department.currentText(),
                                        face=f'/static/images/{self.lineEdit_name.text()}.jpg',
                                        gender=self.comboBox_gender.currentText(),
                                        phone_number=self.lineEdit_phonenumber.text())
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = 0
        self.close()

    def _button_choose_file_clicked(self, event):
        self.file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose File', '',
                                                                  'Image File (*.bmp | *.jpg | *.jpeg | *.png);;'
                                                                  'All Files (*)')
        if self.file_name:
            self.label_photo.setScaledContents(False)
            pixmap = QPixmap(QImage(self.file_name))
            pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
            self.label_photo.setPixmap(pixmap)

    # SETTINGS
    def _get_departments(self):
        pass

    def _set_employee_data(self):
        self.lineEdit_id.setText(str(self.employee.id))
        self.lineEdit_name.setText(self.employee.name)
        self.lineEdit_phonenumber.setText(self.employee.phone_number)
        self.comboBox_gender.setCurrentIndex(self.employee.gender.value - 1)
        self.label_photo.setScaledContents(False)
        pixmap = QPixmap(QImage(f'nginx/html{self.employee.face}'))
        pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
        self.label_photo.setPixmap(pixmap)

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from widget.management import DBManagement
from widget.models import Profile
from widget.forms.messagebox import WarningMessageBox
from widget.forms.form_profile_designer import Ui_FormProfile


class FormProfile(QtWidgets.QDialog, Ui_FormProfile):
    def __init__(self, profile: Profile = None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.profile = profile
        self.database_management = DBManagement()
        # SETTINGS
        self._set_departments()
        if self.profile is not None:
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
        self.dialog_result = 0
        if self.filename is None:
            messagebox = WarningMessageBox()
            messagebox.label_title.setText('Warning - No Face Image')
            messagebox.label_info.setText('For the device to recognize you need a face image\n'
                                          'Upload an face image?')
            messagebox.exec_()
            if messagebox.dialog_result == 0:
                self._button_choose_file_clicked(event)
        else:
            pixmap = QPixmap(QImage(self.filename))
            pixmap.save(f'nginx/html/static/images/{self.lineEdit_name.text()}.jpg')
        if self.profile is None:
            if self.database_management.exists_profile(self.lineEdit_id.text()):
                pass
        self.profile = Profile(identifier=self.lineEdit_id.text(),
                               name=self.lineEdit_name.text(),
                               name_department=self.comboBox_department.currentText(),
                               face=f'/static/images/{self.lineEdit_name.text()}.jpg',
                               gender=self.comboBox_gender.currentText(),
                               phone_number=self.lineEdit_phonenumber.text())
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

    def _button_choose_file_clicked(self, event):
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose File', '',
                                                                  'Image File (*.bmp | *.jpg | *.jpeg | *.png);;'
                                                                  'All Files (*)')
        if self.filename:
            self.label_photo.setScaledContents(False)
            pixmap = QPixmap(QImage(self.filename))
            pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
            self.label_photo.setPixmap(pixmap)

    # SETTINGS
    def _set_departments(self):
        departments = [
            department.name for department in self.database_management.get_departments()
        ]
        self.comboBox_department.addItems(departments)

    def _set_employee_data(self):
        self.lineEdit_id.setText(self.profile.id)
        self.lineEdit_name.setText(self.profile.name)
        self.lineEdit_phonenumber.setText(self.profile.phone_number)
        self.comboBox_gender.setCurrentIndex(self.profile.gender.value - 1)
        self.comboBox_department.setCurrentText(self.profile.name_department)
        self.label_photo.setScaledContents(False)
        pixmap = QPixmap(QImage(f'nginx/html{self.profile.face}'))
        pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
        self.label_photo.setPixmap(pixmap)

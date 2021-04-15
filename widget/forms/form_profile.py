from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from widget.management import DBManagement
from widget.models import Profile
from widget.forms.messagebox import WarningMessageBox, InformationMessageBox
from widget.forms.form_profile_designer import Ui_FormProfile


class FormProfile(QtWidgets.QDialog, Ui_FormProfile):
    def __init__(self, profile: Profile = None):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.profile = profile
        self.filename = None
        self.database_management = DBManagement()
        # SETTINGS
        self._set_departments()
        if self.profile is not None:
            self._set_profile_data()
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
        identifier = self.lineEdit_id.text()
        if self.database_management.exists_profile(identifier) and (
                (self.profile is None) or (self.profile is not None and self.profile.id != identifier)):
            messagebox = InformationMessageBox()
            messagebox.label_title.setText('Information - ID')
            messagebox.label_info.setText(f'ID {self.lineEdit_id.text()} already exists.\n'
                                          f'Enter another ID.')
            messagebox.exec_()
        else:
            if self.lineEdit_name.text() == '':
                messagebox = InformationMessageBox()
                messagebox.label_title.setText('Information - Name')
                messagebox.label_info.setText(f'Enter profile name.')
                messagebox.exec_()
            else:
                self.profile = Profile(
                    identifier=self.lineEdit_id.text(),
                    name=self.lineEdit_name.text(),
                    face=f'/static/images/{self.lineEdit_name.text()}.jpg'
                )
                if self.comboBox_department.currentText() != 'Not Selected':
                    self.profile.name_department = self.comboBox_department.currentText()
                if self.comboBox_gender.currentText() != 'Not Selected':
                    self.profile.gender = self.comboBox_gender.currentText()
                if self.lineEdit_phonenumber.text() != '':
                    self.profile.phone_number = self.lineEdit_phonenumber.text()
                self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

    def _button_choose_file_clicked(self, event):
        self.filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Choose File', '',
            'Image File (*.bmp | *.jpg | *.jpeg | *.jfif | *.png);;'
        )
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

    def _set_profile_data(self):
        self.lineEdit_id.setText(self.profile.id)
        self.lineEdit_name.setText(self.profile.name)
        self.lineEdit_phonenumber.setText(self.profile.phone_number)
        if self.profile.gender is None:
            self.comboBox_gender.setCurrentIndex(0)
        else:
            self.comboBox_gender.setCurrentIndex(self.profile.gender.value)
        if self.profile.name_department is None:
            self.comboBox_department.setCurrentIndex(0)
        else:
            self.comboBox_department.setCurrentText(self.profile.name_department)
        if self.profile.face is not None:
            self.filename = f'nginx/html/{self.profile.face}'
            self.label_photo.setScaledContents(False)
            pixmap = QPixmap(QImage(f'nginx/html{self.profile.face}'))
            pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio)
            self.label_photo.setPixmap(pixmap)

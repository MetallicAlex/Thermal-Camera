from PyQt5 import QtWidgets, QtGui, QtCore

from widget.models import Device
from widget.forms.form_configuration_designer import Ui_FormConfiguration


class FormConfiguration(QtWidgets.QDialog, Ui_FormConfiguration):
    def __init__(self, device: Device):
        super().__init__()
        self.setupUi(self)
        # DATA
        self.dialog_result = -1
        self.device = device
        # SETTINGS
        self.label_title.setText(f'Device {device.id}')
        self.checkBox_temperature.setChecked(device.temperature_check)
        self.checkBox_mask_detection.setChecked(device.mask_detection)
        self.checkBox_stranger_passage.setChecked(device.stranger_passage)
        self.checkBox_light_supplementary.setChecked(device.light_supplementary)
        self.checkBox_save_face.setChecked(device.save_jpeg)
        self.checkBox_save_record.setChecked(device.record_save)
        self.horizontalSlider_volume.setValue(device.volume)
        self.label_volume.setText(f'Volume: {self.horizontalSlider_volume.value()}')
        self.horizontalSlider_brightness.setValue(device.brightness)
        self.label_brightness.setText(f'Brightness: {self.horizontalSlider_brightness.value()}')
        self.lineEdit_record_save_time.setText(str(device.record_save_time))
        self.doubleSpinBox_temperature_alarm.setValue(device.temperature_alarm)
        self.doubleSpinBox_temperature_compensation.setValue(device.temperature_compensation)
        # SYSTEM BUTTONS, FRAME HEADER
        self.button_close.clicked.connect(lambda: self.close())
        self.button_accept.clicked.connect(self._button_accept_clicked)
        self.button_cancel.clicked.connect(self._button_cancel_clicked)
        self.frame_header.mouseMoveEvent = self._frame_header_move_window
        self.frame_header.mousePressEvent = self._frame_header_mouse_press
        self.horizontalSlider_volume.valueChanged.connect(self._horizontal_slider_volume_value_changed)
        self.horizontalSlider_brightness.valueChanged.connect(self._horizontal_slider_brightness_value_changed)

    # EVENTS
    def _frame_header_mouse_press(self, event):
        self.dragPos = event.globalPos()

    def _frame_header_move_window(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def _horizontal_slider_volume_value_changed(self):
        self.label_volume.setText(f'Volume: {self.horizontalSlider_volume.value()}')

    def _horizontal_slider_brightness_value_changed(self):
        self.label_brightness.setText(f'Brightness: {self.horizontalSlider_brightness.value()}')

    def _button_accept_clicked(self, event):
        self.dialog_result = 0
        self.device.temperature_check = self.checkBox_temperature.isChecked()
        self.device.mask_detection = self.checkBox_mask_detection.isChecked()
        self.device.stranger_passage = self.checkBox_stranger_passage.isChecked()
        self.device.light_supplementary = self.checkBox_light_supplementary.isChecked()
        self.device.save_jpeg = self.checkBox_save_face.isChecked()
        self.device.record_save = self.checkBox_save_record.isChecked()
        self.device.volume = self.horizontalSlider_volume.value()
        self.device.brightness = self.horizontalSlider_brightness.value()
        self.device.record_save_time = int(self.lineEdit_record_save_time.text())
        self.device.temperature_alarm = self.doubleSpinBox_temperature_alarm.value()
        self.device.temperature_compensation = self.doubleSpinBox_temperature_compensation.value()
        self.close()

    def _button_cancel_clicked(self, event):
        self.dialog_result = -1
        self.close()

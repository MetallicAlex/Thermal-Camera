# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form_configuration.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FormConfiguration(object):
    def setupUi(self, FormConfiguration):
        FormConfiguration.setObjectName("FormConfiguration")
        FormConfiguration.resize(510, 540)
        FormConfiguration.setMaximumSize(QtCore.QSize(510, 650))
        FormConfiguration.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        font = QtGui.QFont()
        font.setPointSize(8)
        FormConfiguration.setFont(font)
        FormConfiguration.setStyleSheet("background: transparent;\n"
                                        "color: rgb(210, 210, 210);")
        self.frame_border = QtWidgets.QFrame(FormConfiguration)
        self.frame_border.setGeometry(QtCore.QRect(0, 0, 510, 540))
        self.frame_border.setStyleSheet("background-color: rgb(27, 29, 35);")
        self.frame_border.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_border.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_border.setObjectName("frame_border")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_border)
        self.horizontalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.frame_main = QtWidgets.QFrame(self.frame_border)
        self.frame_main.setMinimumSize(QtCore.QSize(500, 530))
        self.frame_main.setMaximumSize(QtCore.QSize(500, 16777215))
        self.frame_main.setStyleSheet("/* LINE EDIT */\n"
                                      "QLineEdit {\n"
                                      "    background-color: rgb(27, 29, 35);\n"
                                      "    border-radius: 5px;\n"
                                      "    border: 2px solid rgb(27, 29, 35);\n"
                                      "    padding-left: 10px;\n"
                                      "}\n"
                                      "QLineEdit:hover {\n"
                                      "    border: 2px solid rgb(64, 71, 88);\n"
                                      "}\n"
                                      "QLineEdit:focus {\n"
                                      "    border: 2px solid rgb(91, 101, 124);\n"
                                      "}\n"
                                      "\n"
                                      "/* SCROLL BARS */\n"
                                      "QScrollBar:horizontal {\n"
                                      "    border: none;\n"
                                      "    background: rgb(52, 59, 72);\n"
                                      "    height: 14px;\n"
                                      "    margin: 0px 21px 0 21px;\n"
                                      "    border-radius: 0px;\n"
                                      "}\n"
                                      "QScrollBar::handle:horizontal {\n"
                                      "    background: rgb(85, 170, 255);\n"
                                      "    min-width: 25px;\n"
                                      "    border-radius: 7px\n"
                                      "}\n"
                                      "QScrollBar::add-line:horizontal {\n"
                                      "    border: none;\n"
                                      "    background: rgb(55, 63, 77);\n"
                                      "    width: 20px;\n"
                                      "    border-top-right-radius: 7px;\n"
                                      "    border-bottom-right-radius: 7px;\n"
                                      "    subcontrol-position: right;\n"
                                      "    subcontrol-origin: margin;\n"
                                      "}\n"
                                      "QScrollBar::sub-line:horizontal {\n"
                                      "    border: none;\n"
                                      "    background: rgb(55, 63, 77);\n"
                                      "    width: 20px;\n"
                                      "    border-top-left-radius: 7px;\n"
                                      "    border-bottom-left-radius: 7px;\n"
                                      "    subcontrol-position: left;\n"
                                      "    subcontrol-origin: margin;\n"
                                      "}\n"
                                      "QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
                                      "{\n"
                                      "     background: none;\n"
                                      "}\n"
                                      "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
                                      "{\n"
                                      "     background: none;\n"
                                      "}\n"
                                      " QScrollBar:vertical {\n"
                                      "    border: none;\n"
                                      "    background: rgb(52, 59, 72);\n"
                                      "    width: 14px;\n"
                                      "    margin: 21px 0 21px 0;\n"
                                      "    border-radius: 0px;\n"
                                      " }\n"
                                      " QScrollBar::handle:vertical {    \n"
                                      "    background: rgb(85, 170, 255);\n"
                                      "    min-height: 25px;\n"
                                      "    border-radius: 7px\n"
                                      " }\n"
                                      " QScrollBar::add-line:vertical {\n"
                                      "     border: none;\n"
                                      "    background: rgb(55, 63, 77);\n"
                                      "     height: 20px;\n"
                                      "    border-bottom-left-radius: 7px;\n"
                                      "    border-bottom-right-radius: 7px;\n"
                                      "     subcontrol-position: bottom;\n"
                                      "     subcontrol-origin: margin;\n"
                                      " }\n"
                                      " QScrollBar::sub-line:vertical {\n"
                                      "    border: none;\n"
                                      "    background: rgb(55, 63, 77);\n"
                                      "     height: 20px;\n"
                                      "    border-top-left-radius: 7px;\n"
                                      "    border-top-right-radius: 7px;\n"
                                      "     subcontrol-position: top;\n"
                                      "     subcontrol-origin: margin;\n"
                                      " }\n"
                                      " QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
                                      "     background: none;\n"
                                      " }\n"
                                      "\n"
                                      " QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
                                      "     background: none;\n"
                                      " }\n"
                                      "\n"
                                      "/* CHECKBOX */\n"
                                      "QCheckBox::indicator {\n"
                                      "    border: 3px solid rgb(52, 59, 72);\n"
                                      "    width: 15px;\n"
                                      "    height: 15px;\n"
                                      "    border-radius: 10px;\n"
                                      "    background: rgb(44, 49, 60);\n"
                                      "}\n"
                                      "QCheckBox::indicator:hover {\n"
                                      "    border: 3px solid rgb(58, 66, 81);\n"
                                      "}\n"
                                      "QCheckBox::indicator:checked {\n"
                                      "    background: 3px solid rgb(52, 59, 72);\n"
                                      "    border: 3px solid rgb(52, 59, 72);    \n"
                                      "    background-image: url(:/16x16/data/resources/icons/16x16/cil-check-alt.png);\n"
                                      "}\n"
                                      "\n"
                                      "/* RADIO BUTTON */\n"
                                      "QRadioButton::indicator {\n"
                                      "    border: 3px solid rgb(52, 59, 72);\n"
                                      "    width: 15px;\n"
                                      "    height: 15px;\n"
                                      "    border-radius: 10px;\n"
                                      "    background: rgb(44, 49, 60);\n"
                                      "}\n"
                                      "QRadioButton::indicator:hover {\n"
                                      "    border: 3px solid rgb(58, 66, 81);\n"
                                      "}\n"
                                      "QRadioButton::indicator:checked {\n"
                                      "    background: 3px solid rgb(94, 106, 130);\n"
                                      "    border: 3px solid rgb(52, 59, 72);    \n"
                                      "}\n"
                                      "\n"
                                      "/* COMBOBOX */\n"
                                      "QComboBox{\n"
                                      "    background-color: rgb(27, 29, 35);\n"
                                      "    border-radius: 5px;\n"
                                      "    border: 2px solid rgb(27, 29, 35);\n"
                                      "    padding: 5px;\n"
                                      "    padding-left: 10px;\n"
                                      "}\n"
                                      "QComboBox:hover{\n"
                                      "    border: 2px solid rgb(64, 71, 88);\n"
                                      "}\n"
                                      "QComboBox::drop-down {\n"
                                      "    subcontrol-origin: padding;\n"
                                      "    subcontrol-position: top right;\n"
                                      "    width: 25px; \n"
                                      "    border-left-width: 3px;\n"
                                      "    border-left-color: rgba(39, 44, 54, 150);\n"
                                      "    border-left-style: solid;\n"
                                      "    border-top-right-radius: 3px;\n"
                                      "    border-bottom-right-radius: 3px;    \n"
                                      "    background-image: url(:/16x16/data/resources/icons/16x16/cil-arrow-bottom.png);\n"
                                      "    background-position: center;\n"
                                      "    background-repeat: no-reperat;\n"
                                      " }\n"
                                      "QComboBox QAbstractItemView {\n"
                                      "    color: rgb(85, 170, 255);    \n"
                                      "    background-color: rgb(27, 29, 35);\n"
                                      "    padding: 10px;\n"
                                      "    selection-background-color: rgb(39, 44, 54);\n"
                                      "}\n"
                                      "\n"
                                      "/* SLIDERS */\n"
                                      "QSlider::groove:horizontal {\n"
                                      "    border-radius: 9px;\n"
                                      "    height: 18px;\n"
                                      "    margin: 0px;\n"
                                      "    background-color: rgb(52, 59, 72);\n"
                                      "}\n"
                                      "QSlider::groove:horizontal:hover {\n"
                                      "    background-color: rgb(55, 62, 76);\n"
                                      "}\n"
                                      "QSlider::handle:horizontal {\n"
                                      "    background-color: rgb(85, 170, 255);\n"
                                      "    border: none;\n"
                                      "    height: 18px;\n"
                                      "    width: 18px;\n"
                                      "    margin: 0px;\n"
                                      "    border-radius: 9px;\n"
                                      "}\n"
                                      "QSlider::handle:horizontal:hover {\n"
                                      "    background-color: rgb(105, 180, 255);\n"
                                      "}\n"
                                      "QSlider::handle:horizontal:pressed {\n"
                                      "    background-color: rgb(65, 130, 195);\n"
                                      "}\n"
                                      "\n"
                                      "QSlider::groove:vertical {\n"
                                      "    border-radius: 9px;\n"
                                      "    width: 18px;\n"
                                      "    margin: 0px;\n"
                                      "    background-color: rgb(52, 59, 72);\n"
                                      "}\n"
                                      "QSlider::groove:vertical:hover {\n"
                                      "    background-color: rgb(55, 62, 76);\n"
                                      "}\n"
                                      "QSlider::handle:vertical {\n"
                                      "    background-color: rgb(85, 170, 255);\n"
                                      "    border: none;\n"
                                      "    height: 18px;\n"
                                      "    width: 18px;\n"
                                      "    margin: 0px;\n"
                                      "    border-radius: 9px;\n"
                                      "}\n"
                                      "QSlider::handle:vertical:hover {\n"
                                      "    background-color: rgb(105, 180, 255);\n"
                                      "}\n"
                                      "QSlider::handle:vertical:pressed {\n"
                                      "    background-color: rgb(65, 130, 195);\n"
                                      "}\n"
                                      "/* DoubleSpinBox */\n"
                                      "QDoubleSpinBox {\n"
                                      "    background-color: rgb(27, 29, 35);\n"
                                      "    border-radius: 5px;\n"
                                      "    border: 2px solid rgb(27, 29, 35);\n"
                                      "    padding: 5px;\n"
                                      "    padding-left: 10px;\n"
                                      "}\n"
                                      "QDoubleSpinBox :hover{\n"
                                      "    border: 2px solid rgb(64, 71, 88);\n"
                                      "}\n"
                                      "QDoubleSpinBox::up-arrow {\n"
                                      "    subcontrol-origin: padding;\n"
                                      "    subcontrol-position: top right;\n"
                                      "    width: 25px; \n"
                                      "    border-left-width: 3px;\n"
                                      "    border-left-color: rgba(39, 44, 54, 150);\n"
                                      "    border-left-style: solid;\n"
                                      "    border-top-right-radius: 3px;\n"
                                      "    border-bottom-right-radius: 3px;    \n"
                                      "    background-image: url(:/16x16/data/resources/icons/16x16/cil-arrow-top.png);\n"
                                      "    background-position: center;\n"
                                      "    background-repeat: no-reperat;\n"
                                      " }\n"
                                      "QDoubleSpinBox::down-arrow {\n"
                                      "    subcontrol-origin: padding;\n"
                                      "    subcontrol-position: top right;\n"
                                      "    width: 25px; \n"
                                      "    border-left-width: 3px;\n"
                                      "    border-left-color: rgba(39, 44, 54, 150);\n"
                                      "    border-left-style: solid;\n"
                                      "    border-top-right-radius: 3px;\n"
                                      "    border-bottom-right-radius: 3px;    \n"
                                      "    background-image: url(:/16x16/data/resources/icons/16x16/cil-arrow-bottom.png);\n"
                                      "    background-position: center;\n"
                                      "    background-repeat: no-reperat;\n"
                                      " }\n"
                                      "QDoubleSpinBox::up-button {\n"
                                      "    background-color: transparent;\n"
                                      " }\n"
                                      "QDoubleSpinBox::down-button {\n"
                                      "    background-color: transparent;\n"
                                      " }\n"
                                      "QDoubleSpinBox QAbstractItemView {\n"
                                      "    color: rgb(85, 170, 255);    \n"
                                      "    background-color: rgb(27, 29, 35);\n"
                                      "    padding: 10px;\n"
                                      "    selection-background-color: rgb(39, 44, 54);\n"
                                      "}\n"
                                      "")
        self.frame_main.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_main.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_main.setObjectName("frame_main")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_main)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_header = QtWidgets.QFrame(self.frame_main)
        self.frame_header.setMinimumSize(QtCore.QSize(500, 42))
        self.frame_header.setMaximumSize(QtCore.QSize(500, 42))
        self.frame_header.setStyleSheet("background-color: rgb(27, 29, 35);")
        self.frame_header.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_header.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_header.setObjectName("frame_header")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_header)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_title = QtWidgets.QLabel(self.frame_header)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("")
        self.label_title.setObjectName("label_title")
        self.horizontalLayout.addWidget(self.label_title)
        self.frame_system_buttons = QtWidgets.QFrame(self.frame_header)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_system_buttons.sizePolicy().hasHeightForWidth())
        self.frame_system_buttons.setSizePolicy(sizePolicy)
        self.frame_system_buttons.setMinimumSize(QtCore.QSize(40, 0))
        self.frame_system_buttons.setMaximumSize(QtCore.QSize(40, 16777215))
        self.frame_system_buttons.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_system_buttons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_system_buttons.setObjectName("frame_system_buttons")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_system_buttons)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.button_close = QtWidgets.QPushButton(self.frame_system_buttons)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_close.sizePolicy().hasHeightForWidth())
        self.button_close.setSizePolicy(sizePolicy)
        self.button_close.setMinimumSize(QtCore.QSize(40, 0))
        self.button_close.setMaximumSize(QtCore.QSize(40, 16777215))
        self.button_close.setStyleSheet("QPushButton {    \n"
                                        "    border: none;\n"
                                        "    background-color: transparent;\n"
                                        "}\n"
                                        "QPushButton:hover {\n"
                                        "    background-color: rgb(52, 59, 72);\n"
                                        "}\n"
                                        "QPushButton:pressed {    \n"
                                        "    background-color: rgb(85, 170, 255);\n"
                                        "}")
        self.button_close.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/20x20/data/resources/icons/20x20/cil-x.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.button_close.setIcon(icon)
        self.button_close.setObjectName("button_close")
        self.horizontalLayout_5.addWidget(self.button_close)
        self.horizontalLayout.addWidget(self.frame_system_buttons)
        self.verticalLayout.addWidget(self.frame_header)
        self.frame_contains = QtWidgets.QFrame(self.frame_main)
        self.frame_contains.setMinimumSize(QtCore.QSize(500, 678))
        self.frame_contains.setMaximumSize(QtCore.QSize(500, 678))
        self.frame_contains.setStyleSheet("background-color: rgb(40, 44, 52);")
        self.frame_contains.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_contains.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_contains.setObjectName("frame_contains")
        self.button_accept = QtWidgets.QPushButton(self.frame_contains)
        self.button_accept.setGeometry(QtCore.QRect(30, 420, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        self.button_accept.setFont(font)
        self.button_accept.setStyleSheet("QPushButton {\n"
                                         "    border: 2px solid rgb(52, 59, 72);\n"
                                         "    border-radius: 10px;    \n"
                                         "    background-color: rgb(52, 59, 72);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "}\n"
                                         "QPushButton:hover {\n"
                                         "    background-color: rgb(57, 65, 80);\n"
                                         "    color: rgb(227, 227, 227);\n"
                                         "    border: 2px solid rgb(61, 70, 86);\n"
                                         "}\n"
                                         "QPushButton:pressed {    \n"
                                         "    background-color: rgb(35, 40, 49);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "    border: 2px solid rgb(43, 50, 61);\n"
                                         "}")
        self.button_accept.setIconSize(QtCore.QSize(40, 40))
        self.button_accept.setObjectName("button_accept")
        self.button_cancel = QtWidgets.QPushButton(self.frame_contains)
        self.button_cancel.setGeometry(QtCore.QRect(260, 420, 200, 40))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        self.button_cancel.setFont(font)
        self.button_cancel.setStyleSheet("QPushButton {\n"
                                         "    border: 2px solid rgb(52, 59, 72);\n"
                                         "    border-radius: 10px;    \n"
                                         "    background-color: rgb(52, 59, 72);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "}\n"
                                         "QPushButton:hover {\n"
                                         "    background-color: rgb(57, 65, 80);\n"
                                         "    color: rgb(227, 227, 227);\n"
                                         "    border: 2px solid rgb(61, 70, 86);\n"
                                         "}\n"
                                         "QPushButton:pressed {    \n"
                                         "    background-color: rgb(35, 40, 49);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "    border: 2px solid rgb(43, 50, 61);\n"
                                         "}")
        self.button_cancel.setIconSize(QtCore.QSize(40, 40))
        self.button_cancel.setObjectName("button_cancel")
        self.checkBox_temperature = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_temperature.setGeometry(QtCore.QRect(10, 10, 181, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_temperature.setFont(font)
        self.checkBox_temperature.setObjectName("checkBox_temperature")
        self.checkBox_stranger_passage = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_stranger_passage.setGeometry(QtCore.QRect(10, 40, 181, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_stranger_passage.setFont(font)
        self.checkBox_stranger_passage.setObjectName("checkBox_stranger_passage")
        self.checkBox_mask_detection = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_mask_detection.setGeometry(QtCore.QRect(10, 70, 181, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_mask_detection.setFont(font)
        self.checkBox_mask_detection.setObjectName("checkBox_mask_detection")
        self.doubleSpinBox_temperature_alarm = QtWidgets.QDoubleSpinBox(self.frame_contains)
        self.doubleSpinBox_temperature_alarm.setGeometry(QtCore.QRect(10, 170, 90, 30))
        self.doubleSpinBox_temperature_alarm.setStyleSheet("QDoubleSpinBox {\n"
                                                           "    background-color: rgb(27, 29, 35);\n"
                                                           "    border-radius: 5px;\n"
                                                           "    border: 2px solid rgb(27, 29, 35);\n"
                                                           "    padding-left: 10px;\n"
                                                           "}\n"
                                                           "QDoubleSpinBox:hover {\n"
                                                           "    border: 2px solid rgb(64, 71, 88);\n"
                                                           "}\n"
                                                           "QDoubleSpinBox:focus {\n"
                                                           "    border: 2px solid rgb(91, 101, 124);\n"
                                                           "}")
        self.doubleSpinBox_temperature_alarm.setMinimum(35.0)
        self.doubleSpinBox_temperature_alarm.setMaximum(40.0)
        self.doubleSpinBox_temperature_alarm.setSingleStep(0.1)
        self.doubleSpinBox_temperature_alarm.setProperty("value", 37.5)
        self.doubleSpinBox_temperature_alarm.setObjectName("doubleSpinBox_temperature_alarm")
        self.label_temperature_alarm = QtWidgets.QLabel(self.frame_contains)
        self.label_temperature_alarm.setGeometry(QtCore.QRect(10, 140, 151, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label_temperature_alarm.setFont(font)
        self.label_temperature_alarm.setObjectName("label_temperature_alarm")
        self.doubleSpinBox_temperature_compensation = QtWidgets.QDoubleSpinBox(self.frame_contains)
        self.doubleSpinBox_temperature_compensation.setGeometry(QtCore.QRect(270, 170, 90, 30))
        self.doubleSpinBox_temperature_compensation.setStyleSheet("QDoubleSpinBox {\n"
                                                                  "    background-color: rgb(27, 29, 35);\n"
                                                                  "    border-radius: 5px;\n"
                                                                  "    border: 2px solid rgb(27, 29, 35);\n"
                                                                  "    padding-left: 10px;\n"
                                                                  "}\n"
                                                                  "QDoubleSpinBox:hover {\n"
                                                                  "    border: 2px solid rgb(64, 71, 88);\n"
                                                                  "}\n"
                                                                  "QDoubleSpinBox:focus {\n"
                                                                  "    border: 2px solid rgb(91, 101, 124);\n"
                                                                  "}")
        self.doubleSpinBox_temperature_compensation.setMinimum(-5.0)
        self.doubleSpinBox_temperature_compensation.setMaximum(5.0)
        self.doubleSpinBox_temperature_compensation.setSingleStep(0.1)
        self.doubleSpinBox_temperature_compensation.setProperty("value", 0.0)
        self.doubleSpinBox_temperature_compensation.setObjectName("doubleSpinBox_temperature_compensation")
        self.label_temperature_compensation = QtWidgets.QLabel(self.frame_contains)
        self.label_temperature_compensation.setGeometry(QtCore.QRect(270, 140, 221, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label_temperature_compensation.setFont(font)
        self.label_temperature_compensation.setObjectName("label_temperature_compensation")
        self.label_record_save_time = QtWidgets.QLabel(self.frame_contains)
        self.label_record_save_time.setGeometry(QtCore.QRect(270, 40, 151, 60))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label_record_save_time.setFont(font)
        self.label_record_save_time.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_record_save_time.setObjectName("label_record_save_time")
        self.checkBox_save_record = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_save_record.setGeometry(QtCore.QRect(270, 10, 181, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_save_record.setFont(font)
        self.checkBox_save_record.setObjectName("checkBox_save_record")
        self.checkBox_save_face = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_save_face.setGeometry(QtCore.QRect(10, 100, 181, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_save_face.setFont(font)
        self.checkBox_save_face.setObjectName("checkBox_save_face")
        self.horizontalSlider_volume = QtWidgets.QSlider(self.frame_contains)
        self.horizontalSlider_volume.setGeometry(QtCore.QRect(10, 300, 481, 30))
        self.horizontalSlider_volume.setMaximum(24)
        self.horizontalSlider_volume.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_volume.setObjectName("horizontalSlider_volume")
        self.label_volume = QtWidgets.QLabel(self.frame_contains)
        self.label_volume.setGeometry(QtCore.QRect(10, 270, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label_volume.setFont(font)
        self.label_volume.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_volume.setObjectName("label_volume")
        self.horizontalSlider_brightness = QtWidgets.QSlider(self.frame_contains)
        self.horizontalSlider_brightness.setGeometry(QtCore.QRect(10, 360, 481, 30))
        self.horizontalSlider_brightness.setMinimum(45)
        self.horizontalSlider_brightness.setMaximum(100)
        self.horizontalSlider_brightness.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_brightness.setObjectName("horizontalSlider_brightness")
        self.label_brightness = QtWidgets.QLabel(self.frame_contains)
        self.label_brightness.setGeometry(QtCore.QRect(10, 330, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label_brightness.setFont(font)
        self.label_brightness.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_brightness.setObjectName("label_brightness")
        self.checkBox_light_supplementary = QtWidgets.QCheckBox(self.frame_contains)
        self.checkBox_light_supplementary.setGeometry(QtCore.QRect(10, 240, 201, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.checkBox_light_supplementary.setFont(font)
        self.checkBox_light_supplementary.setObjectName("checkBox_light_supplementary")
        self.lineEdit_record_save_time = QtWidgets.QLineEdit(self.frame_contains)
        self.lineEdit_record_save_time.setGeometry(QtCore.QRect(270, 100, 211, 30))
        self.lineEdit_record_save_time.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        self.lineEdit_record_save_time.setFont(font)
        self.lineEdit_record_save_time.setStyleSheet("QLineEdit {\n"
                                                     "    background-color: rgb(27, 29, 35);\n"
                                                     "    border-radius: 5px;\n"
                                                     "    border: 2px solid rgb(27, 29, 35);\n"
                                                     "    padding-left: 10px;\n"
                                                     "}\n"
                                                     "QLineEdit:hover {\n"
                                                     "    border: 2px solid rgb(64, 71, 88);\n"
                                                     "}\n"
                                                     "QLineEdit:focus {\n"
                                                     "    border: 2px solid rgb(91, 101, 124);\n"
                                                     "}")
        self.lineEdit_record_save_time.setMaxLength(32)
        self.lineEdit_record_save_time.setObjectName("lineEdit_record_save_time")
        self.verticalLayout.addWidget(self.frame_contains)
        self.horizontalLayout_3.addWidget(self.frame_main)

        self.retranslateUi(FormConfiguration)
        QtCore.QMetaObject.connectSlotsByName(FormConfiguration)

    def retranslateUi(self, FormConfiguration):
        _translate = QtCore.QCoreApplication.translate
        FormConfiguration.setWindowTitle(_translate("FormConfiguration", "Device Configuration"))
        self.label_title.setText(_translate("FormConfiguration", "Device"))
        self.button_close.setToolTip(_translate("FormConfiguration", "Close"))
        self.button_accept.setText(_translate("FormConfiguration", "Accept"))
        self.button_cancel.setText(_translate("FormConfiguration", "Cancel"))
        self.checkBox_temperature.setText(_translate("FormConfiguration", "Temperature Check"))
        self.checkBox_stranger_passage.setText(_translate("FormConfiguration", "Stranger Passage"))
        self.checkBox_mask_detection.setText(_translate("FormConfiguration", "Mask Detection"))
        self.label_temperature_alarm.setText(_translate("FormConfiguration", "Temperature Alarm"))
        self.label_temperature_compensation.setText(_translate("FormConfiguration", "Temperature Compensation"))
        self.label_record_save_time.setText(_translate("FormConfiguration", "Record Save Time\n"
                                                                            "(unlimited = -1)"))
        self.checkBox_save_record.setText(_translate("FormConfiguration", "Save Record"))
        self.checkBox_save_face.setText(_translate("FormConfiguration", "Save Face"))
        self.label_volume.setText(_translate("FormConfiguration", "Volume"))
        self.label_brightness.setText(_translate("FormConfiguration", "Brightness"))
        self.checkBox_light_supplementary.setText(_translate("FormConfiguration", "Light Supplementary"))
        self.lineEdit_record_save_time.setPlaceholderText(_translate("FormConfiguration", "Hour"))
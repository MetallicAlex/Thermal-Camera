# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'messagebox_export.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExportMessageBox(object):
    def setupUi(self, ExportMessageBox):
        ExportMessageBox.setObjectName("ExportMessageBox")
        ExportMessageBox.resize(400, 200)
        ExportMessageBox.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        ExportMessageBox.setStyleSheet("background: transparent;\n"
                                       "color: rgb(210, 210, 210);")
        self.verticalLayout = QtWidgets.QVBoxLayout(ExportMessageBox)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_center = QtWidgets.QFrame(ExportMessageBox)
        self.frame_center.setStyleSheet("background-color: #0C5DB9;\n"
                                        "")
        self.frame_center.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_center.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_center.setObjectName("frame_center")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_center)
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_title = QtWidgets.QFrame(self.frame_center)
        self.frame_title.setMaximumSize(QtCore.QSize(400, 42))
        self.frame_title.setStyleSheet("background-color: #0C5DB9;\n"
                                       "")
        self.frame_title.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_title.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_title.setLineWidth(0)
        self.frame_title.setObjectName("frame_title")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_title)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_title = QtWidgets.QLabel(self.frame_title)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 221))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.label_title.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("background: transparent;\n"
                                       "color: rgb(255, 255, 255, 221);")
        self.label_title.setObjectName("label_title")
        self.horizontalLayout_3.addWidget(self.label_title)
        self.button_close = QtWidgets.QPushButton(self.frame_title)
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
                                        "    background-color: #B9400C;\n"
                                        "}\n"
                                        "QPushButton:pressed {    \n"
                                        "    background-color: #D04B4B;\n"
                                        "}")
        self.button_close.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/20x20/data/resources/icons/20x20/cil-x.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.button_close.setIcon(icon)
        self.button_close.setObjectName("button_close")
        self.horizontalLayout_3.addWidget(self.button_close)
        self.verticalLayout_2.addWidget(self.frame_title)
        self.frame_contains = QtWidgets.QFrame(self.frame_center)
        self.frame_contains.setStyleSheet("background-color: #EFF7FD;")
        self.frame_contains.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_contains.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_contains.setObjectName("frame_contains")
        self.button_temperature = QtWidgets.QPushButton(self.frame_contains)
        self.button_temperature.setGeometry(QtCore.QRect(122, 104, 150, 30))
        self.button_temperature.setMinimumSize(QtCore.QSize(150, 30))
        self.button_temperature.setMaximumSize(QtCore.QSize(150, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.button_temperature.setFont(font)
        self.button_temperature.setStyleSheet("QPushButton {\n"
                                              "    border-radius: 10px;    \n"
                                              "    background-color: #0C5DB9;\n"
                                              "    color: rgb(255, 255, 255, 221);\n"
                                              "}\n"
                                              "QPushButton:hover {\n"
                                              "    background-color: #91D1EE;\n"
                                              "    color: rgb(255, 255, 255, 221);\n"
                                              "}\n"
                                              "QPushButton:pressed {    \n"
                                              "    background-color: #87B9E0;\n"
                                              "    color: rgb(255, 255, 255);\n"
                                              "}")
        self.button_temperature.setObjectName("button_temperature")
        self.button_all = QtWidgets.QPushButton(self.frame_contains)
        self.button_all.setGeometry(QtCore.QRect(122, 18, 150, 30))
        self.button_all.setMaximumSize(QtCore.QSize(150, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.button_all.setFont(font)
        self.button_all.setStyleSheet("QPushButton {\n"
                                      "    border-radius: 10px;    \n"
                                      "    background-color: #0C5DB9;\n"
                                      "    color: rgb(255, 255, 255, 221);\n"
                                      "}\n"
                                      "QPushButton:hover {\n"
                                      "    background-color: #91D1EE;\n"
                                      "    color: rgb(255, 255, 255, 221);\n"
                                      "}\n"
                                      "QPushButton:pressed {    \n"
                                      "    background-color: #87B9E0;\n"
                                      "    color: rgb(255, 255, 255);\n"
                                      "}")
        self.button_all.setObjectName("button_all")
        self.button_passage = QtWidgets.QPushButton(self.frame_contains)
        self.button_passage.setGeometry(QtCore.QRect(122, 61, 150, 30))
        self.button_passage.setMaximumSize(QtCore.QSize(150, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.button_passage.setFont(font)
        self.button_passage.setStyleSheet("QPushButton {\n"
                                          "    border-radius: 10px;    \n"
                                          "    background-color: #0C5DB9;\n"
                                          "    color: rgb(255, 255, 255, 221);\n"
                                          "}\n"
                                          "QPushButton:hover {\n"
                                          "    background-color: #91D1EE;\n"
                                          "    color: rgb(255, 255, 255, 221);\n"
                                          "}\n"
                                          "QPushButton:pressed {    \n"
                                          "    background-color: #87B9E0;\n"
                                          "    color: rgb(255, 255, 255);\n"
                                          "}")
        self.button_passage.setObjectName("button_passage")
        self.verticalLayout_2.addWidget(self.frame_contains)
        self.verticalLayout.addWidget(self.frame_center)

        self.retranslateUi(ExportMessageBox)
        QtCore.QMetaObject.connectSlotsByName(ExportMessageBox)

    def retranslateUi(self, ExportMessageBox):
        _translate = QtCore.QCoreApplication.translate
        ExportMessageBox.setWindowTitle(_translate("ExportMessageBox", "Экспорт"))
        self.label_title.setText(_translate("ExportMessageBox", "Экспорт"))
        self.button_close.setToolTip(_translate("ExportMessageBox", "Close"))
        self.button_temperature.setText(_translate("ExportMessageBox", "Температура"))
        self.button_all.setText(_translate("ExportMessageBox", "Все"))
        self.button_passage.setText(_translate("ExportMessageBox", "Время прохода"))

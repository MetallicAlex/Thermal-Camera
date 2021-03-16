from PyQt5 import QtCore, QtGui, QtWidgets
from widget.forms.form_main import MainForm

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    form.show()
    sys.exit(app.exec_())

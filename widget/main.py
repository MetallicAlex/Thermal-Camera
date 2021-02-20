from PyQt5 import QtCore, QtGui, QtWidgets
from form_main import MainForm
from form_profile import FormProfile

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    form.show()
    sys.exit(app.exec_())

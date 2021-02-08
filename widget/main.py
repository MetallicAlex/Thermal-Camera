from PyQt5 import QtCore, QtGui, QtWidgets
from form_main import MainForm

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #MainWindow = QtWidgets.QMainWindow()
    form = MainForm()
    #form.setupUi(MainWindow)
    form.show()
    sys.exit(app.exec_())

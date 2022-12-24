from PyQt5.QtWidgets import QApplication
from detectionWindow import detectionWindow
import sys

app = QApplication(sys.argv)
mainwindow = detectionWindow()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")
from PyQt5.QtWidgets import QApplication
from uiLibrary.detectionWindow import detectionWindow
import sys

app = QApplication(sys.argv)
mainWindow = detectionWindow()

mainWindow.detection_instance()
mainWindow.start_detection()

try:
    sys.exit(app.exec_())
except:
    print("Process Killed")
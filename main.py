
import time

from PyQt5.QtWidgets import *
from module.controller.controller_module import Controller
import sys

app = QApplication(sys.argv)
myWindow = Controller()
myWindow.show()
app.exec_()

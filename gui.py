from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileDialog
from PyQt5.uic import loadUi
import sys
from main import *

class MyWindow(QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__()
		self.initUI()


def window():
	app = QApplication(sys.argv)
	win = QMainWindow()
	win.setGeometry(200, 200, 750, 500)
	win.setWindowTitle('Readable')

	get_density = QtWidgets.QPushButton(win)
	get_density.setText('Get Density!')
	get_density.move(25, 50)
	get_density.clicked.connect(lambda:start_new_map('cycle hit.osu', 0, 0, 0, 0, 1))

	win.show()
	sys.exit(app.exec_())

window()
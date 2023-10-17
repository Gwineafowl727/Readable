import sys
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QComboBox, QFileDialog, QLabel, QMainWindow, QPushButton, QSpinBox
from readable import start_new_map


class Window(QMainWindow):
	def __init__(self) -> None:
		# Make window
		super().__init__()
		self.setWindowTitle("Readable")
		self.setFixedWidth(400)
		self.setFixedHeight(600)
		self.filepath = ""
		self.mod = "NM"
		
		# Select map
		self.map_button = QPushButton(self)
		self.map_button.setText("Select Map")
		self.map_button.setGeometry(20, 20, 100, 30)
		self.map_button.clicked.connect(self.choose_map)
		
		# Display map name
		self.map_name = QLabel(self)
		self.map_name.setGeometry(20, 50, 360, 30)

		# Select mod
		self.mod_list_text = QLabel(self)
		self.mod_list_text.setGeometry(20, 130, 100, 30)
		self.mod_list_text.setText("Select Mod")
		self.mod_list = QComboBox(self)
		self.mod_list.setGeometry(20, 160, 100, 30)
		self.mod_list.addItems(["NM", "HR", "EZ", "Custom AR"])
		self.mod_list.currentIndexChanged.connect(lambda: self.set_mod(self.mod_list.currentIndex()))

		# Custom AR
		self.custom_ar_text = QLabel(self)
		self.custom_ar_text.setGeometry(20, 270, 200, 30)
		self.custom_ar_text.setText("Custom AR (-5 to 11)")
		self.custom_ar = QSpinBox(self)
		self.custom_ar.setRange(-5, 11)
		self.custom_ar.setGeometry(20, 300, 100, 30)
		self.custom_ar.setEnabled(False)

		# Get score
		self.get_score_button = QPushButton(self)
		self.get_score_button.setGeometry(20, 440, 160, 30)
		self.get_score_button.setText("Get Readability Rating")
		self.get_score_button.clicked.connect(self.get_score)
		self.readability = QLabel(self)
		self.readability.setGeometry(20, 470, 360, 30)

		self.show()

	@Slot()
	def choose_map(self) -> None:
		try:
			file = QFileDialog.getOpenFileName(self, caption="Open Map", dir="./", filter="Map Files (*.osu)")[0]
			if file:
				# Not sure how you want the map's name displayed
				self.map_name.setText(file.split("/")[-1][:-4])
				self.filepath = file
			else:
				self.filepath = ""
		except: # Can't think of a specific error
			pass

	@Slot()
	def set_mod(self, index: int) -> None:
		if index == 3:
			self.custom_ar.setEnabled(True)
			self.mod = "Custom AR"
		else:
			self.custom_ar.setEnabled(False)
			self.mod = self.mod_list.currentText()

	@Slot()
	def get_score(self) -> None:
		if self.filepath:
			if self.mod == "Custom AR":
				score = str(round(start_new_map(self.filepath, self.custom_ar.value()), 2))
			else:
				score = str(round(start_new_map(self.filepath, self.mod), 2))
			self.readability.setText(score)


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    sys.exit(app.exec())

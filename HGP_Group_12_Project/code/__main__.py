from PyQt6.QtWidgets import QApplication
from go import Go
import sys

app = QApplication([])

with open("HGP_Group_12_Project/code/stylesheet.qss", "r") as f:
    app.setStyleSheet(f.read())

myGo = Go()
sys.exit(app.exec())

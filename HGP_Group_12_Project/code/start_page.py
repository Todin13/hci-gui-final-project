from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize


class StartPage(QWidget):
    newGameSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        # Add a space at the top to center vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        label = QLabel("Welcome to the Go game !")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label)

        # Add a space between the label and the button
        layout.addSpacing(20)

        button_new_game = QPushButton("New game")
        button_new_game.clicked.connect(self.newGameSignal.emit)
        button_new_game.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(button_new_game)

        button_rules = QPushButton("How to play")
        button_rules.clicked.connect(self.showRules)
        button_rules.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(button_rules)

        # Add a space at the bottom to center vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.setLayout(layout)

    def showRules(self):
        rules = (
            "Rules of Go:\n"
            '1. Go is a territory control game between "Black" and "White".\n\n'
            "2. Go is played on a Goban, a squared board, here 9x9.\n\n"
            '3. Every turn, Black or White places a "Stone" in a free intersection on the board.\n\n'
            "4. Totally surrounding an opponnent' stone or group of stones will have those captured.\n\n"
            "5. The winner is decided by however has the most captured stones and free intersections surrounded by their own stones.\n\n"
            "6. The game is over when both player passes their turn.\n"
        )
        QMessageBox.information(self, "Rules of Go", rules)

    def sizeHint(self):
        return QSize(400, 200)  # Define a prefered size for the window

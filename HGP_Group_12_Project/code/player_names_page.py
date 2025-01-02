from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize

class PlayerNamesPage(QWidget):
    startGameSignal = pyqtSignal(str, str)

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

        formLayout = QFormLayout()

        self.player1Name = QLineEdit()
        self.player2Name = QLineEdit()

        self.player1Name.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.player2Name.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        formLayout.addRow("Player name 1:", self.player1Name)
        formLayout.addRow("Player name 2:", self.player2Name)

        layout.addLayout(formLayout)

        # Add a space between the write boxes and the button
        layout.addSpacing(20)

        button = QPushButton("Start the game")
        button.clicked.connect(self.startGame)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(button)

        # Add a space at the bottom to center vertically
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.setLayout(layout)

    def startGame(self):
        player1 = self.player1Name.text()
        player2 = self.player2Name.text()
        self.startGameSignal.emit(player1, player2)

    def sizeHint(self):
        return QSize(400, 300)  # Define a prefered size for the window

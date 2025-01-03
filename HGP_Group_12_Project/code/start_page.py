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
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.initUI()

    def initUI(self):
        # Clear the existing layout before reinitializing
        self.clearLayout(self.layout)

        # Add a space at the top to center vertically
        self.layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.label = QLabel("Welcome to the Go game !")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(self.label)

        # Add a space between the label and the button
        self.layout.addSpacing(20)

        self.button_new_game = QPushButton("New game")
        self.button_new_game.clicked.connect(self.showGameOptions)
        self.button_new_game.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(self.button_new_game)

        self.button_rules = QPushButton("How to play")
        self.button_rules.clicked.connect(self.showRules)
        self.button_rules.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(self.button_rules)

        # Add a space at the bottom to center vertically
        self.layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

    def showRules(self):
        rules = (
            "Rules of Go:\n"
            '1. Go is a territory control game between "Black" and "White".\n\n'
            "2. Go is played on a Goban, a squared board, here 9x9.\n\n"
            '3. Every turn, Black or White places a "Stone" in a free intersection on the board.\n\n'
            "4. Totally surrounding an opponent' stone or group of stones will have those captured.\n\n"
            "5. The winner is decided by whoever has the most captured stones and free intersections surrounded by their own stones.\n\n"
            "6. The game is over when both players pass their turn.\n"
        )
        QMessageBox.information(self, "Rules of Go", rules)

    def sizeHint(self):
        return QSize(400, 200)  # Define a preferred size for the window

    def showGameOptions(self):
        # Clear the layout
        self.clearLayout(self.layout)

        # Update the label
        self.label.setText("Select Game Mode")
        self.layout.addWidget(self.label)

        # Add Normal Game button
        button_normal_game = QPushButton("Normal Game")
        button_normal_game.clicked.connect(
            self.newGameSignal.emit
        )  # Connect to the new game signal
        button_normal_game.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(button_normal_game)

        # Add Blitz Game button
        button_blitz_game = QPushButton("Blitz Game")
        button_blitz_game.clicked.connect(
            self.newGameSignal.emit
        )  # Connect to the new game signal
        button_blitz_game.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(button_blitz_game)

        # Add Return button
        button_return = QPushButton("Return")
        button_return.clicked.connect(self.initUI)
        button_return.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.layout.addWidget(button_return)

        # Add a space at the bottom to center vertically
        self.layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

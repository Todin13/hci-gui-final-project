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

        # Ajouter un espace en haut pour centrer verticalement
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        label = QLabel("Bienvenue au jeu de Go")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label)

        # Ajouter un espace entre le label et le bouton
        layout.addSpacing(20)

        button_new_game = QPushButton("Nouvelle partie")
        button_new_game.clicked.connect(self.newGameSignal.emit)
        button_new_game.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(button_new_game)

        button_rules = QPushButton("Comment jouer")
        button_rules.clicked.connect(self.showRules)
        button_rules.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(button_rules)

        # Ajouter un espace en bas pour centrer verticalement
        layout.addSpacerItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        self.setLayout(layout)

    def showRules(self):
        rules = (
            "Règles du jeu de Go:\n"
            "1. Le jeu se joue sur un plateau de 9x9.\n"
            "2. Les joueurs placent à tour de rôle une pierre sur une intersection vide.\n"
            "3. Le but est de contrôler plus de territoire que l'adversaire.\n"
            "4. Les pierres sont capturées si elles n'ont plus de libertés.\n"
            "5. Le jeu se termine quand les deux joueurs passent leur tour.\n"
        )
        QMessageBox.information(self, "Règles du jeu de Go", rules)

    def sizeHint(self):
        return QSize(400, 200)  # Définir une taille préférée pour la page

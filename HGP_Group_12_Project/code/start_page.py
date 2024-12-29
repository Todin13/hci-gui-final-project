from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt, QSize

class StartPage(QWidget):
    newGameSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Ajouter un espace en haut pour centrer verticalement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        label = QLabel("Bienvenue au jeu de Go")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(label)

        # Ajouter un espace entre le label et le bouton
        layout.addSpacing(20)

        button = QPushButton("Nouvelle partie")
        button.clicked.connect(self.newGameSignal.emit)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(button)

        # Ajouter un espace en bas pour centrer verticalement
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

    def sizeHint(self):
        return QSize(400, 200)  # Définir une taille préférée pour la page

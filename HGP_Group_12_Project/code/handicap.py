from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QButtonGroup,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)


class HandicapDialog(QDialog):

    player_index = {"White Player": 1, "Black Player": 2, "None": 0}
    index_to_player = {1: "White Player", 2: "Black Player", 0: "None"}

    def __init__(self, handicaps: dict):
        super().__init__()
        self.setWindowTitle("Choose Handicap and Komi")
        self.selected_player = self.index_to_player[handicaps["player"]]
        self.selected_type = handicaps["type"]
        self.selected_value = handicaps["value"]
        self.selected_komi = handicaps["komi"]

        self.init_ui()

        self.setFixedSize(400, 200)

    def init_ui(self):
        layout = QVBoxLayout()

        # Combo box for player selection
        player_layout = QHBoxLayout()
        self.player_label = QLabel("Select Player:")
        self.player_combo = QComboBox()
        self.player_combo.addItems(["None", "White Player", "Black Player"])
        self.player_combo.currentTextChanged.connect(self.update_ui)

        player_layout.addWidget(self.player_label)
        player_layout.addWidget(self.player_combo)

        # Combo box for Komi value
        self.komi_label = QLabel("Komi:")
        self.komi_combo = QComboBox()
        self.komi_combo.addItems([f"{x * 0.5}" for x in range(21)])
        self.komi_combo.setCurrentText(self.selected_komi)
        self.komi_combo.currentTextChanged.connect(self.update_komi)

        player_layout.addWidget(self.komi_label)
        player_layout.addWidget(self.komi_combo)

        layout.addLayout(player_layout)

        # Area for handicap type and value
        self.handicap_layout = QVBoxLayout()

        # Radio buttons for "Point" or "Piece"
        self.type_group = QButtonGroup(self)
        self.point_radio = QRadioButton("Points")
        self.piece_radio = QRadioButton("Pieces")
        self.type_group.addButton(self.point_radio)
        self.type_group.addButton(self.piece_radio)

        self.point_radio.toggled.connect(self.update_value_input)
        self.piece_radio.toggled.connect(self.update_value_input)

        self.handicap_layout.addWidget(self.point_radio)
        self.handicap_layout.addWidget(self.piece_radio)

        # Combo box for entering handicap value
        self.value_label = QLabel("Select Value:")
        self.value_input = QComboBox()
        self.handicap_layout.addWidget(self.value_label)
        self.handicap_layout.addWidget(self.value_input)

        layout.addLayout(self.handicap_layout)

        # OK button
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_ui("None")  # Initialize UI state

    def update_ui(self, player):
        """Update UI based on player selection."""
        self.selected_player = player

        if player == "None":
            self.point_radio.setEnabled(False)
            self.piece_radio.setEnabled(False)
            self.value_label.setEnabled(False)
            self.value_input.setEnabled(False)
        else:
            self.point_radio.setEnabled(True)
            self.piece_radio.setEnabled(True)
            self.update_value_input()  # Update input visibility based on selection

    def update_value_input(self):
        """Update the value input based on the selected handicap type."""
        self.value_input.clear()
        if self.point_radio.isChecked():
            self.values = [f"{x * 0.5}" for x in range(31)]
        elif self.piece_radio.isChecked():
            self.values = [f"{x}" for x in range(6)]
        else:
            self.values = []

        self.value_input.addItems(self.values)
        self.value_label.setEnabled(bool(self.values))
        self.value_input.setEnabled(bool(self.values))

    def update_komi(self, komi):
        """Update the selected Komi value."""
        self.selected_komi = komi

    def get_results(self):
        """Return the selected handicap and Komi information."""
        return {
            "player": self.player_index[self.selected_player],
            "type": (
                "Points"
                if self.point_radio.isChecked()
                else ("Pieces" if self.piece_radio.isChecked() else None)
            ),
            "value": (
                self.value_input.currentText() if self.value_input.isEnabled() else None
            ),
            "komi": self.selected_komi,
        }

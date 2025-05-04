from gui.dialog_utils import BaseDialog
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QRadioButton, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QDialog, QDialogButtonBox

class AddRelationTypeDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Neuer Beziehungstyp", parent)

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit(self)

        self.description_label = QLabel("Beschreibung:")
        self.description_input = QTextEdit(self)

        self.equal_radio = QRadioButton("Gleichwertig", self)
        self.lower_radio = QRadioButton("Untergeordnet", self)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_input)

        self.layout.addWidget(self.equal_radio)
        self.layout.addWidget(self.lower_radio)

        self.equal_radio.setChecked(True)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_data(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        hierarchy_level = 0 if self.equal_radio.isChecked() else 1
        return name, description, hierarchy_level

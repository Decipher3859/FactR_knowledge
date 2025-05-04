from gui.dialog_utils import BaseDialog
from PyQt5.QtWidgets import QLineEdit, QLabel

class CreateProjectDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Neues Projekt erstellen", parent)

        self.project_name_label = QLabel("Projektname:", self)
        self.project_name_input = QLineEdit(self)

        self.layout.addWidget(self.project_name_label)
        self.layout.addWidget(self.project_name_input)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_project_name(self):
        return self.project_name_input.text()

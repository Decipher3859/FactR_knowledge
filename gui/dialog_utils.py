from PyQt5.QtWidgets import (
    QTextEdit, QVBoxLayout, QHBoxLayout,
    QLabel, QRadioButton, QLineEdit,
    QDialog, QDialogButtonBox
)

class BaseDialog(QDialog):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self
        )
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

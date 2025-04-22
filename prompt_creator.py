from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from patterns import *
from tag_manager import *
import os
import re

class PromptCreator(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.project = self.controller.get_project()

        self. setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Eigene Aussage, Gedanke, These hier eingeben...")
        self.input_field.setFixedHeight(60)
        self.layout.addWidget(self.input_field)

        tag_button_layout = QHBoxLayout()

        self.prompt_button = QPushButton("Prompt hinzufügen")

        tag_button_layout.addWidget(self.prompt_button)

        self.layout.addLayout(tag_button_layout)

        self.prompt_button.clicked.connect(lambda: self.add_prompt("prmt"))

        self.setLayout(self.layout)

        self.input_field.clear()

        self.tag_manager = TagManager(self.input_field.toPlainText(), self.project)

    def add_prompt(self, tag):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        source = 0
        id_ = self.tag_manager.get_max_id_from_file(tag) + 1

        wrapped = MARKUP_TEMPLATE.format(tag=tag, source=source, id=id_, text=text)

        file_path = os.path.join(self.project.project_dir, tag_to_file[tag])
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{wrapped}\n")

        self.input_field.clear()

    

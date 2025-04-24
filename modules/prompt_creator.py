from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from patterns import *
from modules.tag_manager import *
import os
import re

class PromptCreator(QWidget):
    def __init__(self, module_manager, controller, instance_id=None, position=None):
        super().__init__()
        self.module_manager = module_manager
        self.controller = controller

        self.module_name = "Prompt Creator"
        self.icon_path = "prompt_creator.png"
        self.instance_id = instance_id

        self.project = self.controller.get_project()
        self.db = self.controller.db_manager

        self.setup_ui()
        print("setup_ui() wurde aufgerufen.")

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

        return self

    def add_prompt(self, tag):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        source_id = 0

        self.controller.db_manager.create_prompt(
            content=text,
            tag=tag,
            source_id=source_id,
        )

        self.input_field.clear()

    
    @property
    def name(self):
        return self.__class__.__name__
    
    def to_dict(self):
        return {
            "name": self.name,
            "instance_id": self.instance_id,
            "position": self.position,
            "icon_path": self.icon_path
        }
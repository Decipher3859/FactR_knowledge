import os
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QSizePolicy, QRadioButton
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from patterns import *
from modules.tag_manager import *

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

        self.controller.reference_changes.connect(self.update_reference_display)
        self.controller.relation_type_added.connect(self.update_relation_type_buttons)

        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.setMinimumSize(500, 300)

        self.reference_label = QLabel("Referenz:")
        self.reference_label.setAlignment(Qt.AlignLeft)
        self.reference_label.setFixedHeight(30)
        self.reference_label.setStyleSheet("font-weight: bold; color: #333; padding: 4px;")
        self.layout.addWidget(self.reference_label)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Eigene Aussage, Gedanke, These hier eingeben...")
        self.input_field.setStyleSheet("font-size:14px; padding 6px;")
        self.input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        input_wrapper = QWidget()
        input_wrapper_layout = QVBoxLayout(input_wrapper)
        input_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        input_wrapper_layout.addWidget(self.input_field)
        input_wrapper.setFixedHeight(self.height() // 2)

        self.layout.addWidget(input_wrapper)

        self.add_relation_type_button = QPushButton("Beziehungstyp hinzufügen")
        self.add_relation_type_button.clicked.connect(self.controller.show_add_relation_type_dialog)
        self.layout.addWidget(self.add_relation_type_button)

        self.relation_type_group = QVBoxLayout()
        self.layout.addLayout(self.relation_type_group)

        tag_button_layout = QHBoxLayout()

        self.prompt_button = QPushButton("Prompt hinzufügen")
        self.prompt_button.setFixedWidth(150)
        self.prompt_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px, 16px;
                font-size: 16px;
                border: none;
                border-radius: 4px;
                }
            QPushButton:hover {
                background-color: #45a049;
                }
            QPushButton:pressed {
                background-color: #3e8e41;
                }
            """)

        tag_button_layout.addWidget(self.prompt_button)

        self.layout.addLayout(tag_button_layout)

        self.prompt_button.clicked.connect(lambda: self.add_prompt("prmt"))

        self.setLayout(self.layout)

        self.input_field.clear()
        self.update_relation_type_buttons()

        return self
    
    def update_reference_display(self, reference_data):
        self.reference_label.setText(f"Referenz: {reference_data['content']}")
    
    def update_relation_type_buttons(self):
        for i in reversed(range(self.relation_type_group.count())):
            widget = self.relation_type_group.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.selected_relation_type_id = None

        relation_types = self.controller.db_manager.get_relation_types()
        for relation in relation_types:
            radio_button = QRadioButton(f"{relation['name']}")
            radio_button.relation_type_id = relation['id']
            radio_button.toggled.connect(self.on_relation_type_selected)
            self.relation_type_group.addWidget(radio_button)

    def on_relation_type_selected(self):
        radio = self.sender()
        if radio.isChecked():
                self.selected_relation_type_id = radio.relation_type_id

    def add_prompt(self, tag):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        
        source_id = 0

        prompt_id = self.controller.db_manager.create_prompt(
            content=text,
            tag=tag,
            source_id=source_id,
        )

        print("Controller Referenz: ", self.controller.get_current_reference())
        reference = self.controller.get_current_reference()
        if reference and self.selected_relation_type_id is not None:
            print("Reference ID: ", reference['id'])
            print("Prompt ID: ", prompt_id)
            self.controller.db_manager.add_prompt_relation(
                prompt_a_id = reference['id'],
                prompt_b_id = prompt_id,
                relation_type_id = self.selected_relation_type_id
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
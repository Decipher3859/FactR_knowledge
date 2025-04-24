from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
import os
from patterns import *

class PromptCollection(QWidget):
    def __init__(self, module_manager, controller, instance_id=None, position=None):
        super().__init__()
        self.module_manager = module_manager
        self.controller = controller

        self.module_name = "PromptCollection"
        self.icon_path = "prompt_collection.png"
        self.instance_id = instance_id

        self.project = controller.get_project()
        self.db = controller.db_manager

        self.setup_ui()
        print("setup_ui() wurde aufgerufen.")
        

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Prompt Collection sichtbar"))
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(["Kategorie", "Pos", "Inhalt", "Quelle"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.setSortingEnabled(True)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        
        self.refresh_prompt_table()
        self.db.prompt_added.connect(self.refresh_prompt_table)
        
        return self

    def refresh_prompt_table(self):
        print("refresh_prompt_table() wird aufgerufen.")
        self.table.setRowCount(0)
        prompts = self.db.get_all_prompts()

        for prompt in prompts:
            _, content, tag, source, local_id, _, = prompt
            self.add_row(content, tag, str(local_id), source)

    def add_row(self, tag, local_id, content, source):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        self.table.setItem(row_position, 0, QTableWidgetItem(tag))
        self.table.setItem(row_position, 1, QTableWidgetItem(local_id))

        item = QTableWidgetItem(content)
        item.setToolTip(content)
        item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.table.setItem(row_position, 2, item)

        self.table.setItem(row_position, 3, QTableWidgetItem(source))

        font_metrics = QFontMetrics(self.table.font())
        text_width = self.table.columnWidth(2)

        bounding_rect = font_metrics.boundingRect(0, 0, text_width, 0, Qt.TextWordWrap, content)
        line_height = font_metrics.lineSpacing()

        required_lines = max(1, bounding_rect.height() // line_height)
        visible_lines = min(required_lines, 3)

        self.table.setRowHeight(row_position, visible_lines * line_height + 6)


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
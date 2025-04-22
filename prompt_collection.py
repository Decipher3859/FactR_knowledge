from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
import os
from patterns import *

class PromptCollection(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.project = controller.get_project()
        self.db_manager = controller.get_db_manager()
        self.setup_ui()
        
        self.refresh_prompt_table

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(["Kategorie", "Pos", "Inhalt", "Quelle"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.setSortingEnabled(True)

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def refresh_prompt_table(self):
        self.table.setRowCount(0)
        prompts = self.db_manager.get_all_prompts()

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



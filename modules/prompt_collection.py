from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout,QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QTreeWidget, QTreeWidgetItem,
    QSizePolicy, 
)
from PyQt5.QtGui import QFont, QFontMetrics, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize
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

        self.tree.itemClicked.connect(self.update_reference_from_tree)        

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Prompt Hierarchy"])
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)
        
        self.refresh_prompt_tree()
        self.controller.prompt_added.connect(self.refresh_prompt_tree)
        
        return self

    def refresh_prompt_tree(self):
        expanded_ids = self.get_expanded_prompt_ids()
        print("EXPANDED IDS: ", expanded_ids)

        self.tree.clear()
        root_prompts = self.db.get_root_prompts()
        for prompt in root_prompts:
            self.add_prompt_item(prompt)
        self.restore_expanded_prompt_ids(expanded_ids)

    def add_prompt_item(self, prompt, parent_item=None):
        relation_name = prompt.get('relation_name', "UNKNOWN").upper()

        item = QTreeWidgetItem()
        item.setData(0, Qt.UserRole, prompt)

        widget = PromptItemWidget(relation_name, prompt['content'])

        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        self.tree.setItemWidget(item, 0, widget)

        self.add_children_to_item(item, prompt['id'])

    def add_children_to_item(self, parent_item, parent_id):
        children = self.db.get_direct_children(parent_id)
        for child_prompt in children:
            self.add_prompt_item(child_prompt, parent_item)

    def restore_expanded_prompt_ids(self, ids_to_expand):
        if not ids_to_expand:
            ids_to_expand = set()

        def recurse(item):
            if item is None:
                return
            prompt = item.data(0, Qt.UserRole)
            if prompt and prompt.get('id') in ids_to_expand:
                item.setExpanded(True)
            for i in range(item.childCount()):
                recurse(item.child(i))
        
        for i in range(self.tree.topLevelItemCount()):
            recurse(self.tree.topLevelItem(i))

    def get_expanded_prompt_ids(self):
        def recurse(item):
            ids = []
            if item.isExpanded():
                prompt = item.data(0, Qt.UserRole)
                if prompt:
                    ids.append(prompt.get('id'))
            for i in range(item.childCount()):
                ids.extend(recurse(item.child(i)))
            return ids
        ids = recurse(self.tree.invisibleRootItem())
        return ids

    def update_reference_from_table(self, item, column):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        id = self.table.item(row, 0).text()
        local_id = self.table.item(row, 1).text()
        content = self.table.item(row, 2).text()
        source = self.table.item(row, 3).text()
        
        reference_data = {
            "id": id,
            "local_id": local_id,
            "content": content,
            "source": source
        }
        self.controller.set_current_reference(reference_data)

    def update_reference_from_tree(self, item, column):
        prompt = item.data(0, Qt.UserRole)
        if not prompt:
            return
        
        reference_data = {
            "id": prompt.get("id"),
            "local_id": prompt.get("local_id"),
            "content": prompt.get("content"),
            "source": prompt.get("source")
        }

        self.controller.set_current_reference(reference_data)

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

class PromptItemWidget(QWidget):
    def __init__(self, relation_name, content):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if relation_name != "UNKNOWN":
            label = QLabel(f"{relation_name}")
            label.setStyleSheet("""
                background-color: #404040; 
                color: white; 
                font-weight: bold; 
                font-size: 8px;
                margin-top: 2px; 
                padding: 1px 4px;
            """)

            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            label.setFixedWidth(label.sizeHint().width())
            layout.addWidget(label)

        content_label = QLabel(content)
        layout.addWidget(content_label)

        self.setLayout(layout)


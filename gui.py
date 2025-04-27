import os
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QTextBrowser, QVBoxLayout, QHBoxLayout, 
    QWidget, QStackedWidget, QAction, QFileDialog, QMessageBox, QMenu, QMenuBar, QToolBar, QSplitter, QTreeWidget, QTreeWidgetItem,
    QLabel, QPushButton, QSpacerItem, QSizePolicy, QDockWidget, QInputDialog, QDialog, QDialogButtonBox, QLineEdit

)
from PyQt5.QtGui import QIcon
from modules.prompt_creator import PromptCreator
from modules.prompt_collection import PromptCollection
from modules.source_analyzer import SourceAnalyzer
from modules.layout_templates import *



class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("FactR")
        self.setGeometry(100, 100, 800, 600)
        # self.showMaximized()

        self.controller = controller
        self.project = self.controller.project_manager.get_project()
        self.module_manager = self.controller.module_manager

        self.create_menu()
        
        self.toolbar = QToolBar("Kontext_Werkzeugleiste")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.workspace = SplitContainer(Qt.Vertical, self.module_manager)
        self.setCentralWidget(self.workspace)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Datei")

        create_project_action = QAction("Neues Projekt erstellen", self)
        create_project_action.triggered.connect(self.show_create_project_dialog)
        file_menu.addAction(create_project_action)

        open_action = QAction("Projekt öffnen...", self)
        open_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_action)

    def show_create_project_dialog(self):
        dialog = CreateProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            project_name = dialog.get_project_name()
            self.controller.initialize_project(project_name)
            print("Project Name: ", project_name)
            self.setWindowTitle(project_name)

    def open_project_dialog(self):
        start_path = os.path.expanduser("~/DiscourseAnalyzer-Projekte/")
        selected_dir = QFileDialog.getExistingDirectory(self, "Projektordner wählen", start_path)

        if selected_dir:
            project_name = os.path.basename(selected_dir)
            self.project.load_project(project_name)
            self.project = self.project.get_project()
            self.db_manager = self.project.get_db_manager()
            self.setWindowTitle(self.project.project_name)
            QMessageBox.information(self, "Projekt geöffnet", f"Projekt '{project_name}' wurde geladen.")

            self.prompt_collection.project = self.project
            self.prompt_collection.db_manager = self.db_manager
            self.prompt_collection.refresh_prompt_table()

            self.source_analyzer.project = self.project
            self.source_analyzer.load_sources_from_db()

    def setup_module_buttons(self):
        self.module_buttons = {}
        print("Module werden geladen")
        for module_name in self.module_manager.get_available_modules():
            print("Module: ", module_name)
            print("Action wird erstellt")
            action = QAction(module_name, self)
            print("Action: ", action)
            print("Trigger wird gesetzt")
            action.triggered.connect(lambda checked, name=module_name: self.open_insert_menu(name))
            print("Action wird zur Toolbar hinzugefügt")
            self.toolbar.addAction(action)
            
            self.module_buttons[module_name] = action


    def load_workspace_structure(self, project):
        try:
            self.workspace.deleteLater()
            self.workspace = SplitContainer(Qt.Vertical, self.module_manager)
            self.setCentralWidget(self.workspace)

            file_path = os.path.join(project.project_dir, f"{project.project_name}.proj")
            with open(file_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)

                workspace_structure = project_data.get("open_instances", None)
                if workspace_structure:
                    if isinstance(workspace_structure, list):
                        for module_info in workspace_structure:
                            if module_info.get("type") == "module":
                                module = self.module_manager.add_instance(
                                    module_info["name"],
                                    module_info["instance_id"]
                                )
                                position = module_info["position"]
                                self.workspace.add_from_structure(position, module)
                    else:
                        print("Liste ist kein gültiges Format.")
                else:
                    print("Keine Struktur für den Arbeitsbereich gefunden.")
        except FileNotFoundError:
            print("Projektdatei nicht gefunden.")

class SplitContainer(QWidget):
    def __init__(self, orientation=Qt.Vertical, module_manager=None):
        super().__init__()
        self.module_manager = module_manager
        
        self.setStyleSheet("background-color: lightblue;")
        
        self.splitter = QSplitter(orientation)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

    def add_module(self, module):
        self.splitter.addWidget(module)

    def add_split(self, new_container):
        
        self.splitter.addWidget(new_container)
        self.splitter.setSizes([640, 480])
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

    def find_children(self):
        return [self.splitter.widget(i) for i in range(self.splitter.count())]  
    

    def add_from_structure(self, position, module):
        if not position:
            self.add_module(module)
            return
        
        index = position[0]
        remaining_position = position[1:]

        if self.splitter.count() <= index:
            new_split = SplitContainer(Qt.Horizontal if len(position) % 2 == 0 else Qt.Vertical, self.module_manager)
            self.splitter.insertWidget(index, new_split)
        else:
            widget = self.splitter.widget(index)
            if not isinstance(widget, SplitContainer):
                new_split = SplitContainer(Qt.Horizontal if len(position) % 2 == 0 else Qt.Vertical, self.module_manager)
                self.splitter.insertWidget(index, new_split)
            else:
                new_split = widget
        new_split.add_from_structure(remaining_position, module)
    
    def to_structure(self, current_path=None):
        if current_path is None:
            current_path = []

        structure = []

        for i in range(self.splitter.count()):
            instance = self.splitter.widget(i)
            if isinstance(instance, SplitContainer):
                structure.extend(instance.to_structure(current_path + [i]))
            else:
                structure.append({
                    "type": "module",
                    "name": instance.name,
                    "instance_id": instance.instance_id,
                    "position": current_path + [i]
                })
        return structure

    @staticmethod
    def from_dict(self, data):
        if data["type"] != "split":
            raise ValueError("Invalid data format for SplitContainer")
        
        orientation = Qt.Horizontal if data["orientation"] == "horizontal" else Qt.Vertical
        container = SplitContainer(orientation)

        for child in data.get("children", ()):
            if child["type"] == "split":
                child_container = SplitContainer.from_dict(child)
                container.add_module(child_container)
            elif child["type"] == "module":
                name = child["name"]
                instance_id = child["instance_id"]
                module = self.controller.module_manager.get_instance(name, instance_id)

                if module is None:
                    print(f"Modul nicht gefunden: {name} mit ID {instance_id}")
                    continue

                module.position = child.get("position", 0)
                container.add_module(module)
            else: print(f"Unbekannter Typ in Container: {child['type']}")

        return container

    def to_dict(self):
        container_dict = {
            "type": "split",
            "orientation": "horizontal" if self.orientation() == Qt.Horizontal else "vertical",
            "children": []
        }

        for i in range(self.splitter.count()):
            widget = self.splitter.widget(i)

            if isinstance(widget, SplitContainer):
                container_dict["children"].append(widget.to_dict())

            elif hasattr(widget, "to_dict") and callable(widget.to_dict):
                container_dict["children"].append({
                    "type": "module",
                    "data": widget.to_dict()
                })
        
        return container_dict

class InsertModuleMenu(QTreeWidget):
    def __init__(self, open_instances, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Modulstruktur einfügen")
        self.build_menu(open_instances)

    def build_menu(self, instances):
        for instance in instances:
            if instance["type"] == "module":
                self.add_module(instance["position"], instance["name"], instance["instance_id"])

    def add_module(self, position, name, instance_id):
        current_item = self

        for idx in position:
            child = None

            # Bestehendes Kind suchen
            if isinstance(current_item, QTreeWidget):
                for i in range(current_item.topLevelItemCount()):
                    item = current_item.topLevelItem(i)
                    if int(item.text(0)) == idx:
                        child = item
                        break
            else:
                for i in range(current_item.childCount()):
                    item = current_item.child(i)
                    if int(item.text(0)) == idx:
                        child = item
                        break

            # Wenn nicht gefunden, neues Item erstellen
            if not child:
                child = QTreeWidgetItem()
                child.setText(0, str(idx))
                if isinstance(current_item, QTreeWidget):
                    current_item.addTopLevelItem(child)
                else:
                    current_item.addChild(child)

            current_item = child

        # Modul selbst hinzufügen
        module_item = QTreeWidgetItem()
        module_item.setText(0, f"Modul: {name} (ID: {instance_id})")
        current_item.addChild(module_item)

        # Platzhalter für neue Zeile und neue Spalte hinzufügen
        add_row = QTreeWidgetItem()
        add_row.setText(0, "[+] Neuer Slot")
        current_item.addChild(add_row)

        add_col = QTreeWidgetItem()
        add_col.setText(0, "[+] Neue Spalte")
        current_item.addChild(add_col)


class CreateProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt erstellen")

        self.layout = QVBoxLayout(self)

        self.project_name_label = QLabel("Projektname")
        self.layout.addWidget(self.project_name_label)

        self.project_name_input = QLineEdit(self)
        self.layout.addWidget(self.project_name_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_project_name(self):
        return self. project_name_input.text()

        




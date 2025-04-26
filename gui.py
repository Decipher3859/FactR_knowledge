import os
import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QTextBrowser, QVBoxLayout, QHBoxLayout, 
    QWidget, QStackedWidget, QAction, QFileDialog, QMessageBox, QMenu, QMenuBar, QToolBar, QSplitter,
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

    def open_insert_menu(self, module_name):
        menu = QMenu()
        
        file_path = os.path.join(self.project.project_dir, f"{self.project.project_name}.proj")
        with open(file_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)

                structure = project_data["open_instances"]
                first_row = structure[0]["children"] if structure and structure[0]["type"] == "split" else []

                num_slots = len(first_row) + 1

                for index in range(num_slots):
                    action = QAction(f"Slot {index + 1}", self)
                    action.triggered.connect(lambda checked, idx=index: self.insert_module_at(idx, module_name))
                    menu.addAction(action)

        button_pos = self.sender().parentWidget().mapToGlobal(self.sender().parentWidget().pos())
        menu.exec_(button_pos)

    def insert_module_at(self, index, module_name):
        print(f"Modul {module_name} an Position {index} einfügen")
        
        


        structure = self


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
                        for dictionary in workspace_structure:
                            if isinstance(dictionary, dict):
                                self.workspace.add_from_structure(dictionary)
                            else:
                                print("Ein Element in der Liste ist kein gültiges Dictionary.")
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
    
    def add_from_structure(self, structure_dict):
        if isinstance(structure_dict, dict):
            if structure_dict["type"] == "split":
                print("instanzieren eines neuen SplitContainers mit der Orientierung:", structure_dict["orientation"])
                child_split = SplitContainer(Qt.Orientation(structure_dict["orientation"]), self.module_manager)
                print("Füge einen neuen SplitContainer hinzu")
                self.add_split(child_split)
                print("")
                for child in structure_dict["children"]:
                    print("")
                    child_split.add_from_structure(child)
                print("")
                child_split.show()
                print(f"{child_split} hinzugefügt. - Sichtbar:{child_split.isVisible()}")
            elif structure_dict["type"] == "module":
                module = self.module_manager.add_instance(
                    structure_dict["name"],
                    structure_dict["instance_id"]
                )
                self.add_module(module)
                print(f"Struktur hinzugefügt: {structure_dict}")
                print(f"Modul {module} hinzugefügt. - Sichtbar:{module.isVisible()}")

                print("")
                if len(self.splitter.children()) == 1:
                    print("")
                    self.splitter.setStretchFactor(0, 1)
                    print("")
                    self.splitter.setSizes([1000])     
                    print("")
            self.splitter.setSizes([500, 500])
            
        else:
            print("Struktur ist kein gültiges Dictionary.")


    def to_structure(self):
        children = []
        for module in self.find_children():
            if isinstance(module, SplitContainer):
                children.append(module.to_structure())
            else:
                module_data = {
                    "type": "module",
                    "name": module.name,
                    "instance_id": module.instance_id,
                    "position": module.position
                }
                children.append(module_data)
        return {
            "type": "split",
            "orientation": self.orientation(),
            "children": children
        }
    
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

        




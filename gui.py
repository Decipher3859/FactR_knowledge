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
        self.setWindowTitle("SourceAnalyzer")
        self.setGeometry(100, 100, 800, 600)
        # self.showMaximized()

        self.controller = controller
        self.module_manager = self.controller.module_manager

        self.create_menu()
        
        # label = QLabel("Ist das Fenster sichtbar?")
        # label.setStyleSheet("font-size: 24px; color: red;")
        # self.setCentralWidget(label)

        # label = QLabel("Main Window sichtbar")
        # label.setAlignment(Qt.AlignCenter)
        # self.setCentralWidget(label)
        # self.show()  # unbedingt show() aufrufen


        self.context_toolbar = QToolBar("Kontext_Werkzeugleiste")
        self.addToolBar(Qt.TopToolBarArea, self.context_toolbar)



        self.workspace = SplitContainer(Qt.Vertical, self.module_manager)
        self.workspace.add_from_structure(empty_split_container())

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
            self.project_manager.load_project(project_name)
            self.project = self.project_manager.get_project()
            self.db_manager = self.project_manager.get_db_manager()
            self.setWindowTitle(self.project.project_name)
            QMessageBox.information(self, "Projekt geöffnet", f"Projekt '{project_name}' wurde geladen.")

            self.prompt_collection.project = self.project
            self.prompt_collection.db_manager = self.db_manager
            self.prompt_collection.refresh_prompt_table()

            self.source_analyzer.project = self.project
            self.source_analyzer.load_sources_from_db()


    def create_sidebar(self):
        if not hasattr(self, 'sidebar_dock'):
            self.sidebar = QWidget(self)
            self.sidebar_layout = QVBoxLayout(self.sidebar)

            self.sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.sidebar_dock = QDockWidget("Sidebar", self)
            self.sidebar_dock.setWidget(self.sidebar)
            self.sidebar_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            self.sidebar_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

            self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar_dock)
        

    def update_sidebar_with_modules(self):
        if not hasattr(self, 'sidebar'):
            print("Sidebar nicht gefunden.")
            return
        
        print("Sidebar_Layout:", self.sidebar_layout)
        for i in reversed(range(self.sidebar_layout.count())):
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not hasattr(self, 'modules') or not self.modules:
            print("Keine Module gefunden.")
            return
        
        for module in self.modules:
            print("Module Button hinzugefügt::", module)
            self.add_sidebar_button(self.sidebar_layout, module.name, module.icon_path, self.change_view)

    def add_sidebar_button(self, layout, text, icon_path, action):
        button = QPushButton(text)
        if icon_path:    
            button.setIcon(QIcon(icon_path))
        button.clicked.connect(action)
        layout.addWidget(button)

    def load_workspace_structure(self, project):
        try:
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
                        self.workspace.add_from_structure(workspace_structure)
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

    def add_module(self, module_widget):
        self.splitter.addWidget(module_widget)

    def add_split(self, orientation=Qt.Horizontal):
        new_container = SplitContainer(orientation, self.module_manager)
        self.splitter.addWidget(new_container)
        return new_container

    def find_children(self):
        return [self.splitter.widget(i) for i in range(self.splitter.count())]  
    
    def add_from_structure(self, structure_dict):
        if isinstance(structure_dict, dict):
            if structure_dict["type"] == "split":
                child_split = SplitContainer(Qt.Orientation(structure_dict["orientation"]), self.module_manager)
                self.add_split(child_split)
                for child in structure_dict["children"]:
                    child_split.add_from_structure(child)
            elif structure_dict["type"] == "module":
                module = self.module_manager.add_instance(
                    structure_dict["name"],
                    structure_dict["instance_id"]
                )
                self.add_module(module)
            self.splitter.setSizes([500,500])
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

        




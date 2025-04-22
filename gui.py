import os
import markdown
import re
import shutil
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QTextBrowser, QVBoxLayout, QHBoxLayout, 
    QWidget, QStackedWidget, QAction, QFileDialog, QMessageBox, QMenu, QMenuBar, QToolBar,
    QLabel, QPushButton, QSpacerItem, QSizePolicy, QDockWidget, QInputDialog, QDialog, QDialogButtonBox, QLineEdit

)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QIcon
from prompt_creator import PromptCreator
from prompt_collection import PromptCollection
from source_analyzer import SourceAnalyzer



class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("SourceAnalyzer")
        self.setGeometry(100, 100, 800, 600)
        # self.showMaximized()

        self.controller = controller

        central_widget = QWidget(self)
        central_layout = QHBoxLayout(central_widget)

        self.sidebar = self.create_sidebar()
        central_layout.addWidget(self.sidebar, 1)

        self.stack = QStackedWidget()

        central_layout.addWidget(self.stack, 4)

        self.setCentralWidget(central_widget)

        self.create_menu()
        
        self.context_toolbar = QToolBar("Kontext_Werkzeugleiste")
        self.addToolBar(Qt.TopToolBarArea, self.context_toolbar)

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
            self.source_analyzer.load_sources_from_dir()

    # def open_file(self):
    #     path, _ = QFileDialog.getOpenFileName(self, "Datei öffnen", "", "Markdown-Dateien (*.md);;Alle Dateien (*)")
    #     if path:
    #         try:
    #             with open(path, 'r', encoding='utf-8') as file:
    #                 content = file.read()
    #                 self.load_text(content)
    #         except Exception as e:
    #             QMessageBox.warning(self, "Fehler", f"Konnte Datei nicht öffnen:\n{str(e)}")

    def create_sidebar(self):
        sidebar = QWidget(self)
        sidebar_layout = QVBoxLayout(sidebar)

        self.add_sidebar_button(sidebar_layout, "Sammlung", "collection_icon.png", self.show_collection)
        self.add_sidebar_button(sidebar_layout, "Beziehungen", "Map_icon.png", self.show_map)
        self.add_sidebar_button(sidebar_layout, "Ablauf", "timeline_icon.png", self.show_timeline)
        self.add_sidebar_button(sidebar_layout, "Quellen", "source_icon.png", self.show_source)
        self.add_sidebar_button(sidebar_layout, "Prompt", "prompt_icon.png", self.create_prompt)

        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        sidebar.setLayout(sidebar_layout)
        self.setMenuWidget(sidebar)

        return sidebar

    def add_sidebar_button(self, layout, text, icon_path, action):
        button = QPushButton(text)
        button.setIcon(QIcon(icon_path))
        button.clicked.connect(action)
        layout.addWidget(button)
    
    def show_collection(self):
        self.update_context_toolbar("show_collection")
        self.stack.setCurrentIndex(0)

    def show_map(self):
        self.update_context_toolbar("show_map")
        self.stack.setCurrentIndex(1)

    def show_timeline(self):
        self.update_context_toolbar("show_timeline")
        self.stack.setCurrentIndex(2)

    def show_source(self):
        self.update_context_toolbar("show_source")
        self.stack.setCurrentIndex(3)

    def create_prompt(self):
        self.update_context_toolbar("create_prompt")
        self.stack.setCurrentIndex(4)

    def initialize_modules(self):
        self.prompt_collection = PromptCollection(self.controller)
        self.map_widget = QLabel("Beziehungen")
        self.timeline_widget = QLabel("Zeitverlauf")
        self.source_analyzer = SourceAnalyzer(self.controller)
        self.prompt_creator = PromptCreator(self.controller)

        self.stack.addWidget(self.prompt_collection)  
        self.stack.addWidget(self.map_widget)         
        self.stack.addWidget(self.timeline_widget)    
        self.stack.addWidget(self.source_analyzer)    
        self.stack.addWidget(self.prompt_creator)     

    def update_context_toolbar(self, context):
        self.context_toolbar.clear()

        if context == "show_collection":
            action = QAction("Sammlung", self)
            action.triggered.connect(self.show_collection)
            self.context_toolbar.addAction(action)

        elif context == "show_map":
            action = QAction("Struktur", self)
            action.triggered.connect(self.show_map)
            self.context_toolbar.addAction(action)

        elif context == "show_timeline":
            action = QAction("Ablauf", self)
            action.triggered.connect(self.show_timeline)
            self.context_toolbar.addAction(action)

        elif context == "show_source":
            action = QAction("Quelle", self)
            action.triggered.connect(self.show_source)
            self.context_toolbar.addAction(action)

        elif context == "create_prompt":
            action = QAction("Prompt", self)
            action.triggered.connect(self.create_prompt)
            self.context_toolbar.addAction(action)

    
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

        




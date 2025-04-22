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
from modules.prompt_creator import PromptCreator
from modules.prompt_collection import PromptCollection
from modules.source_analyzer import SourceAnalyzer



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
            self.source_analyzer.load_sources_from_db()

    def create_sidebar(self):
        if not hasattr(self, 'sidebar'):
            self.sidebar = QWidget(self)
            self.sidebar_layout = QVBoxLayout(self.sidebar)

            self.sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

            self.sidebar.setLayout(self.sidebar_layout)
            self.setMenuWidget(self.sidebar)

    def create_module_ui(self):
        module_manager = self.controller.module_manager
        self.modules = module_manager.get_modules()
        
        if not self.modules:
            print("Keine Module gefunden.")
            return  
        
        for module in self.modules:
            try:
                widget = module.setup_ui()
                if widget:
                    self.stack.addWidget(widget)
                else:
                    print(f"Modul {module.name} hat kein UI Model zurückgegeben.")
            except Exception as e:
                print(f"Fehler beim Erstellen der UI für Modul {module.name}: {e}")
        
        self.update_sidebar_with_modules()

    def update_sidebar_with_modules(self):
        if not hasattr(self, 'sidebar'):
            print("Sidebar nicht gefunden.")
            return
        
        for i in reversed(range(self.sidebar.count())):
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not hasattr(self, 'modules') or not self.modules:
            print("Keine Module gefunden.")
            return
        
        for module in self.modules:
            self.add_sidebar_button(self.sidebar_layout, module.name, module.icon_path, self.change_view)

    def add_sidebar_button(self, layout, text, icon_path, action):
        button = QPushButton(text)
        if icon_path:    
            button.setIcon(QIcon(icon_path))
        button.clicked.connect(action)
        layout.addWidget(button)
    
    def change_view(self):
        sender = self.sender()
        if sender:
            module_name = sender.text()

            for i, module in enumerate(self.modules):
                if module.name == module_name:
                    self.stack.setCurrentIndex(i)
                    self.update_context_toolbar(module_name)
                    break

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

        




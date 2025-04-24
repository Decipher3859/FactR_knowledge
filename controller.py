import json
from project_manager import ProjectManager
from database_manager import DatabaseManager
from module_manager import ModuleManager
from gui import MainWindow
from modules.source_analyzer import *
from modules.prompt_collection import *
from modules.layout_templates import *

class Controller:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.db_manager = None
        
        self.module_manager = ModuleManager(self)
        print("ModuleManager im Controller: ", self.module_manager)

        self.main_window = MainWindow(self)

    def start_application(self):
        self.main_window.show()
        if self.load_last_project():
            print("load_last_project(): ", self.load_last_project())
            db_conf = self.project_manager.database
            print("db_conf: ", db_conf)
            self.db_manager = DatabaseManager(**db_conf)
            self.main_window.load_workspace_structure(self.project_manager.get_project())
            self.main_window.setWindowTitle(self.project_manager.get_project().project_name)
        else:
            self.main_window.show_create_project_dialog()

    def initialize_project(self, project_name):
        project = self.project_manager.create_project(project_name)
        db_config = project.database
        self.db_manager = DatabaseManager(**db_config)
        self.db_manager.create_database()
        self.db_manager.create_tables()

        self.main_window.workspace.add_from_structure(default_new_project_structure())
        self.main_window.setWindowTitle(project_name)
    
    def load_project(self, project_name):
        self.project_manager.load_project(project_name)
        self.project = self.project_manager.get_project()
        self.db_manager = DatabaseManager(**self.project.database)
        self.main_window.setWindowTitle(project_name)

    def load_last_project(self):
        if self.project_manager.load_last_project():
            self.db_manager = self.get_db_manager()
            print(f"Projekt {self.project_manager.get_project().project_name} wurde geladen.")
            return True
        else:
            print("Kein letztes Projekt gefunden.")
            return False
    
    def set_module_manager(self, module_manager):
        self.module_manager = module_manager

    def get_project(self):
        return self.project_manager.get_project()
    
    def get_db_manager(self):
        return self.db_manager

    def show_create_project_dialog(self):
        self.main_window.show_create_project_dialog()



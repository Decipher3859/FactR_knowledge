import json
from PyQt5.QtCore import QObject, pyqtSignal
from project_manager import ProjectManager
from database_manager import DatabaseManager
from module_manager import ModuleManager
from gui.gui import MainWindow
from modules.source_analyzer import *
from modules.prompt_collection import *
from modules.layout_templates import *

class Controller(QObject):
    reference_changes = pyqtSignal(dict)
    relation_type_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.db_manager = None
        
        self.module_manager = ModuleManager(self)
        print("ModuleManager im Controller: ", self.module_manager)

        self.main_window = MainWindow(self)

        self.current_reference = None


    def start_application(self):
        self.main_window.show()
        if self.load_last_project():
            print("load_last_project(): ", self.load_last_project())
            db_conf = self.project_manager.database
            print("db_conf: ", db_conf)
            self.db_manager = DatabaseManager(**db_conf)
            self.main_window.load_workspace_structure(self.project_manager.get_project())
            print("Module Buttons werden gesetzt")
            self.main_window.setup_module_buttons()
            self.main_window.setWindowTitle(self.project_manager.get_project().project_name)
        else:
            self.main_window.show_create_project_dialog()

    def initialize_project(self, project_name):
        project = self.project_manager.create_project(project_name)
        db_config = project.database
        self.db_manager = DatabaseManager(**db_config)
        self.db_manager.create_database()
        self.db_manager.create_tables()

        self.main_window.load_workspace_structure(self.project_manager.get_project())
        print("Module Buttons werden gesetzt")
        self.main_window.setup_module_buttons()
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




# Modulverwaltung
    def set_current_reference(self, prompt_data):
        self.current_reference = prompt_data
        self.reference_changes.emit(prompt_data)
        print("set_current_reference: ", prompt_data)

    def get_current_reference(self):
        print("get_current_reference: ", self.current_reference)
        return self.current_reference
    
    def show_add_relation_type_dialog(self):
        self.main_window.show_add_relation_type_dialog()

    def add_relation_type(self, name, description, hierarchy_level):
        self.db_manager.add_relation_type(name, description, hierarchy_level)
        self.relation_type_added.emit()

        



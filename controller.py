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
    prompt_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.db_manager = None
        
        self.module_manager = ModuleManager(self)
        
        self.main_window = MainWindow(self)

        self.current_reference = None


    def start_application(self):
        self.main_window.show()
        if self.load_last_project():
            db_conf = self.project_manager.database
            self.db_manager = DatabaseManager(**db_conf)
            self.main_window.load_workspace_structure(self.project_manager.get_project())
            self.main_window.setup_module_buttons()
            self.main_window.setWindowTitle(self.project_manager.get_project().project_name)
        else:
            self.main_window.show_create_project_dialog()

    def initialize_project(self, project_name):
        self.module_manager.clear_instances()
        project = self.project_manager.create_project(project_name)
        db_config = project.database

        project.set_last_project()
    
        self.db_manager = DatabaseManager(**db_config)
        self.db_manager.create_database()
        self.db_manager.create_tables()
        self.db_manager.ensure_default_relation_types()

        self.main_window.load_workspace_structure(self.project_manager.get_project())
        self.main_window.setup_module_buttons()
        self.main_window.setWindowTitle(project_name)
    
    def load_project(self, project_name):
        self.project_manager.load_project(project_name)
        self.project = self.project_manager.get_project()
        self.project.set_last_project(project_name)
        self.db_manager = DatabaseManager(**self.project.database)
        self.main_window.setWindowTitle(project_name)

    def load_last_project(self):
        if self.project_manager.load_last_project():
            self.db_manager = self.get_db_manager()
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
    def create_prompt(self, content, source_id, relation_type_id=None):
        prompt_id = self.db_manager.create_prompt(content, source_id)
        reference = self.get_current_reference()
        if reference and relation_type_id is not None:
            self.db_manager.add_prompt_relation(
                prompt_a_id = reference['id'],
                prompt_b_id = prompt_id,
                relation_type_id = relation_type_id
            )

        self.prompt_added.emit()
        
        return prompt_id
    
    def show_add_relation_type_dialog(self):
        self.main_window.show_add_relation_type_dialog()

    def add_relation_type(self, name, description, hierarchy_level):
        self.db_manager.add_relation_type(name, description, hierarchy_level)
        self.relation_type_added.emit()

    def set_current_reference(self, prompt_data):
        self.current_reference = prompt_data
        self.reference_changes.emit(prompt_data)

    def get_current_reference(self):
        return self.current_reference



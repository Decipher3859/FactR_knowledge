import json
from project_manager import ProjectManager
from database_manager import DatabaseManager
from gui import MainWindow
from source_analyzer import *
from prompt_collection import *

class Controller:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.db_manager = None

        self.main_window = MainWindow(self)

    def start_application(self):
        print("Start application")
        self.main_window.show()
        print("self.main_window: ", self.main_window)
        if self.load_last_project():
            print("load_last_project(): ", self.load_last_project)
            db_conf = self.project_manager.get_db_manager()
            print("db_conf: ", db_conf)
            self.db_manager = DatabaseManager(**db_conf)
        else:
            self.main_window.show_create_project_dialog()

    def initialize_project(self, project_name):
        project = self.project_manager.create_project(project_name)
        db_config = project.database
        self.db_manager = DatabaseManager(**db_config)
        self.db_manager.create_database()
        self.db_manager.create_tables()
        self.main_window.initialize_modules()

    def load_last_project(self):
        if self.project_manager.load_last_project():
            self.db_manager = self.project_manager.get_db_manager()
            print(f"Projekt {self.project_manager.get_project().project_name} wurde geladen.")
        else:
            print("Kein letztes Projekt gefunden.")

    def get_project(self):
        return self.project_manager.get_project()
    
    def get_db_manager(self):
        return self.db_manager

    def show_create_project_dialog(self):
        self.main_window.show_create_project_dialog()

    def handle_prompt_added(self):
        print("Neues Prompt hinzugefügt. Auffrischen der Tabelle...")
        
        self.prompt_collection.refresh_prompt_table()



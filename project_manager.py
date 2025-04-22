import os
import json
from datetime import datetime

class ProjectManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.project = None
        return cls._instance
    
    def create_project(self, project_name):
        base_path = os.path.expanduser("~/ResearchAnalyzer-Projekte")
        print("Base_path: ", base_path)
        self.project_name = project_name
        print("Project Name: ", self.project_name)
        self.project_dir = os.path.join(base_path, project_name)
        print("Project dir: ", self.project_dir)
        os.makedirs(self.project_dir, exist_ok=True)
        self.proj_file = os.path.join(self.project_dir, f"{project_name}.proj")
        source_dir = os.path.join(self.project_dir, "sources")
        os.makedirs(source_dir, exist_ok=True)

        self.project_data = {
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "database": {
                "database": f"proj_{self.project_name}",
                "host": "localhost",
                "user": "DAuser",
                "password": "5J#Y2j8B6hFwhpNvY67Gv#EJaXGpc2ZM",
            },
            "tags": [],
            "parameter": [],
            "paths": {
                "project_path": self.project_dir,
                "source_folder": os.path.join(self.project_dir, "sources")
            }
        }

        with open(self.proj_file, "w", encoding="utf-8") as f:
            json.dump(self.project_data, f, indent=4)

        return self

    def load_project(self, project_name):
        base_path = os.path.expanduser("~/ResearchAnalyzer-Projekte")
        self.project_dir = os.path.join(base_path, project_name)
        self.proj_file = os.path.join(self.project_dir, f"{project_name}.proj")

        if not os.path.exists(self.proj_file):
            raise FileNotFoundError(f"Projektdatei {self.proj_file} nicht gefunden.")
        
        with open(self.proj_file, "r", encoding="utf-8") as f:
            self.project_data = json.load(f)

            self.project_name = project_name

    def load_last_project(self):
        try:
            with open("config.json", "r") as config_file:
                data = json.load(config_file)
                project_name = data.get("last_project")
                if project_name:
                    self.load_project(project_name)
                    return True
                else:
                    print("Kein letztes Projekt gefunden.")
                    return False
        except FileNotFoundError:
            print("Konfigurationsdatei nicht gefunden")

    def get_project(self):
        return self.project
    
    @property
    def source_dir(self):
        return self.project_data.get("paths", {}).get("source_folder", "")
    
    @property
    def database(self):
        return self.project_data.get("database", {})
    
    @property
    def name(self):
        return self.project_data.get("project_name", "")
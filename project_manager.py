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

        self.project_name = project_name
        self.project_dir = os.path.join(base_path, project_name)

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
            },
            "available_modules": [
                "SourceAnalyzer",
                "PromptCollection",
                "PromptCreator",
            ],
            "open_instances": [
                {
                    "type": "module",
                    "name": "PromptCollection",
                    "instance_id": "1",
                    "position": [0, 0, 0]
                },
                {
                    "type": "module",
                    "name": "PromptCreator",
                    "instance_id": "2",
                    "position": [0, 1, 0]
                }
            ]
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
        project_name = self.get_last_project()
        if project_name:
            self.load_project(project_name)
            return True
        else:
            print("Kein letztes Projekt gefunden.")
            return False

    def set_last_project(self):
        try:
            with open("config.json", "w") as config_file:
                data = {"last_project": self.project_name}
                json.dump(data, config_file, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern des letzten Projekts: {e}")
        return data
    
    def get_last_project(self):
        try:
            with open("config.json", "r") as config_file:
                data = json.load(config_file)
                return data.get("last_project", None)
        except FileNotFoundError:
            print("Konfigurationsdatei nicht gefunden.")
            return None

    def save_active_modules_and_instances(self):
        if self.project_data is None:
            print("Projektdaten sind nicht geladen.")
            return
        
        available_modules = [module.name for module in self.module_manager.modules]
        self.project_data["available_modules"] = available_modules

        open_instances = []
        for module in self.module_manager.modules:
            for module in self.module_manager.modules:
                instance_data = {
                    "module_name": module.name,
                    "instance_id": module.instance_id,
                    "position": module.position,
                }
        
        self.project_data["open_instances"] = open_instances

        with open(self.proj_file, "w", encoding="utf-8") as f:
            json.dump(self.project_data, f, indent=4)

    def load_active_modules_and_instances(self):
        available_modules = self.project_data.get("available_modules", [])
        for module_name in available_modules:
            self.add_module_by_name(module_name)

        open_instances = self.project_data.get("open_instances", [])
        for instance in open_instances:
            self.add_instance_at_position(instance)

    def add_module_by_name(self, module_name):
        module = self.create_module_by_name(module_name)
        if module:
            self.module_manager.add_module(module)


    def get_project(self):
        return self

    @property
    def source_dir(self):
        return self.project_data.get("paths", {}).get("source_folder", "")
        
    @property
    def database(self):
        return self.project_data.get("database", {})
    
    @property
    def name(self):
        return self.project_data.get("project_name", "")
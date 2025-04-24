from modules.source_analyzer import SourceAnalyzer
from modules.prompt_collection import PromptCollection
from modules.prompt_creator import PromptCreator

class ModuleManager:
    def __init__(self, controller):
        print("ModuleManager initialized")
        self.controller = controller
        self.modules = {}
        self.available_modules = {
            "SourceAnalyzer": SourceAnalyzer,
            "PromptCollection": PromptCollection,
            "PromptCreator": PromptCreator,
        }
        self.instances = {}

    def add_instance(self, name, instance_id, position=None):
        if(name, instance_id) not in self.modules:
            instance = self.create_instance(
                name, 
                module_manager=self,
                controller=self.controller,
                instance_id=instance_id,
                position=position
                )
            self.modules[(name, instance_id)] = instance
        return self.modules[(name, instance_id)]


    def create_instance(self, name, *args, **kwargs):
        print("Creating instance of module:", name)
        cls = self.available_modules.get(name)
        if cls is None:
            raise ValueError(f"Module '{name}' is not available.")
        
        instance = cls(*args, **kwargs)
        instance.instance_id = id(instance)
        instance.position = 0
        self.register_instance(name, instance)
        return instance

    def register_instance(self, name, instance):
        if name not in self.instances:
            self.instances[name] = {}
        self.instances[name][instance.instance_id] = instance
    
    def get_instance(self, name, instance_id):
        return self.instances.get(name, {}).get(instance_id, None)


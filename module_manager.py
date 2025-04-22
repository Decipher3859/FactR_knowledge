from modules.source_analyzer import SourceAnalyzer
from modules.prompt_collection import PromptCollection
from modules.prompt_creator import PromptCreator

class ModuleManager:
    def __init__(self, controller):
        self.controller = controller
        self.modules = []

        self.prompt_collection = None
        self.source_analyzer = None
        self.prompt_creator = None

    def initialize_modules(self):
        self.prompt_collection  = PromptCollection(self, self.controller)
        self.source_analyzer = SourceAnalyzer(self, self.controller)
        self.prompt_creator = PromptCreator(self, self.controller)

    def register_module(self, module):
        self.modules.append(module)
    
    def get_modules(self):
        return self.modules
    



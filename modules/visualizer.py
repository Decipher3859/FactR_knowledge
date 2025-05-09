from PyQt5.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from pyvis.network import Network
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

class Visualizer(QWidget):
    def __init__(self, module_manager, controller, instance_id=None, position=None):
        super().__init__()
        self.module_manager = module_manager
        self.controller = controller

        self.module_name = "Visualizer"
        self.icon_path = "visualizer.png"
        self.instance_id = instance_id

        self.project = controller.get_project()
        self.db = controller.db_manager

        self.setup_ui()

        self.render_graph()
        self.controller.prompt_added.connect(self.render_graph)

        self.setup_web_channel()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

    def render_graph(self):
        env = Environment(loader=FileSystemLoader("/home/damn/apprehendData/01_Projekte/FactR/gui/templates"))
        net = Network(height="100%", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)
        net.templateEnv = env
        net.path = "network_template.html"

        net.force_atlas_2based()

        columns = ['id', 'content', 'source', 'relation_name', 'local_id', 'parent_id']
        prompts = self.db.get_all_prompts()
        prompts_dict = [dict(zip(columns, row)) for row in prompts]

        id_to_label = {}
        
        for prompt in prompts_dict:
            print("Add Node")
            net.add_node(
                prompt['id'],
                label = prompt['content'],
                title = prompt['content'],
                shape = 'box',
                color = '#ccc'
            )
        
        relations = self.db.get_all_prompts_relations()
        for parent_id, child_id, relation in relations:
            print("Add Edge")
            net.add_edge(
                parent_id,
                child_id,
                label=relation,
                color="#888"
            )
            
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")

        for node in net.nodes:
            print(node)
        for edge in net.edges:
            print(edge)

        net.write_html(temp_file.name, notebook=False)
        temp_file.seek(0)
        
        self.web_view.load(QUrl.fromLocalFile(temp_file.name))
    
    def setup_web_channel(self):
        self.channel = QWebChannel()
        self.bridge = JSBridge(self.controller)
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

    @property
    def name(self):
        return self.__class__.__name__
    
    def to_dict(self):
        return {
            "name": self.name,
            "instance_id": self.instance_id,
            "position": self.position,
            "icon_path": self.icon_path
        }


class JSBridge(QObject):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    @pyqtSlot(str, str, str, str)
    def set_reference(self, id_, local_id, content, source):
        reference_data = {
            "id": id_,
            "local_id": local_id,
            "content": content,
            "source": source
        }
        self.controller.set_current_reference(reference_data)


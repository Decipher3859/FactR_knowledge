from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

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
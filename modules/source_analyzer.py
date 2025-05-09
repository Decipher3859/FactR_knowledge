import shutil
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QMenu, QAction, QListWidget, QListWidgetItem, QSplitter, QMessageBox, QFileDialog,
    QPushButton
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QIcon
from modules.markup_parser import *
from modules.tag_manager import *
from patterns import MARKUP_PATTERN, MARKUP_TEMPLATE

class SourceAnalyzer(QWidget):
    def __init__ (self, module_manager, controller, instance_id=None, position=None):
        super().__init__()
        self.module_manager = module_manager
        self.controller = controller

        self.module_name = "Quellanalyse"
        self.icon_path = "source_analyzer.png"
        self.instance_id = instance_id

        self.project = self.controller.get_project()
        self.db_manager = controller.get_db_manager()

        self.setup_ui()

        self.text_area = CustomTextEdit(self)
        self.current_source_id = 1
        self.tag_manager = TagManager(self.text_area.toPlainText(), self.project)
        self.highlighter = DiscourseHighlighter(self.text_area.document())


        
    def setup_ui(self):
        splitter = QSplitter(Qt.Horizontal, self)
        self.source_sidebar = SourceSidebar(self)

        splitter.addWidget(self.source_sidebar)
        splitter.addWidget(self.text_area)

        splitter.setSizes([200, 600])

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

        return self

    def load_text(self, raw_text):
        parser = MarkupParser(raw_text)
        cleaned_text = parser.get_cleaned_text()
        self.text_area.setPlainText(cleaned_text) 

        self.update_markers()

    def update_markers(self, text=None):
        if text is None:
            text = self.text_area.toPlainText()

        self.tag_manager = TagManager(text, self.project)
        self.highlighter.set_markers(
            self.tag_manager.get_all_tag_positions()
        )
        self.highlighter.rehighlight()

class CustomTextEdit(QTextEdit):
    def __init__(self, source_analyzer):
        super().__init__()
        self.source_analyzer = source_analyzer
        self.db_manager = source_analyzer.db_manager


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        
        if event.button() == Qt.LeftButton:
            cursor = self.textCursor()
            selected_text = cursor.selectedText()
            if selected_text.strip():
                self.show_inline_menu(event)

    def show_inline_menu(self, event):
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        source = self.source_analyzer.current_source_id

        menu = QMenu(self)

        if self.source_analyzer.tag_manager.is_tagged(selected_text):
            remove_action = QAction("Delete Tag", self)
            remove_action.triggered.connect(self.remove_tag)
            menu.addAction(remove_action)
        else:
            thesis_action = QAction("These", self)
            thesis_action.triggered.connect(lambda: self.add_tag(source, 'the', selected_text))
            menu.addAction(thesis_action)

            separator_action = QAction("------", self)
            separator_action.setEnabled(False)
            menu.addAction(separator_action)
            
            marker_action = QAction("Beleg", self)
            marker_action.triggered.connect(lambda: self.add_tag(source, 'cit', selected_text))
            menu.addAction(marker_action)
        
            arg_action = QAction("Gegenbeleg", self)
            arg_action.triggered.connect(lambda: self.add_tag(source, 'con', selected_text))
            menu.addAction(arg_action)

            question_action = QAction("Frage", self)
            question_action.triggered.connect(lambda: self.add_tag(source, 'que', selected_text))
            menu.addAction(question_action)


        menu.exec_(self.mapToGlobal(event.pos()))

    def add_tag(self, source: str, tag: str, content: str):
        source_id = self.source_analyzer.current_source_id
        local_id = str(self.source_analyzer.tag_manager.get_max_id_from_file(tag, source_id) + 1)

        wrapped = MARKUP_TEMPLATE.format(tag=tag, source=source, id=local_id, text=content)

        cursor = self.textCursor()
        cursor.insertText(wrapped)

        self.source_analyzer.project.save_tag_to_file(tag, source, local_id, content)
        self.source_analyzer.project.save_source_file(content, tag)

        if self.db_manager:
            self.db_manager.create_prompt(content, tag, source_id, local_id)

        self.source_analyzer.update_markers()


    def remove_tag(self):
        cursor = self.textCursor()
        selection_start = cursor.selectionStart()
        selection_end = cursor.selectionEnd()

        text = self.toPlainText()

        for match in re.finditer(MARKUP_PATTERN, text):
            start, end = match.span()
            if selection_start >= start and selection_end <= end:
                tag_data = match.groupdict()

                new_text = text[:start] + tag_data["text"] + text[end:]
                self.setPlainText(new_text)
                tag = tag_data["tag"]
                source = int(tag_data["source"])
                id_ = int (tag_data["id"])
                self.source_analyzer.project.delete_tag_entry(tag, source, id_)

                self.source_analyzer.project.save_source_file(new_text, tag)

                self.source_analyzer.update_markers()
                return

        self.source_analyzer.update_markers()

class SourceSidebar(QWidget):
    def __init__(self, source_analyzer):
        super().__init__(source_analyzer)
        self.source_analyzer = source_analyzer
        self.project = self.source_analyzer.project
        self.db_manager = self.source_analyzer.db_manager

        self.layout = QVBoxLayout(self)
        self.source_list = QListWidget(self)
        self.layout.addWidget(self.source_list)

        self.add_source_button = QPushButton("Neue Quelle")
        self.add_source_button.clicked.connect(self.add_new_source)
        self.layout.addWidget(self.add_source_button)

        self.setLayout(self.layout)

        self.load_sources_from_db()
        self.source_list.itemClicked.connect(self.load_source_from_file)

    def load_sources_from_db(self):
        self.source_list.clear()
        sources = self.db_manager.get_all_sources()

        for source in sources:
            item = QListWidgetItem(source[1])
            self.source_list.addItem(item)
        self.source_list.setCurrentRow(0)

    def load_source_from_file(self, item):
        source_name = item.text()
        file_name = f"{source_name}.md"
        source_path = os.path.join(self.project.source_dir, file_name)

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                text = f.read()
                self.source_analyzer.text_area.setPlainText(text)

            from patterns import extract_source_id
            source_id = extract_source_id(file_name)
            self.source_analyzer.current_source_id = int(source_id)

            self.source_analyzer.update_markers()

        except Exception as e:
            print(f"Fehler beim Laden der Quelle {source_name}: {e}")

    def add_new_source(self):
        if not self.project or not self.project.project_dir:
            QMessageBox.warning(self, "Kein Projekt geladen", "Bitte lade zuerst ein Projekt.")
            return
        
        options = QFileDialog.Options()
        file_path,  _ = QFileDialog.getOpenFileName(
            self, "Neue Quelle auswählen", "", "Txtdateien(*.txt *.md);;Alle Dateien (*)", options=options)
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(self.project.source_dir, file_name)
                shutil.copy(file_path, target_path)

                self.db_manager.add_source(
                    file_name = file_name,
                    title = file_name
                )


                QMessageBox.information(self, "Quelle hinzufügen", f"Datei erfolgreich kopiert nach: \n{target_path}")

                self.source_analyzer.source_sidebar.load_sources_from_db()

            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Kopieren: {str(e)}")
    

class DiscourseHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.tag_colors = {
            'cit': '#40d0e0',   # türkis
            'con': '#c4f0c5',   # hellgrün
            'the': '#cfe2ff',   # hellblau
            'que': '#ffeeba'    # hellgelb
        }
        self.markers = []

    def set_markers(self, markers):
        self.markers = markers

    def highlightBlock(self, text):
        block_position = self.currentBlock().position()
        block_length = len(text)

        if not self.markers:
            print("Keine Markierungen vorhanden!")
            return

        for marker in self.markers:
            start = marker['start']
            end = marker['end']
            tag = marker['tag']

            if start < block_position + block_length and end > block_position:
                highlight_start = max(0, start - block_position)
                highlight_length = min(end, block_position + block_length) - max(start, block_position)

                if tag in self.tag_colors:
                    fmt = QTextCharFormat()
                    fmt.setBackground(QColor(self.tag_colors[tag]))
                    self.setFormat(highlight_start, highlight_length, fmt)

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
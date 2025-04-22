import os
import re
from modules.markup_parser import *
from patterns import MARKUP_PATTERN


class TagManager:
    def __init__(self, text, project=None):
        self.text = text
        self.project = project
        parser = MarkupParser(text)
        self.tags = parser.extract_tags(text)

    def get_tags(self):
        return self.tags

    def is_tagged(self, selected_text: str) -> bool:
        return bool(re.fullmatch(MARKUP_PATTERN, selected_text.strip()))

    def find_full_tag_span(self, selection_start, selection_end):
        for match in re.finditer(MARKUP_PATTERN, self.text):
            start, end = match.span()
            if selection_start >= start and selection_end <= end:
                return start, end, match.group('text')
        return None, None, None

    def get_all_tag_positions(self):
        tag_positions = []
        
        for tag, tag_list in self.tags.items():
            for tag_data in tag_list:
                tag_positions.append({
                    'tag':tag_data['tag'],
                    'source': tag_data['source'],
                    'id':tag_data['id'],
                    'start':tag_data['start'],
                    'end':tag_data['end'],
                    'text':tag_data['text']
                })
        return tag_positions
    
    # def get_next_tag_id( self, tag):
    #     return len(self.tags.get(tag, [])) + 1
    
    # def get_max_id_from_file(self, tag):
    #     file_name = tag_to_file.get(tag)

    #     if file_name is None:
    #         print(f"Kein Dateipfad für Tag '{tag}' gefunden!")

    #     file_path = os.path.join(self.project.project_dir, file_name)
    #     pattern = re.compile(r"§\{" + tag + r":\d+:([0-9]+)\}\[.*\]§")
    #     max_id = 0

    #     with open(file_path, "r") as file:
    #         content = file.read()
    #         matches = pattern.findall(content)
    #         if matches:
    #             max_id = max(int(match) for match in matches)

    #     return max_id

    def get_max_id_from_file(self, tag, source_id=None):
        file_path = os.path.join(self.project.ensure_project_folder(), tag_to_file[tag])
        pattern = MARKUP_PATTERN
        max_id = 0

        try: 
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    match = re.match(pattern, line)
                    if match:
                        source, id_ = int(match.group(2)), int(match.group(3))
                        if source_id is None or source == source_id:
                            max_id = max(max_id, id_)

        except FileNotFoundError:
            pass

        return max_id

    def register_tag(self, tag, text):
        self.tags.setdefault(tag, []).append(text)

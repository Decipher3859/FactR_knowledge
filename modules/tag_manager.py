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
    
    def register_tag(self, tag, text):
        self.tags.setdefault(tag, []).append(text)

from patterns import *

class MarkupParser:
    def __init__(self, raw_text):
        self.raw_text= raw_text
        self.cleaned_text = ""
        self.markers = []
        self._parse()

    def _parse(self):
        pattern = MARKUP_PATTERN
        result = []
        cleaned = ""
        cursor = 0

        for match in re.finditer(pattern, self.raw_text):
            start, end = match.span()
            tag, source, marker_id, marked_text = match.groups()
            prefix = self.raw_text[cursor:start]
            cleaned += prefix
            cleaned_start = len(cleaned)

            cleaned += marked_text
            cleaned_end = len(cleaned)

            result.append({
                "tag": tag,
                "source": int(source),
                "id": int(marker_id),
                "start": cleaned_start,
                "end": cleaned_end,
                "text": marked_text
            })

            cursor = end

        cleaned+= self.raw_text[cursor:]

        self.cleaned_text = cleaned
        self.markers = result

    def get_cleaned_text(self):
        return self.cleaned_text
    
    def get_markers(self):
        return self.markers

    def extract_tags(self, text):
        grouped = {}

        for match in find_all_markup(text):
            tag_data = match.groupdict()
            tag_data['start'] = match.start()
            tag_data['end'] = match.end()
            tag = tag_data["tag"]

            grouped.setdefault(tag, []).append(tag_data)

        return grouped


    def create_markup(tag, source, id, text):
        return MARKUP_TEMPLATE.format(tag=tag, source=source, id=id, text=text)

import re

MARKUP_TEMPLATE = "§{{{tag}:{source}:{id}}}[{text}]§"
MARKUP_PATTERN = re.compile(
    r"§\{(?P<tag>\w+):(?P<source>\d+):(?P<id>\d+)\}\[(?P<text>.+?)\]§", 
    re.DOTALL
    )

tag_to_file = {
    'prmt': 'source/s00_prompts.md',
    'cit': 'citations.md', 
    'con': 'contradictions.md',
    'the': 'theses.md',
    'que': 'questions.md'
        }

tag_labels = {
    'prmt': 'Prompt',
    'cit': 'Citation',
    'con': 'Contradiction',
    'the': 'These',
    'que': 'Frage'
}

def find_all_markup(text):
    
    return list(MARKUP_PATTERN.finditer(text))

def extract_source_id(file_name: str) -> str:
    match = re.match(r"s(\d+)_", file_name)
    return match.group(1) if match else "0"
def default_new_project_structure():
    """
    Stanadrdlayout beim Erstellen eines neuen Projekts.
    Oben: PromptCollection
    Unten: PromptCreator
    """
    return {
        "type": "split",
        "orientation": 2,
        "children": [
            {
                "type": "module",
                "name": "PromptCollection",
                "instance_id": "default",
                "position": 0,
            },
            {
                "type": "module",
                "name": "PromptCreator",
                "instance_id": "default",
                "position": 1
            }
        ]
    }

def empty_split_container():
    """
    Leeres Layout für den Fall, dass kein Layout vorhanden ist.
    """
    return {
        "type": "split",
        "orientation": 2,
        "children": []
    }
import json

def load_json(filename):
    """Lädt JSON-Dateien aus dem data-Ordner"""
    with open(f"data/{filename}", "r", encoding="utf-8") as f:
        return json.load(f)

def load_story():
    return load_json("story.json")

def load_gegner():
    return load_json("gegner.json")

def load_items():
    return load_json("items.json")

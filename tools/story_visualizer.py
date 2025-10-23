import json
from graphviz import Digraph
from pathlib import Path

path = Path("../data/story.json")

def load_story(story_path: str | Path) -> dict:
  with open(story_path, "r",encoding="utf-8") as file:
    return json.load(file)

def build_story_graph(story_data: dict, output_file: str = "story_graph"):
  dot = Digraph(comment = "Story Graph", format = "png") # Als Format auch "svg" oder "pdf möglich"

  # Alle vorhandenen Szenen als neutrale Knoten
  for scene_id in story_data.keys():
    dot.node(scene_id, scene_id, shape="box", style="filled", color="lightgrey")

  # Kanten bauen + Validierung sammeln
  warnings = []
  drawn_edges = set()   # Set, um doppelte kanten zu verhindern.

  for scene_id, scene in story_data.items():
    for choice in scene.get("choices", []):
      target = choice.get("next_scene", [])
      if not target:
        warnings.append(f"{scene_id}: Choice ohne 'next_scene' --> {choice}")
        continue

      # Fehlende Zielscene? Markiere sie im Graph und merke Warnung
      if target not in story_data:
        dot.node(target, f"{target}\n[FEHLT]", shape="ellipse", style="filled", color="red")
        warnings.append(f"Verweis auf fehlende Szene: {scene_id} --> {target}")
        

      # Kante nur zeichnen, wenn noch nicht gezeichnet
      if (scene_id, target) not in drawn_edges:
          dot.edge(scene_id, target)
          drawn_edges.add((scene_id, target))
  
  # Warnungen ausgeben
  if warnings:
    print("WARNUNGEN:")
    for w in warnings:
      print(" - ", w)

  
  # PNG rendern
  output_path = Path(output_file).with_suffix("")
  dot.render(output_path, cleanup = True)
  print(f"Story-Graph gespeichert als: {output_path}.png")

if __name__ == "__main__":
  
  try:
    story = load_story(path)
  except FileNotFoundError:
    print(f"Datei {path} nicht gefunden!")
    exit()
  except json.JSONDecodeError as e:
    print(f"Fehler beim Lader der JSON: {e}")
    exit()

  # Den Graphen rendern
  build_story_graph(story, "rendered/story_graph")
  
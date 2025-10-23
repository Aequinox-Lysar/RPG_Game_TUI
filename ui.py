from textual.widgets import Static, Input
from textual.containers import Horizontal, Vertical, Container
from rich.text import Text
from rich.emoji import Emoji
from rich.table import Table
from rich.progress import BarColumn, Progress
from utils import sanitize_emoji

def create_widgets():
    """
    Erzeugt alle Widgets und das Layout für die App.
    """
    
    # Title Art einlesen
    with open("assets/title.txt", "r", encoding="utf-8") as f:
        ascii_title = f.read()
    
    # Titel
    title_widget = Static(ascii_title, id="title")


    # Widgets erstellen
    stats_widget = Static("", id="stats")
    story_widget = Static("", id="story")
    inv_widget = Static("", id="inv")
    actions_widget = Static("", id="actions_text")
    input_widget = Input(placeholder="Option wählen...")
    
    # Infobox mit festem Titel
    info_widget = Static(id="info_widget")
    info_widget.update("[bold orange]Infobox[/bold orange]\n")  # Titel immer oben

    # Layout
    # Obere Zeile: Stats | Story | Inventar
    horizontal = Horizontal(
        stats_widget,
        story_widget,
        inv_widget,
        id="top_row",
    )

    stats_widget.width = 40
    story_widget.expand = True
    inv_widget.width = 40

    # Untere Zeile: Aktionen + Input
    vertical = Vertical(
        actions_widget,
        input_widget,
        info_widget,
        id="actions_container",
    )

    # Hauptcontainer erstellen um Darstellung zu begrenzen.
    main_container = Container(title_widget, horizontal, vertical, id="main_container")  

    return main_container, stats_widget, story_widget, inv_widget, actions_widget, input_widget, title_widget, info_widget


# Renderfunktionen

def render_stats(spieler):

    # Icons mit Rich-Emoji (breitenkorrekt)
    hp_icon = Emoji("heart")
    xp_icon = Emoji("star")
    atk_icon = Emoji("crossed_swords")
    def_icon = Emoji("shield")
    stats_icon = Emoji("zap")
    level_icon = Emoji("bookmark_tabs")

    # HP-Balken
    hp_ratio = spieler.hp / spieler.max_hp
    hp_bar_length = 20  # Anzahl der Blöcke
    filled_hp = int(hp_ratio * hp_bar_length)
    empty_hp = hp_bar_length - filled_hp
    hp_bar = f"[red]{'█'*filled_hp}[/red][grey]{'█'*empty_hp}[/grey]"

    # XP-Balken
    xp_ratio = spieler.xp / (spieler.level * 100)  # Beispiel: 100 XP pro Level
    xp_bar_length = 20
    filled_xp = int(xp_ratio * xp_bar_length)
    empty_xp = xp_bar_length - filled_xp
    xp_bar = f"[green]{'█'*filled_xp}[/green][grey]{'█'*empty_xp}[/grey]"


    return (
        f"{stats_icon} [bold yellow]Stats[/bold yellow]:\n\n"
        f"\U0001f464 Name: [bold green]{spieler.name}[/bold green]\n\n"
        f"{level_icon} Level: [cyan]{spieler.level}[/cyan]\n\n"
        f"{xp_icon}  XP: [magenta]{spieler.xp}/{spieler.level*100} {xp_bar}[/magenta]\n\n"
        f"{hp_icon}  HP: [red]{spieler.hp}/{spieler.max_hp} {hp_bar}[/red]\n\n"
        f"{atk_icon}  Angriff: {spieler.attack}\n\n"
        f"{def_icon}  Verteidigung: {spieler.defense}"
    )

def render_inventar(spieler):
    # Inventar-Titel mit Emoji
    header = "🎒 Inventar:\n\n"
    
    if spieler.inventar:
        # Items nach Anzahl gruppieren
        items_count = {}
        for item in spieler.inventar:
            key = item["id"]
            if key in items_count:
                items_count[key]["anzahl"] += 1
            else:
                items_count[key] = {
                    "name": item["name"],
                    "icon": sanitize_emoji(item.get("icon", "")),
                    "anzahl": 1
                }

        # Items formatiert auflisten
        lines = []
        for item in items_count.values():
            lines.append(f"{item['anzahl']}x {item['icon']} {item['name']}")

        return header + "\n".join(lines)
    
    return header + "[leer]"

def render_story(scene):
    text = scene["text"]
    choices = scene.get("choices", [])

    actions_text = ""
    if choices:
        for i, c in enumerate(choices):
            # Signalwort farbig hervorheben
            highlighted = c["text"].replace(
                 c["signal"], f"[bold bright_cyan]{c['signal']}[/bold bright_cyan]"
            )
            actions_text += f"{i+1}) {highlighted}\n"
    else:
        actions_text = "[italic grey]Keine Optionen verfügbar[/]"
    
    # Story mittig rendern
    return text, actions_text

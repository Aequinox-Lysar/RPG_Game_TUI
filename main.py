import asyncio
import re
from textual.app import App, ComposeResult
from textual.widgets import Input, Static
from rich.align import Align
from rich.markup import escape
from rich.text import Text



from ui import create_widgets, render_stats, render_inventar, render_story
from spieler import Spieler
from data_loader import load_story, load_gegner, load_items
from fortschritt import erhöhe_xp
from inventar import neues_item, benutze_item
from utils import sanitize_emoji
from shop import ShopModal


class RPGApp(App):

    CSS = """
    
    #main_container {
        border: round white;
        padding: 2 3;
        width: 180;
        height: 48;
        margin-top: 1;
        margin-bottom: 10;
    }

    #title {
        dock: top;
        color: gold;
        text-align: center;
        margin-bottom: 2;
        margin-top: 2;
    }

    Screen {
        align: center middle;
        background: rgb(15,15,25);
    }

    #story {
        border: heavy green;
        background: rgb(30,30,50);
        min-width: 40%;
        max-width: 60%;
        min-height: 20;
        margin-left: 3;
        margin-right: 3;
        padding: 2 3;
        overflow: auto;
    }

    #stats {
        border: round blue;
        background: rgb(20,20,40);
        min-width: 18%;
        max-width: 18%;
        padding: 1 2;
        margin-right: 2;
    }

    #inv {
        border: round magenta;
        background: rgb(40,20,50);
        width: 20%;
        padding: 1 2;
        margin-left: 2;
    }

    #actions_container {
        border: round yellow;
        background: rgb(40,40,25);
        padding: 1 2;
        margin-top: 2;
        height: auto;
    }

    #info_widget {
        border: round orange;
        background: rgb(50,40,20);
        padding: 0 3;
        max-height: 10;
        min-height: 5;
        overflow: auto;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.info_task: asyncio.Task | None = None  # Aktiver Typewriter-Task für Infobox

        # Daten laden
        self.story_data = load_story()
        self.gegner_data = load_gegner()
        self.items_data = load_items()
        
        # Spieler erstellen und Startitem geben
        self.spieler = Spieler("Daniel")
        neues_item(self.spieler, self.items_data[0])
        
        # Aktuelle Szene
        self.current_scene = "start"

    def update_stats(self):
        self.stats_widget.update(render_stats(self.spieler))

    def update_inventar(self):
        self.inv_widget.update(render_inventar(self.spieler))

    # Typewriter- Effekt für die Story
    async def typewriter(self, widget, text, delay=0.05):
        """
        Animiert den Text wie beim Tippen, inkl. Rich-Markup für Farben.
        """
        widget.update("")  # Widget leeren
        buffer = Text("")

        # Regex um Rich-Tags zu erkennen
        tag_pattern = re.compile(r"(\[/?[^\]]+\])")
        tokens = tag_pattern.split(text)

        # Aktive Tags merken
        open_tags = []

        for token in tokens:
            if tag_pattern.fullmatch(token):
                # Tag öffnen oder schließen
                if token.startswith("[/"):
                    if open_tags:
                        open_tags.pop()
                else:
                    open_tags.append(token)
            else:
                 # Text ohne Tags Zeichen für Zeichen anzeigen
                for char in token:
                    # Rich-Markup zusammenbauen
                    markup_text = "".join(open_tags) + char + "".join(f"[/{t[1:]}" for t in reversed(open_tags))
                    buffer = Text.from_markup(str(buffer) + markup_text)
                    widget.update(buffer)
                    await asyncio.sleep(delay)

    # Typewriter für die Infobox
    async def show_info_with_typewriter(self, text: str, delay: float = 0.08, display_time: float = 5.0):
        """Zeigt die Item-Beschreibung in der Infobox mit Typewriter-Effekt und blendet sie nach display_time Sekunden sanft aus."""
        text= sanitize_emoji(text)
        
        # Vorherigen Task abbrechen
        if self.info_task and not self.info_task.done():
            self.info_task.cancel()
            try:
                await self.info_task
            except asyncio.CancelledError:
                pass

        async def _typewriter_fade():
            # Titel fix
            self.info_widget.update(Text("Infobox\n" + "\n", style="bold orange"))
            buffer = Text()

            # Typewriter nur für Beschreibung
            for char in text:
                buffer.append(char)
                # Titel + Beschreibung zusammen aktualisieren
                self.info_widget.update(Text("Infobox\n", style="bold orange") + "\n" + buffer)
                await asyncio.sleep(delay)

            # Kurze Anzeige
            await asyncio.sleep(display_time)

            # Fade-Out: Text in dunkler werdendem Grau
            fade_steps = 10
            for i in range(fade_steps):
                grey_value = 255 - int((i+1) * (200 / fade_steps))
                fade_text = Text("Infobox\n", style="bold orange")
                fade_text.append(buffer.plain, style=f"rgb({grey_value},{grey_value},{grey_value})")
                self.info_widget.update(fade_text)
                await asyncio.sleep(0.05)

            # Nach Fade nur Titel anzeigen
            self.info_widget.update(Text("Infobox\n", style="bold orange"))

        self.info_task = asyncio.create_task(_typewriter_fade())
        await self.info_task




    async def update_story(self):
        scene = self.story_data[self.current_scene]
        story_text, actions_text = render_story(scene)

        # Storytext animiert anzeigen
        await self.typewriter(self.story_widget, story_text)

        # Optionen normal ins Widget.
        if actions_text.strip():
            self.actions_widget.update(
                "Aktionen:\n" + actions_text + "\n\n(Tipp: 'exit' zum Beenden)"
            )
        else:
            self.actions_widget.update("Keine Aktionen verfügbar.\n\n(Tipp: 'exit' zum Beenden)")

    def compose(self) -> ComposeResult:
        main_container, self.stats_widget, self.story_widget, self.inv_widget, \
        self.actions_widget, self.input_widget, self.title_widget, info_widget = create_widgets()

        # Wichtig: als Attribut speichern.
        self.info_widget = info_widget
        
        # Titel separat oben Anzeigen
        yield self.title_widget

        # Danach den Spielfeld-Container mit Rahmen
        yield main_container

    async def on_mount(self) -> None:
        # Erste Aktualisierung
        self.update_stats()
        self.update_inventar()
        self.call_later(lambda: asyncio.create_task(self.update_story()))
        # Fokus auf Input
        self.set_focus(self.input_widget)

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        choice = message.value.strip().lower()

        # --- Shop geöffnet? ---
        if self.screen_stack and isinstance(self.screen_stack[-1], ShopModal):
            # Alles wird vom Shop abgefangen
            return
        
        # --- Beenden ---
        if choice == "exit":
            await self.action_quit()
            return
        
        # --- Shop öffnen ---
        if choice == "shop":
            await self.push_screen(ShopModal(self.items_data, self.spieler))
            self.input_widget.value = ""            
            return

        # --- Info-Befehl ---
        if choice.startswith("info "):
            item_name = choice[5:].strip().lower()
            # Ab jetzt Items direkt aus self.items_data suchen
            item = next((i for i in self.items_data if i["name"].lower() == item_name), None)
            if item:
                info_text = f"{item.get('icon','')} {item['name']}: {item.get('beschreibung','')}"
            else:
                info_text = "Item nicht gefunden."
            asyncio.create_task(self.show_info_with_typewriter(info_text))
            self.input_widget.value = ""
            self.set_focus(self.input_widget)
            return
                        

        # --- Story-Optionen prüfen ---
        scene = self.story_data[self.current_scene]
        scene_choices = scene.get("choices", [])

        # Inventar-Optionen dynamisch hinzufügen
        item_choices = [i["name"].lower() for i in self.spieler.inventar]

        # Prüfen: Story-Option auswählen
        selected_choice = next((c for c in scene_choices if choice == c["signal"].lower()), None)

        if selected_choice:
            next_scene_id = selected_choice.get("next_scene")
            if next_scene_id:
                self.current_scene = next_scene_id
                erhöhe_xp(self.spieler, 5)
            else:
                self.story_widget.update("Ende der Geschichte")
                await self.action_quit()
                return

        # Prüfen: Item benutzen
        elif choice in item_choices:
            # Item aus Inventar finden
            inv_item = next(i for i in self.spieler.inventar if i["name"].lower() == choice)
            msg = benutze_item(self.spieler, inv_item["id"], self.items_data)
            self.story_widget.update(f"{self.story_widget.renderable}\n\n{msg}")

        else:
            # Ungültige Eingabe
            self.story_widget.update("Ungültige Eingabe! Signalwort oder Item verwenden.")
            self.input_widget.value = ""
            self.set_focus(self.input_widget)
            return

        # --- UI aktualisieren ---
        self.update_stats()
        self.update_inventar()
        await self.update_story()

        # Input zurücksetzen und Fokus
        self.input_widget.value = ""
        self.set_focus(self.input_widget)

if __name__ == "__main__":
    app = RPGApp()
    app.run()

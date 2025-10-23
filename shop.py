from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static, Input
from utils import sanitize_emoji
from textual import events

class ShopModal(ModalScreen):

    CSS = """
    ShopModal {
        align: center middle;
        background: rgba(0,0,0,0.6);   /* Overlay */
    }

    #shop_container {
        border: heavy yellow;
        background: rgb(40,30,10);
        padding: 2 3;
        width: 60%;
        min-height: 20;
        align: center top;
    }

    #shop_list {
        margin-top: 1;
        margin-bottom: 1;
        color: navajowhite;
    }

    #shop_input {
        border: round green;
        background: black;
        color: white;
        height: 3;
    }
    """

    def __init__(self, items_data, spieler, **kwargs):
        super().__init__(**kwargs)
        self.items_data = items_data
        self.spieler = spieler
        self.items_list = None
        self.input_widget = None

    def _render_items(self) -> str:
        """Liste aller kaufbaren Items als Text."""
        lines = [f"[bold yellow]🛒 Shop[/bold yellow]  |  Gold: [yellow]{self.spieler.geld}[/yellow]\n"]
        for item in self.items_data:
            preis = item.get("preis", 10)
            icon = sanitize_emoji(item.get("icon", ""))
            lines.append(f"{icon} {item['name']} - {preis} Gold")
        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        with Container(id="shop_container"):
            self.items_list = Static(self._render_items(), id="shop_list")
            yield self.items_list

            self.input_widget = Input(placeholder="Eingabe: kaufe <item> oder exit", id="shop_input")
            yield self.input_widget

    async def on_mount(self) -> None:
        self.set_focus(self.input_widget)

    async def on_input_submitted(self, message: Input.Submitted) -> None:

        choice = message.value.strip().lower()

        # Stoppe Event-Bubbling, damit App es nicht sieht
        message.stop()

        if choice == "exit":
            # Inventar und Stats direkt aktualisieren, bevor modal schließt.
            self.app.update_inventar()
            self.app.inv_widget.refresh()
            self.app.update_stats()
            self.app.stats_widget.refresh()

            self.dismiss() # Modal Schließen
            return

        if choice.startswith("kaufe "):
            item_name = choice[6:].strip().lower()
            item = next((i for i in self.items_data if i["name"].lower() == item_name), None)
            if not item:
                self.items_list.update("[red]Item nicht gefunden.[/red]\n\n" + self._render_items())
                self.input_widget.value = ""
                self.set_focus(self.input_widget)
                return

            preis = item.get("preis", 10)
            if self.spieler.geld >= preis:
                self.spieler.geld -= preis
                self.spieler.inventar.append(item)

                # Direkt Inventar & Stats rendern
                self.app.update_inventar()
                self.app.inv_widget.refresh()
                self.app.update_stats()
                self.app.stats_widget.refresh()

                self.items_list.update(f"[green]Gekauft:[/green] {item['name']} für {preis} Gold!\n\n" + self._render_items())
            else:
                self.items_list.update("[red]Nicht genug Gold![/red]\n\n" + self._render_items())

            # Eingabe zurücksetzen und Fokus behalten
            self.input_widget.value = ""
            self.set_focus(self.input_widget)

    async def on_dismiss(self) -> None:
        # Fokus wieder auf Haupt-Input setzen
        self.app.set_focus(self.app.input_widget)

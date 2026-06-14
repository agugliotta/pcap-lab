from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Input, ContentSwitcher, ListView, ListItem
from textual.containers import Container, Vertical, Horizontal
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator

class ClickableLabel(Label):
    def __init__(self, text, id=None, callback=None):
        super().__init__(text, id=id)
        self.callback = callback

    def on_click(self):
        if self.callback:
            self.callback()

class PCAPApp(App):
    CSS = """
    #sidebar { width: 30; background: $surface; border-right: vkey $accent; }
    #main { width: 100%; height: 100%; padding: 2; }
    .title { padding: 1; text-align: center; text-style: bold; }
    .clickable { cursor: pointer; color: $text; }
    .clickable:hover { color: $accent; text-style: underline; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self):
        super().__init__()
        self.available_attacks = ["sqli", "xss", "idor", "csrf", "rce", "lfi", "cmdi"]
        self.enabled_attacks = self.available_attacks.copy()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Menu", classes="title")
                yield ListView(
                    ListItem(Label("  Dashboard"), id="dashboard"),
                    ListItem(Label("  Attacks"), id="attacks"),
                    ListItem(Label("  Settings"), id="settings"),
                    id="menu"
                )
            with ContentSwitcher(initial="dashboard", id="main"):
                with Container(id="dashboard"):
                    yield Label("PCAP Lab Control Center")
                    yield ClickableLabel("  [ Run Generation ]", id="run_btn", callback=self.run_generation)
                with Container(id="attacks"):
                    yield Label("Toggle Attacks:")
                    for attack in self.available_attacks:
                        status = "[x]" if attack in self.enabled_attacks else "[ ]"
                        yield ClickableLabel(f"  {status} {attack}", id=f"attack_{attack}", callback=lambda a=attack: self.toggle_attack(a))
                with Container(id="settings"):
                    yield Label("Settings")
                    yield Input(placeholder="Enter Student File Path...", id="student_file")
        yield Footer()

    def toggle_attack(self, attack):
        if attack in self.enabled_attacks:
            self.enabled_attacks.remove(attack)
        else:
            self.enabled_attacks.append(attack)
        # Refresh the attacks view
        self.refresh()

    def on_list_view_selected(self, event: ListView.Selected):
        self.query_one(ContentSwitcher).current = event.item.id

    def run_generation(self):
        student_file = self.query_one("#student_file", Input).value
        # (Generation logic similar to before)
        self.query_one("#dashboard").add_child(Label(f"Generation started with {student_file}"))

if __name__ == "__main__":
    PCAPApp().run()

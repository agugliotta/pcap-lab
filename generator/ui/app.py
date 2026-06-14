from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label, Switch, Input, Button, ContentSwitcher
from textual.containers import Container, Vertical, Horizontal
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator
import os

class PCAPApp(App):
    CSS = """
    #sidebar { width: 30; background: $surface; border-right: vkey $accent; }
    #main { width: 100%; height: 100%; }
    .title { padding: 1; text-align: center; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Menu", classes="title")
                yield ListView(
                    ListItem(Label("Dashboard"), id="dashboard"),
                    ListItem(Label("Attacks"), id="attacks"),
                    ListItem(Label("Settings"), id="settings"),
                    id="menu"
                )
            with ContentSwitcher(initial="dashboard", id="main"):
                with Container(id="dashboard"):
                    yield Label("PCAP Lab Control Center")
                    yield Button("Run Generation", id="run_btn")
                with Container(id="attacks"):
                    yield Label("Toggle Attacks:")
                    # Simplified attack checklist
                    for attack in ["sqli", "xss", "idor"]:
                        yield Horizontal(Switch(id=f"switch_{attack}"), Label(attack))
                with Container(id="settings"):
                    yield Label("Settings")
                    yield Input(placeholder="Student File", id="student_file")
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected):
        self.query_one(ContentSwitcher).current = event.item.id

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "run_btn":
            self.run_generation()

    def run_generation(self):
        student_file = self.query_one("#student_file", Input).value
        # (Generation logic similar to before, but async for Textual)

if __name__ == "__main__":
    PCAPApp().run()

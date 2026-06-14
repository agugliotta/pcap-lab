from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Tree, ContentSwitcher, Input, Label
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator

class Sidebar(Tree):
    def __init__(self, **kwargs):
        super().__init__("PCAP Lab", **kwargs)
        self.root.expand()
        self.root.add_leaf("Dashboard", data="dashboard")
        self.root.add_leaf("Attacks", data="attacks")
        self.root.add_leaf("Settings", data="settings")

class MainPanel(ContentSwitcher):
    def compose(self) -> ComposeResult:
        with Container(id="dashboard"):
            art = [
                " ____   ____    _    ____  ",
                "|  _ \\ / ___|  / \\  |  _ \\ ",
                "| |_) | |     / _ \\ | |_) |",
                "|  __/| |___ / ___ \\|  __/ ",
                "|_|    \\____/_/   \\_\\_|    "
            ]
            for line in art:
                yield Label(line)
            yield Label("============================================")
            yield Label("Version: v0.3 | Author: Agustín Gugliotta")
            yield Label("GitHub: github.com/agugliotta")
            yield Label("============================================")
            yield Label("Status: Idle")
            yield Label("Press [ctrl+r] to run generation")
        with Container(id="attacks", classes="padded"):
            yield Label("--- Attacks (Toggle with [0-6]) ---")
            # Attack items will be mounted dynamically
        with Container(id="settings", classes="padded"):
            yield Label("--- Settings ---")
            yield Input(placeholder="Student File Path", id="student_file")

class PCAPApp(App):
    CSS = """
    Screen { background: $surface; }
    #sidebar { width: 25; border-right: solid $accent; background: $surface; }
    .padded { padding: 1; }
    .panel-title { text-style: bold; padding: 1; }
    """
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+r", "run", "Run Batch"),
    ]

    def __init__(self):
        super().__init__()
        self.available_attacks = ["sqli", "xss", "idor", "csrf", "rce", "lfi", "cmdi"]
        self.enabled_attacks = self.available_attacks.copy()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar(id="sidebar")
            yield MainPanel(initial="dashboard", id="main")
        yield Footer()

    def on_mount(self):
        self.notify(f"Init attacks: {self.enabled_attacks}")
        self.render_attacks()

    def render_attacks(self):
        attacks_container = self.query_one("#attacks", Container)
        # Remove old attack labels
        for child in attacks_container.query("Label")[1:]:
            child.remove()
        
        # Mount new labels with explicit status
        for i, attack in enumerate(self.available_attacks):
            status = "[x]" if attack in self.enabled_attacks else "[ ]"
            label = Label(f"  {status} {attack} ({i})")
            attacks_container.mount(label)
        
        attacks_container.refresh(layout=True)

    def on_key(self, event):
        self.notify(f"Key: {event.key}")
        if self.query_one(ContentSwitcher).current == "attacks":
            key = event.key
            if key in [str(i) for i in range(len(self.available_attacks))]:
                attack = self.available_attacks[int(key)]
                if attack in self.enabled_attacks:
                    self.enabled_attacks.remove(attack)
                else:
                    self.enabled_attacks.append(attack)
                self.notify(f"Toggled {attack}: {attack in self.enabled_attacks}")
                self.render_attacks()

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        if event.node.data:
            self.query_one(ContentSwitcher).current = event.node.data

    def action_run(self):
        student_file = self.query_one("#student_file", Input).value
        self.notify(f"Running generation for {student_file}...")

if __name__ == "__main__":
    PCAPApp().run()

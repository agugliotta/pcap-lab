import os
import shutil
import sys
import time
import types
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator
from generator.utils.network import default_interface, interface_exists, list_interfaces

try:
    import questionary
except ImportError:  # pragma: no cover - exercised when dependency is unavailable
    questionary = types.ModuleType("questionary")

    class _Prompt:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def ask(self):
            return None

    def _factory(*args, **kwargs):
        return _Prompt(*args, **kwargs)

    questionary.select = _factory
    questionary.text = _factory
    questionary.path = _factory
    questionary.confirm = _factory
    sys.modules.setdefault("questionary", questionary)

class PcapLabShell:
    """
    Provides an interactive CLI interface for configuring and executing traffic generation.
    """
    def __init__(self):
        self.config = {
            "student_list": "",
            "student_file": "",
            "interface": default_interface(),
            "requests": 50,
            "attack_ratio": 0.3,
            "obfuscation": 1,
            "jobs": 4,
            "enabled_attacks": ["sqli", "xss", "idor", "csrf", "rce", "lfi", "cmdi"]
        }
        self.art = [
            " ____   ____    _    ____  ",
            "|  _ \\ / ___|  / \\  |  _ \\ ",
            "| |_) | |     / _ \\ | |_) |",
            "|  __/| |___ / ___ \\|  __/ ",
            "|_|    \\____/_/   \\_\\_|    "
        ]

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self, title=""):
        self.clear_screen()
        for line in self.art:
            print(line)
        print("Version: v0.3 | Author: Agustín Gugliotta")
        print("============================================")
        if title:
            print(f"--- {title} ---")

    def _student_source_summary(self):
        sources = []
        if self.config["student_list"]:
            sources.append("inline list")
        if self.config["student_file"]:
            sources.append("file")
        return ", ".join(sources) if sources else "not configured"

    def print_config_summary(self):
        print()
        print("Current configuration")
        print(f"  Students: {self._student_source_summary()}")
        print(f"  Interface: {self.config['interface']}")
        print(f"  Requests: {self.config['requests']}")
        print(f"  Attack ratio: {self.config['attack_ratio']}")
        print(f"  Obfuscation: {self.config['obfuscation']}")
        print(f"  Jobs: {self.config['jobs']}")
        print(f"  Enabled attacks: {', '.join(self.config['enabled_attacks'])}")

    def _print_interface_hint(self):
        interfaces = ", ".join(list_interfaces())
        if interfaces:
            print(f"Available interfaces: {interfaces}")
        else:
            print("Unable to detect local interfaces automatically.")

    def configure(self):
        while True:
            self.print_banner("Settings")
            self.print_config_summary()
            choice = questionary.select(
                "Select setting to configure:",
                choices=[
                    f"Student List: {self.config['student_list'] or 'Empty'}",
                    f"Student File: {self.config['student_file'] or 'Empty'}",
                    f"Interface: {self.config['interface']}",
                    f"Requests: {self.config['requests']}",
                    f"Attack Ratio: {self.config['attack_ratio']}",
                    f"Obfuscation: {self.config['obfuscation']}",
                    f"Jobs: {self.config['jobs']}",
                    "Back"
                ]
            ).ask()

            if choice is None or choice == "Back":
                break
            
            self.clear_screen()
            if "Student List" in choice:
                val = questionary.text("Enter student list (comma-separated):", default=self.config['student_list']).ask()
                if val is not None:
                    self.config['student_list'] = val
            elif "Student File" in choice:
                val = questionary.path("Enter student file path:", default=self.config['student_file']).ask()
                if val is not None:
                    self.config['student_file'] = val
            elif "Interface" in choice:
                val = questionary.text("Enter interface:", default=self.config['interface']).ask()
                if val is not None:
                    self.config['interface'] = val
            elif "Requests" in choice:
                val = questionary.text("Enter requests:", default=str(self.config['requests'])).ask()
                if val is not None:
                    try:
                        requests = int(val)
                        if requests <= 0:
                            raise ValueError
                        self.config['requests'] = requests
                    except ValueError:
                        print("Requests must be a positive integer!")
                        time.sleep(1)
            elif "Attack Ratio" in choice:
                val = questionary.text("Enter ratio:", default=str(self.config['attack_ratio'])).ask()
                if val is not None:
                    try:
                        ratio = float(val)
                        if not 0.0 <= ratio <= 1.0:
                            raise ValueError
                        self.config['attack_ratio'] = ratio
                    except ValueError:
                        print("Attack ratio must be between 0.0 and 1.0!")
                        time.sleep(1)
            elif "Obfuscation" in choice:
                val = questionary.text("Enter level (1-3):", default=str(self.config['obfuscation'])).ask()
                if val is not None:
                    try:
                        lvl = int(val)
                        if 1 <= lvl <= 3:
                            self.config['obfuscation'] = lvl
                        else:
                            print("Obfuscation level must be 1, 2, or 3!")
                            time.sleep(1)
                    except ValueError:
                        print("Invalid integer entered!")
                        time.sleep(1)
            elif "Jobs" in choice:
                val = questionary.text("Enter number of parallel jobs:", default=str(self.config['jobs'])).ask()
                if val is not None:
                    try:
                        jobs = int(val)
                        if jobs <= 0:
                            raise ValueError
                        self.config['jobs'] = jobs
                    except ValueError:
                        print("Jobs must be a positive integer!")
                        time.sleep(1)

    def run_menu(self):
        while True:
            self.print_banner("Dashboard")
            self.print_config_summary()
            choice = questionary.select(
                "Select action:",
                choices=["Run Generation", "Configure", "Clean Output", "Quit"]
            ).ask()

            if choice == "Quit" or choice is None:
                break
            elif choice == "Clean Output":
                self.clear_screen()
                if os.path.exists("output"):
                    confirmed = questionary.confirm(
                        "Delete the entire output directory?",
                        default=False,
                    ).ask()
                    if confirmed:
                        shutil.rmtree("output")
                        print("Output cleaned.")
                    else:
                        print("Clean output canceled.")
                else:
                    print("Nothing to clean.")
                input("\nPress Enter to continue...")
            elif choice == "Configure":
                self.configure()
            elif choice == "Run Generation":
                self.clear_screen()
                if not self.config['student_list'] and not self.config['student_file']:
                    print("Error: Set students list or file first!")
                    input("\nPress Enter to continue...")
                    continue

                if not interface_exists(self.config["interface"]):
                    print(f"Error: interface '{self.config['interface']}' does not exist on this machine.")
                    self._print_interface_hint()
                    input("\nPress Enter to continue...")
                    continue
                
                print("\nGenerating...")
                student_ids = []
                if self.config['student_file']:
                    with open(self.config['student_file'], 'r') as f:
                        student_ids.extend([line.strip() for line in f if line.strip()])
                if self.config['student_list']:
                    student_ids.extend([s.strip() for s in self.config['student_list'].split(',') if s.strip()])
                    
                engines = [TrafficEngine(
                    student_id=sid,
                    num_requests=self.config['requests'],
                    attack_ratio=self.config['attack_ratio'],
                    obfuscation_level=self.config['obfuscation'],
                    enabled_attacks=self.config['enabled_attacks']
                ) for sid in student_ids]
                
                generator = PcapGenerator(interface=self.config['interface'])
                generator.generate_batch(engines=engines, jobs=self.config['jobs'])
                print("Batch Complete!")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    PcapLabShell().run_menu()

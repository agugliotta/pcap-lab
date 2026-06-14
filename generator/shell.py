import questionary
import sys
import os
import shutil
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator

class PcapLabShell:
    def __init__(self):
        self.config = {
            "student_list": "",
            "student_file": "",
            "interface": "lo",
            "requests": 50,
            "attack_ratio": 0.3,
            "obfuscation": 1,
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

    def configure(self):
        while True:
            self.print_banner("Settings")
            choice = questionary.select(
                "Select setting to configure:",
                choices=[
                    f"Student List: {self.config['student_list'] or 'Empty'}",
                    f"Student File: {self.config['student_file'] or 'Empty'}",
                    f"Interface: {self.config['interface']}",
                    f"Requests: {self.config['requests']}",
                    f"Attack Ratio: {self.config['attack_ratio']}",
                    f"Obfuscation: {self.config['obfuscation']}",
                    "Back"
                ]
            ).ask()

            if choice == "Back":
                break
            
            if "Student List" in choice:
                self.config['student_list'] = questionary.text("Enter student list (comma-separated):", default=self.config['student_list']).ask()
            elif "Student File" in choice:
                self.config['student_file'] = questionary.path("Enter student file path:", default=self.config['student_file']).ask()
            elif "Interface" in choice:
                self.config['interface'] = questionary.text("Enter interface:", default=self.config['interface']).ask()
            elif "Requests" in choice:
                self.config['requests'] = int(questionary.text("Enter requests:", default=str(self.config['requests'])).ask())
            elif "Attack Ratio" in choice:
                self.config['attack_ratio'] = float(questionary.text("Enter ratio:", default=str(self.config['attack_ratio'])).ask())
            elif "Obfuscation" in choice:
                self.config['obfuscation'] = int(questionary.text("Enter level (1-3):", default=str(self.config['obfuscation'])).ask())

    def run_menu(self):
        while True:
            self.print_banner("Dashboard")
            choice = questionary.select(
                "Select action:",
                choices=["Run Generation", "Configure", "Clean Output", "Quit"]
            ).ask()

            if choice == "Quit":
                break
            elif choice == "Clean Output":
                if os.path.exists("output"):
                    shutil.rmtree("output")
                    print("Output cleaned.")
                else:
                    print("Nothing to clean.")
                input("\nPress Enter to continue...")
            elif choice == "Configure":
                self.configure()
            elif choice == "Run Generation":
                if not self.config['student_list'] and not self.config['student_file']:
                    print("Error: Set students list or file first!")
                    input("\nPress Enter to continue...")
                    continue
                
                print("\nGenerating...")
                # Simplified generation logic
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
                generator.generate_batch(engines=engines, jobs=4)
                print("Batch Complete!")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    PcapLabShell().run_menu()

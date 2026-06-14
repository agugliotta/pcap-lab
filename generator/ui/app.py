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

    def configure(self):
        while True:
            choice = questionary.select(
                "Configure Settings",
                choices=[
                    f"Student List (Current: {self.config['student_list'] or 'Empty'})",
                    f"Student File (Current: {self.config['student_file'] or 'Empty'})",
                    f"Interface (Current: {self.config['interface']})",
                    f"Requests (Current: {self.config['requests']})",
                    f"Attack Ratio (Current: {self.config['attack_ratio']})",
                    f"Obfuscation (Current: {self.config['obfuscation']})",
                    "Back"
                ]
            ).ask()

            if choice == "Back":
                break
            
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
            choice = questionary.select(
                "PCAP Lab Control Center",
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
            elif choice == "Configure":
                self.configure()
            elif choice == "Run Generation":
                # ... generation logic ...
                pass

if __name__ == "__main__":
    PcapLabShell().run_menu()

import questionary
import sys
from generator.traffic_engine import TrafficEngine
from generator.pcap_generator import PcapGenerator

def run_menu():
    config = {
        "student_list": "",
        "student_file": "",
        "interface": "lo",
        "requests": 50,
        "attack_ratio": 0.3,
        "obfuscation": 1,
        "enabled_attacks": ["sqli", "xss", "idor", "csrf", "rce", "lfi", "cmdi"]
    }

    while True:
        choice = questionary.select(
            "PCAP Lab Control Center",
            choices=["Run Generation", "Configure", "Clean Output", "Quit"]
        ).ask()

        if choice == "Quit":
            break
        elif choice == "Clean Output":
            import shutil
            if os.path.exists("output"):
                shutil.rmtree("output")
            print("Output cleaned.")
        elif choice == "Configure":
            config["student_list"] = questionary.text("Student List:").ask() or config["student_list"]
            config["student_file"] = questionary.path("Student File Path:").ask() or config["student_file"]
            config["interface"] = questionary.text("Interface:", default=config["interface"]).ask()
            config["requests"] = int(questionary.text("Requests:", default=str(config["requests"])).ask())
            config["attack_ratio"] = float(questionary.text("Attack Ratio:", default=str(config["attack_ratio"])).ask())
            config["obfuscation"] = int(questionary.text("Obfuscation (1-3):", default=str(config["obfuscation"])).ask())
            config["enabled_attacks"] = questionary.checkbox(
                "Enable Attacks:",
                choices=[{"name": a, "checked": a in config["enabled_attacks"]} for a in config["enabled_attacks"] + [a for a in ["sqli", "xss", "idor", "csrf", "rce", "lfi", "cmdi"] if a not in config["enabled_attacks"]]]
            ).ask()
            
        elif choice == "Run Generation":
            if not config['student_list'] and not config['student_file']:
                print("Error: Set student list or file first!")
                continue
            
            print("Generating...")
            # ... (generation logic)
            print("Batch Complete!")

if __name__ == "__main__":
    run_menu()

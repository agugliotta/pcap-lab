<div align="center">
  <img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/wireshark.svg" width="100" height="100" alt="PCAP Lab Logo">
  <h1>PCAP Lab Generator</h1>
  <p><i>A deterministic HTTP traffic generator for cybersecurity laboratories and WAF testing.</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  </p>

  <h4>
    <a href="#-key-features">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-educational-workflow">Workflow</a>
  </h4>
</div>

---

**PCAP Lab Generator** is a specialized tool designed to bridge the gap between synthetic packet crafting and manual browsing. It generates **deterministic HTTP traffic** that blends realistic user behavior with sophisticated web attacks, outputting industry-standard **PCAP files** ready for deep packet inspection (DPI) and security analysis.

Unlike traditional random traffic generators, this tool ensures **100% reproducibility** by using a seed-based approach. This makes it the ideal companion for **cybersecurity educators** building labs, and **security engineers** validating **WAF (Web Application Firewall)** rules, IDS/IPS signatures, or ModSecurity CRS configurations.

## 🛡️ Key Features

- 🎯 **Deterministic Traffic:** Uses a `STUDENT_ID` seed to guarantee identical attack sequences and payloads for every run—perfect for consistent grading and benchmarking.
- 🧱 **Realistic Simulation:** Emulates diverse User-Agents, varied HTTP headers, and normal navigation patterns to hide malicious signatures in noise.
- 🧪 **Multi-Vector Attack Library:** Built-in modules for **SQL Injection (SQLi)**, **XSS**, **RCE**, **LFI**, **IDOR**, **CSRF**, and **Command Injection**.
- ✅ **Automated Ground Truth:** Generates a detailed `answer_key.json` mapping every attack to its exact timestamp and payload for automated validation.
- 📦 **Modern CLI:** A unified Python interface built with `Click` for seamless generation, replay, and testing workflows.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/agugliotta/pcap-lab.git
cd pcap-lab

# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> [!IMPORTANT]
> Packet capture (tcpdump) and traffic replay (tcpreplay) require root privileges. Always run generation and replay commands with `sudo`.

## 🖥️ Interactive Shell (`main.py shell`)

For an easier configuration experience, use the interactive shell:

```bash
sudo .venv/bin/python main.py shell
```

This interface allows you to:
- Configure student lists, files, interfaces, and attack parameters (volume, ratio, obfuscation).
- Easily clean the output directory.
- Run traffic generation batch jobs directly.

## ⚙️ Configuring Attacks (`attacks.json`)

You can extend or modify the attack library using `generator/attacks.json`. This file maps simple attack keys to their corresponding Python classes in the project structure:

```json
{
  "sqli": "generator.attacks.sqli.SQLIAttack",
  "xss": "generator.attacks.xss.XSSAttack",
  ...
}
```

To add a new attack, define its class and add its path to this registry.

## ⏱️ Quick Start

Generate a unique trace for a student named `agustin` on the loopback interface:

```bash
# Generate deterministic traffic
sudo .venv/bin/python main.py generate agustin lo
```

The artifacts will be generated in `output/agustin/`:
- `traffic.pcap`: The full raw network capture.
- `answer_key.json`: The "ground truth" metadata for automated grading or verification.

## 🎓 Educational Workflow

This tool facilitates a complete **Attack-Detection-Defense** cycle:

1.  **Offense (Generate):** Fire the generator to create a trace containing a mix of malicious and normal traffic.
2.  **Analysis (Detect):** Students use **Wireshark** or **TShark** to identify attack signatures based on the `answer_key.json`.
3.  **Defense (Mitigate):** Write and apply defensive rules (e.g., **ModSecurity CRS**) to block the identified vectors.
4.  **Validation (Replay):** Use the `replay` command to fire the exact same traffic against the protected target to verify mitigation success.

## 📖 Advanced Usage

### Customizing Attack Composition
Focus your lab on specific vulnerabilities or control the "noise" ratio:

```bash
# Focus only on Remote Code Execution and SQLi
sudo .venv/bin/python main.py generate test lo --attacks rce,sqli

# Set exact attack volume (e.g., 20% malicious traffic)
sudo .venv/bin/python main.py generate test lo --requests 100 --attack-ratio 0.2
```

### Flexible Traffic Replay
Replay captured traffic against an external WAF or a Docker container:

```bash
# Rewrite destination IP and Port on the fly
sudo .venv/bin/python main.py replay lo output/agustin/traffic.pcap --target-ip 172.17.0.2 --target-port 80
```

## 🧪 Testing

We use `pytest` to ensure everything is working correctly:

```bash
.venv/bin/python main.py test
```

## 🛡️ WAF Validation (ModSecurity)

Validate your rules against deterministic payloads. Here are some typical rules to detect the attacks generated by this lab:

### SQL Injection
```apache
SecRule ARGS "@detectSQLi" \
    "id:1001,phase:2,t:none,t:urlDecodeUni,block,msg:'SQL Injection Detected'"
```

### Remote Code Execution (RCE) / Command Injection
```apache
SecRule ARGS "@pm system exec passthru shell_exec" \
    "id:1002,phase:2,t:none,t:lowercase,block,msg:'Potential RCE detected'"

SecRule ARGS "@rx [;&|`\$]" \
    "id:1003,phase:2,t:none,block,msg:'Command Injection Characters Detected'"
```

### Local File Inclusion (LFI)
```apache
SecRule ARGS "@rx \.\./\.\./" \
    "id:1004,phase:2,t:none,t:urlDecodeUni,block,msg:'Path Traversal Attempt'"
```

---

<div align="center">
  <sub>Built for the next generation of Cybersecurity Professionals</sub>
</div>

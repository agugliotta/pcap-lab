<div align="center">
  <img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/wireshark.svg" width="100" height="100" alt="PCAP Lab Logo">
  <h1>PCAP Lab Generator</h1>
  <p><i>A deterministic HTTP traffic generator for cybersecurity laboratories.</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  </p>

  <h4>
    <a href="#-features">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-usage">Usage</a>
  </h4>
</div>

---

This tool generates deterministic HTTP traffic to simulate realistic web environments for cybersecurity training. It creates a mix of normal user behavior and common web attacks, capturing everything into PCAP files for analysis.

> [!NOTE]
> This project was designed for educational purposes. Use it to practice traffic analysis, WAF rule creation (ModSecurity), and incident response.

## 🚀 Features

- 🛡️ **Attack Simulation:** Includes SQL Injection, Cross-Site Scripting (XSS), IDOR, and CSRF.
- 🎯 **Deterministic:** Uses a `STUDENT_ID` as a seed to generate identical traffic for the same student every time.
- 🌐 **Realistic Traffic:** Simulates diverse user agents, varied headers, and normal navigation patterns.
- ✅ **Ground Truth:** Automatically generates an `answer_key.json` for easy automated grading.
- 📦 **Unified CLI:** A single Python-based CLI (`pcap-lab`) to manage generation, replay, and testing.

## 💎 Why Determinism Matters?

In network security education, randomness is the enemy of consistent grading and clear analysis. This project solves this by ensuring:

*   **Reproducibility:** The same `STUDENT_ID` will always generate the exact same attack sequence and payloads.
*   **Predictable Grading:** Instructors can verify student findings against a pre-calculated `answer_key.json` that is guaranteed to match the traffic.
*   **Realistic Artifacts:** Unlike synthetic packet builders (like Scapy), we use a real OS network stack. This results in realistic TCP sequences and timestamps while maintaining application-layer determinism.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/youruser/pcap-lab.git
cd pcap-lab

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> [!IMPORTANT]
> Capturing network traffic and replaying it requires root privileges. Ensure you have `sudo` access on your machine.

## ⏱️ Quick Start

Generate traffic for a student named `agustin` using the unified CLI:

```bash
# Using the CLI directly
sudo .venv/bin/python main.py generate agustin lo
```

The artifacts will be available in `output/agustin/`:
- `traffic.pcap`: The full network capture.
- `answer_key.json`: List of all attacks executed and their timestamps.

## 🎓 Educational Workflow

This tool is designed to facilitate a complete **Attack-Defend** cycle in a classroom setting:

1.  **Offense (Generation):** The student or professor runs the `generate` command. This creates a unique trace of malicious and normal traffic.
2.  **Analysis (Detection):** Students open the PCAP in Wireshark to identify the signatures, IP patterns, and payloads of the attacks listed in the `answer_key.json`.
3.  **Defense (Mitigation):** Students write defensive rules (e.g., ModSecurity CRS) to block the identified attacks.
4.  **Validation (Replay):** Using the `replay` command, the same traffic is fired against the student's WAF. If the rules are correct, the WAF logs will show the blocked requests, confirming the defense is successful.

## 📖 Usage

The project uses a unified CLI.

### 1. Generating Traffic
By default, the generator uses the loopback interface (`lo` or `lo0`).

```bash
# Standard generation
sudo .venv/bin/python main.py generate test lo

# Selective attacks (e.g., only SQLi and XSS)
sudo .venv/bin/python main.py generate test lo --attacks sqli,xss

# Define an exact number of total requests
sudo .venv/bin/python main.py generate test lo --requests 50
```

> [!TIP]
> Use the `--attacks` option to focus the lab on specific vectors. Available types: `sqli`, `xss`, `idor`, `csrf`.
> Use the `--requests` option to generate an exact number of HTTP requests (by default, it chooses a random number between 50 and 100).


### 2. Analyze with Wireshark
Open the generated PCAP in Wireshark to inspect the attacks:
```bash
wireshark output/agustin/traffic.pcap
```

### 3. Replay against a WAF
You can replay the captured traffic against a real WAF like ModSecurity.

```bash
# Standard replay
sudo .venv/bin/python main.py replay lo output/agustin/traffic.pcap

# Replay with IP/Port rewriting (for external targets)
sudo .venv/bin/python main.py replay lo output/agustin/traffic.pcap --target-ip 172.17.0.2 --target-port 80
```

#### 🔄 Flexible Replay (Advanced)
If your WAF is running in a different environment (like a Docker container or an external server), use the `--target-ip` and `--target-port` options to rewrite the destination headers on the fly.

## 🧪 Testing

We use `pytest` to ensure everything is working correctly:

```bash
.venv/bin/python main.py test
```

## 🛡️ ModSecurity Example

A typical rule to detect the SQLi attacks generated by this lab:

```apache
SecRule ARGS "@detectSQLi" \
    "id:1001,phase:2,t:none,t:urlDecodeUni,block,msg:'SQL Injection Detected'"
```

---

<div align="center">
  <sub>Built with ❤️ for Cybersecurity Education</sub>
</div>

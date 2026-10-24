#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import json
import ipaddress
import tempfile
import struct
from pathlib import Path
import click

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from generator.utils.network import interface_exists, list_interfaces
from generator.utils.output import clean_output


def _interface_hint():
    interfaces = ", ".join(list_interfaces())
    if interfaces:
        return f"Available interfaces: {interfaces}"
    return "Unable to detect local interfaces automatically."


@click.group()
def cli():
    """PCAP Lab Generator CLI"""
    pass


@cli.command()
@click.argument("student_ids", nargs=-1)
@click.argument("interface")
@click.option("--output-dir", default="output", help="Base directory for generated files.")
@click.option(
    "--students-file",
    type=click.Path(exists=True, dir_okay=False),
    help="File containing a list of student IDs (one per line).",
)
@click.option("--attacks", help="Comma-separated list of attack types to include (e.g. sqli,xss).")
@click.option("--requests", type=click.IntRange(min=1), help="Exact number of total requests to generate.")
@click.option("--attack-count", type=click.IntRange(min=0), help="Exact number of attacks to generate.")
@click.option(
    "--attack-ratio",
    type=click.FloatRange(0, 1),
    help="Ratio of attacks to total requests (float between 0.0 and 1.0).",
)
@click.option("--jobs", type=click.IntRange(min=1), default=1, help="Number of parallel jobs for generation.")
@click.option("--obfuscation", type=click.IntRange(1, 3), default=1, help="Obfuscation level (1-3) for attack payloads.")
def generate(student_ids, interface, output_dir, students_file, attacks, requests, attack_count, attack_ratio, jobs, obfuscation):
    """Generate deterministic HTTP traffic and capture it to a PCAP file for one or more students."""
    from generator.attack_registry import AttackRegistry
    from generator.traffic_engine import TrafficEngine
    from generator.pcap_generator import PcapGenerator

    if os.geteuid() != 0:
        click.echo("Warning: Generating traffic usually requires sudo for packet capture.", err=True)

    final_student_ids = list(student_ids)
    if students_file:
        try:
            with open(students_file, "r", encoding="utf-8") as f:
                final_student_ids.extend([line.strip() for line in f if line.strip()])
        except (OSError, UnicodeError) as exc:
            raise click.ClickException(f"Cannot read students file: {exc}") from exc

    if not final_student_ids:
        click.echo("Error: No student IDs provided via arguments or --students-file.", err=True)
        sys.exit(1)

    if not interface_exists(interface):
        click.echo(f"Error: interface '{interface}' does not exist on this machine.", err=True)
        click.echo(_interface_hint(), err=True)
        sys.exit(1)

    enabled_attacks = None
    if attacks:
        enabled_attacks = [a.strip().lower() for a in attacks.split(",")]
        available_attacks = set(AttackRegistry().get_all_attack_names())
        invalid_attacks = [attack for attack in enabled_attacks if attack not in available_attacks]
        if invalid_attacks:
            click.echo(
                "Warning: unknown attack type(s) ignored: " + ", ".join(invalid_attacks),
                err=True,
            )
            click.echo(
                "Available attacks: " + ", ".join(sorted(available_attacks)),
                err=True,
            )
            enabled_attacks = [attack for attack in enabled_attacks if attack in available_attacks]
            if not enabled_attacks:
                click.echo("Error: no valid attack types remain after filtering.", err=True)
                sys.exit(1)

    try:
        engines = [
            TrafficEngine(
                student_id=student_id,
                enabled_attacks=enabled_attacks,
                num_requests=requests,
                attack_count=attack_count,
                attack_ratio=attack_ratio,
                obfuscation_level=obfuscation,
            )
            for student_id in final_student_ids
        ]

        generator = PcapGenerator(
            interface=interface,
            output_dir=output_dir,
        )

        generator.generate_batch(engines=engines, jobs=jobs)
    except (OSError, ValueError, RuntimeError) as exc:
        click.echo(f"Error during generation: {exc}", err=True)
        click.echo("Hint: install tcpdump, confirm the capture interface is correct, and rerun with sudo.", err=True)
        sys.exit(1)

    click.echo(f"Successfully generated traffic for {len(final_student_ids)} students.")


@cli.command()
@click.argument("interface")
@click.argument("pcap_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--target-ip", help="Rewrite destination IP (default maps 127.0.0.1 to this IP)")
@click.option("--target-port", type=click.IntRange(1, 65535), help="Rewrite the captured server port to this port.")
@click.option("--source-port", type=click.IntRange(1, 65535), help="Captured server port; defaults to answer_key.json, or 8080 for legacy captures.")
def replay(interface, pcap_file, target_ip, target_port, source_port):
    """Replay a PCAP file on a specific network interface using tcpreplay."""
    if shutil.which("tcpreplay") is None:
        click.echo("Error: tcpreplay is not installed. Please install it first.", err=True)
        sys.exit(1)

    if os.geteuid() != 0:
        click.echo("Warning: Replaying traffic usually requires sudo.", err=True)

    if not interface_exists(interface):
        click.echo(f"Error: interface '{interface}' does not exist on this machine.", err=True)
        click.echo(_interface_hint(), err=True)
        sys.exit(1)

    if target_ip or target_port:
        with open(pcap_file, "rb") as capture:
            header = capture.read(24)
        # tcprewrite can silently skip edits when preserving BSD loopback framing.
        byte_orders = {b"\xd4\xc3\xb2\xa1": "<", b"\x4d\x3c\xb2\xa1": "<",
                       b"\xa1\xb2\xc3\xd4": ">", b"\xa1\xb2\x3c\x4d": ">"}
        byte_order = byte_orders.get(header[:4])
        if len(header) == 24 and byte_order and struct.unpack(byte_order + "I", header[20:24])[0] & 0xFFFF == 0:
            raise click.ClickException("tcprewrite cannot reliably rewrite BSD loopback (DLT_NULL) captures. Convert to RAW or Ethernet first and select a compatible replay interface.")

    if target_ip:
        try:
            ipaddress.IPv4Address(target_ip)
        except ipaddress.AddressValueError as exc:
            raise click.BadParameter("Expected an IPv4 address.", param_hint="--target-ip") from exc

    if target_port and source_port is None:
        key_file = Path(pcap_file).with_name("answer_key.json")
        if key_file.exists():
            try:
                source_port = json.loads(key_file.read_text())["server_port"]
                if type(source_port) is not int or not 1 <= source_port <= 65535:
                    raise ValueError("Invalid server_port")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise click.ClickException("Cannot read captured server port; pass --source-port explicitly.") from exc
        else:
            source_port = 8080

    with tempfile.TemporaryDirectory(prefix="pcap-replay-") as temp_dir:
        replay_file = pcap_file
        try:
            if target_ip or target_port:
                if shutil.which("tcprewrite") is None:
                    raise click.ClickException("tcprewrite is not installed (needed for IP/Port mapping).")
                replay_file = os.path.join(temp_dir, "traffic.pcap")
                rewrite_cmd = ["tcprewrite", "--infile=" + pcap_file, "--outfile=" + replay_file]
                if target_ip:
                    rewrite_cmd.append(f"--dstipmap=127.0.0.1/32:{target_ip}/32")
                if target_port:
                    rewrite_cmd.append(f"--portmap={source_port}:{target_port}")
                rewrite_cmd.append("--fixcsum")
                subprocess.run(rewrite_cmd, check=True)
            click.echo(f"Replaying {replay_file} on {interface}...")
            subprocess.run(["tcpreplay", "--intf1=" + interface, "--topspeed", replay_file], check=True)
        except (subprocess.CalledProcessError, OSError) as exc:
            raise click.ClickException(f"Replay failed: {exc}") from exc


@cli.command()
def test():
    """Run the project test suite using pytest."""
    click.echo("Running tests...")
    try:
        # Use sys.executable to ensure we use the same environment
        subprocess.run([sys.executable, "-m", "pytest", "tests/"], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Tests failed with exit code {e.returncode}", err=True)
        sys.exit(e.returncode)


@cli.command()
@click.option("--output-dir", default="output", help="Output directory to clean.")
def clean(output_dir):
    """Remove generated output only; refuse directories containing unrelated files."""
    try:
        clean_output(output_dir)
    except (OSError, ValueError) as exc:
        raise click.ClickException(f"Cannot clean output: {exc}") from exc
    click.echo("Done.")


@cli.command()
def shell():
    """Launch the interactive Pcap-Lab Shell."""
    import subprocess
    import sys

    # Run the interactive shell
    try:
        subprocess.run([sys.executable, "-m", "generator.shell"], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    cli()

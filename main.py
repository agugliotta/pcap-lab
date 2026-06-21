#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import click

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


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
    type=click.Path(exists=True),
    help="File containing a list of student IDs (one per line).",
)
@click.option("--attacks", help="Comma-separated list of attack types to include (e.g. sqli,xss).")
@click.option("--requests", type=int, help="Exact number of total requests to generate.")
@click.option("--attack-count", type=int, help="Exact number of attacks to generate.")
@click.option(
    "--attack-ratio",
    type=float,
    help="Ratio of attacks to total requests (float between 0.0 and 1.0).",
)
@click.option("--jobs", type=int, default=1, help="Number of parallel jobs for generation.")
@click.option("--obfuscation", type=int, default=1, help="Obfuscation level (1-3) for attack payloads.")
def generate(student_ids, interface, output_dir, students_file, attacks, requests, attack_count, attack_ratio, jobs, obfuscation):
    """Generate deterministic HTTP traffic and capture it to a PCAP file for one or more students."""
    from generator.traffic_engine import TrafficEngine
    from generator.pcap_generator import PcapGenerator

    if os.geteuid() != 0:
        click.echo("Warning: Generating traffic usually requires sudo for packet capture.", err=True)

    final_student_ids = list(student_ids)
    if students_file:
        with open(students_file, "r") as f:
            final_student_ids.extend([line.strip() for line in f if line.strip()])

    if not final_student_ids:
        click.echo("Error: No student IDs provided via arguments or --students-file.", err=True)
        sys.exit(1)

    enabled_attacks = None
    if attacks:
        enabled_attacks = [a.strip().lower() for a in attacks.split(",")]

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
    click.echo(f"Successfully generated traffic for {len(final_student_ids)} students.")


@cli.command()
@click.argument("interface")
@click.argument("pcap_file", type=click.Path(exists=True))
@click.option("--target-ip", help="Rewrite destination IP (default maps 127.0.0.1 to this IP)")
@click.option("--target-port", type=int, help="Rewrite destination port (default maps 8080 to this port)")
def replay(interface, pcap_file, target_ip, target_port):
    """Replay a PCAP file on a specific network interface using tcpreplay."""
    if shutil.which("tcpreplay") is None:
        click.echo("Error: tcpreplay is not installed. Please install it first.", err=True)
        sys.exit(1)

    if os.geteuid() != 0:
        click.echo("Warning: Replaying traffic usually requires sudo.", err=True)

    replay_file = pcap_file

    # If IP or Port is provided, we need to rewrite the PCAP
    if target_ip or target_port:
        if shutil.which("tcprewrite") is None:
            click.echo("Error: tcprewrite is not installed (needed for IP/Port mapping).", err=True)
            sys.exit(1)

        temp_pcap = pcap_file + ".tmp"
        rewrite_cmd = ["tcprewrite", "--infile=" + pcap_file, "--outfile=" + temp_pcap]

        if target_ip:
            click.echo(f"Mapping 127.0.0.1 to {target_ip}...")
            rewrite_cmd.append(f"--dstipmap=127.0.0.1/32:{target_ip}/32")

        if target_port:
            click.echo(f"Mapping port 8080 to {target_port}...")
            rewrite_cmd.append(f"--portmap=8080:{target_port}")

        rewrite_cmd.append("--fixcsum")

        try:
            subprocess.run(rewrite_cmd, check=True)
            replay_file = temp_pcap
        except subprocess.CalledProcessError as e:
            click.echo(f"Error during tcprewrite: {e}", err=True)
            sys.exit(e.returncode)

    click.echo(f"Replaying {replay_file} on {interface}...")
    try:
        subprocess.run(["tcpreplay", "--intf1=" + interface, "--topspeed", replay_file], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during replay: {e}", err=True)
        sys.exit(e.returncode)
    finally:
        # Clean up temporary file if it was created
        if replay_file != pcap_file and os.path.exists(replay_file):
            os.remove(replay_file)


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
    """Remove generated output, __pycache__, and pytest cache."""
    if os.path.exists(output_dir):
        click.echo(f"Cleaning {output_dir}...")
        try:
            shutil.rmtree(output_dir)
        except PermissionError:
            click.echo(f"Permission denied for {output_dir}. Use sudo to clean it.", err=True)

    click.echo("Cleaning python cache files...")
    for root, dirs, files in os.walk(".", topdown=False):
        for name in dirs:
            if name == "__pycache__" or name == ".pytest_cache":
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                except Exception:
                    pass  # Best effort for cache cleanup

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

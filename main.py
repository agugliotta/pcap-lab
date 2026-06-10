import os
import sys
import subprocess
import shutil
import click

# Ensure the project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generator.generate_pcap import generate_pcap

@click.group()
def cli():
    """PCAP Lab Generator CLI"""
    pass

@cli.command()
@click.argument('student_id')
@click.argument('interface')
@click.option('--output-dir', default='output', help='Base directory for generated files.')
def generate(student_id, interface, output_dir):
    """Generate deterministic HTTP traffic and capture it to a PCAP file."""
    if os.geteuid() != 0:
        click.echo("Warning: Generating traffic usually requires sudo for packet capture.", err=True)
    
    try:
        generate_pcap(student_id, interface, output_dir)
        click.echo(f"Successfully generated traffic for student: {student_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('interface')
@click.argument('pcap_file', type=click.Path(exists=True))
def replay(interface, pcap_file):
    """Replay a PCAP file on a specific network interface using tcpreplay."""
    if shutil.which("tcpreplay") is None:
        click.echo("Error: tcpreplay is not installed. Please install it first.", err=True)
        sys.exit(1)
    
    if os.geteuid() != 0:
        click.echo("Warning: Replaying traffic usually requires sudo.", err=True)
    
    click.echo(f"Replaying {pcap_file} on {interface}...")
    try:
        subprocess.run(["tcpreplay", "--intf1=" + interface, "--topspeed", pcap_file], check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during replay: {e}", err=True)
        sys.exit(e.returncode)

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
@click.option('--output-dir', default='output', help='Output directory to clean.')
def clean(output_dir):
    """Remove all generated output files."""
    if os.path.exists(output_dir):
        click.echo(f"Cleaning {output_dir}...")
        try:
            # We use sudo if needed, but here we try simple deletion first
            shutil.rmtree(output_dir)
            click.echo("Done.")
        except PermissionError:
            click.echo(f"Permission denied. Try running with sudo: sudo rm -rf {output_dir}", err=True)
            sys.exit(1)
    else:
        click.echo(f"Directory {output_dir} does not exist.")

if __name__ == '__main__':
    cli()

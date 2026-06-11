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
@click.option('--attacks', help='Comma-separated list of attack types to include (e.g. sqli,xss).')
@click.option('--requests', type=int, help='Exact number of total requests to generate.')
def generate(student_id, interface, output_dir, attacks, requests):
    """Generate deterministic HTTP traffic and capture it to a PCAP file."""
    if os.geteuid() != 0:
        click.echo("Warning: Generating traffic usually requires sudo for packet capture.", err=True)
    
    enabled_attacks = None
    if attacks:
        enabled_attacks = [a.strip().lower() for a in attacks.split(',')]
    
    try:
        generate_pcap(student_id, interface, output_dir, enabled_attacks=enabled_attacks, num_requests=requests)
        click.echo(f"Successfully generated traffic for student: {student_id}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('interface')
@click.argument('pcap_file', type=click.Path(exists=True))
@click.option('--target-ip', help='Rewrite destination IP (default maps 127.0.0.1 to this IP)')
@click.option('--target-port', type=int, help='Rewrite destination port (default maps 8080 to this port)')
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

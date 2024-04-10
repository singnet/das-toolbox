import click
import sys
import os


@click.group(help="Example CLI tool for Hyperon-DAS.")
def example():
    global script_name

    if getattr(sys, "frozen", False):
        script_name = os.path.basename(sys.executable)
    else:
        script_name = "python3 " + sys.argv[0]


@example.command(help="Echo commands for local setup.")
def local():
    click.echo(
        f"""
# Install Hyperon-DAS:
pip3 install hyperon-das

# Set the configuration file
{script_name} config set

# Start server services
{script_name} db start

# Validate a Metta file or directory
{script_name} metta check $PWD/examples/data/

# Load Metta files
{script_name} metta load $PWD/examples/data/animals.metta
"""
    )


@example.command(help="Echo commands for OpenFaaS setup.")
def faas():
    click.echo(
        f"""
# Set the configuration file
{script_name} config set

# Start server services
{script_name} db start

# Validate a Metta file or directory
{script_name} metta check $PWD/examples/data/

# Load Metta files
{script_name} metta load $PWD/examples/data/animals.metta

# Start OpenFaaS Service
{script_name} faas start
"""
    )

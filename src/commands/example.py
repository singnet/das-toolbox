import click
import sys
import os


@click.group()
def example():
    """
    The example command offers a step-by-step guide for using DAS.

    This command provides various topics to choose from, each offering a step-by-step guide to help you set up and configure DAS for different scenarios, such as local, connecting to OpenFaaS functions, and more.
    """
    global script_name

    if getattr(sys, "frozen", False):
        script_name = os.path.basename(sys.executable)
    else:
        script_name = "python3 " + sys.argv[0]


@example.command()
def local():
    """
    Echo commands for local setup.

    The \\fBdas-cli example local\\fR command displays an example of the initial steps required to run DAS locally on your server.

    .SH EXAMPLES

    Display an example of initial steps to run DAS locally.

    \\fB$ das-cli example local\\fR
    """

    click.echo(
        f"""
# Install Hyperon-DAS:
pip3 install hyperon-das

# Set the configuration file
{script_name} config set

# Start server services
{script_name} db start

# Validate a Metta file or directory
{script_name} metta check <metta file path>

# Load Metta files
{script_name} metta load <metta file path>
"""
    )


@example.command()
def faas():
    """
    Echo commands for OpenFaaS setup.

    The \\fBdas-cli example faas\\fR command displays an example of the initial steps required to connect to OpenFaaS functions using DAS.

    .SH EXAMPLES

    Display an example of initial steps to connect to OpenFaaS functions.

    \\fB$ das-cli example faas\\fR
    """
    click.echo(
        f"""
# Set the configuration file
{script_name} config set

# Start server services
{script_name} db start

# Validate a Metta file or directory
{script_name} metta check <metta file path>

# Load Metta files
{script_name} metta load <metta file path>

# Start OpenFaaS Service
{script_name} faas start
"""
    )

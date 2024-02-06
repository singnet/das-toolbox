import click


@click.group(help="Example CLI tool for Hyperon-DAS.")
def example():
    pass


@example.command(help="Echo commands for local setup.")
def local():
    click.echo(
        """
# Install Hyperon-DAS:
pip3 install hyperon-das

# Set the configuration file
python3 das-cli.py config set

# Start server services
python3 das-cli.py server start

# Validate a Metta file or directory
python3 das-cli.py metta validate --filepath $PWD/examples/data/

# Load Metta files
python3 das-cli.py metta load --path $PWD/examples/data/animals.metta

sleep 5

# Modify the examples/distributed_atom_space_remote.py file with the credentials added through the configuration command (MongoDB port, username, password, etc.).
python3 examples/distributed_atom_space_local.py
"""
    )


@example.command(help="Echo commands for OpenFaaS setup.")
def faas():
    click.echo(
        """
# Set the configuration file
python3 das-cli.py config set

# Start server services
python3 das-cli.py server start

# Validate a Metta file or directory
python3 das-cli.py metta validate --filepath $PWD/examples/data/

# Load Metta files
python3 das-cli.py metta load --path $PWD/examples/data/animals.metta

# Start OpenFaaS Service
python3 das-cli.py faas start --function queryengine --version 1.9.2

sleep 5

# Modify the examples/distributed_atom_space_remote.py file with the port openFaaS is running (default 8080).
python3 examples/distributed_atom_space_remote.py
"""
    )

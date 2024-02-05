# DAS Toolbox

## Overview

This CLI provides a set of commands to manage containerized services, OpenFaaS functions, and Metta operations. It includes functionalities to start and stop server services, manage OpenFaaS functions, load Metta files, and validate Metta file syntax.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment Options](#deployment-options)
- [Usage](#usage)
- [Local Distributed Atom Space](#local-distributed-atom-space)
- [Distributed Atom Space with OpenFaaS](#distributed-atom-space-with-openfaas)
- [Getting Help](#getting-help)
- [Troubleshooting](#troubleshooting)
  - [Docker Permission Denied](#docker-permission-denied)

## Prerequisites

- Docker
- Python 3.x
- Pip (Python package installer)

## Installation

To ensure a clean and isolated environment for running the DAS Toolbox, it is recommended to use a virtual environment. Follow these steps to set up the required prerequisites using a virtual environment:

1. **Create a Virtual Environment:**

   ```bash
   python3 -m venv env
   ```

   This command will create a virtual environment named `env` in the current directory.

2. **Activate the Virtual Environment:**

   ```bash
   source env/bin/activate
   ```

   After activation, your shell prompt should change to indicate that you are now working within the virtual environment.

3. **Install Prerequisites:**

   ```bash
   pip3 install -r requirements.txt
   ```

   This command will install all the required dependencies for the DAS Toolbox within the virtual environment.

4. **Deactivate the Virtual Environment:**

   When you are done using the DAS Toolbox, you can deactivate the virtual environment:

   ```bash
   deactivate
   ```

   Your shell prompt will return to its normal state.

## Deployment Options

Before delving into usage, it's crucial to comprehend the two distinct deployment options available with DAS: LOCAL AND REMOTE (OPENFAAS).

The concept of a local DAS is tailored for users to execute queries, add atoms, and perform various actions within their local environment. In contrast, the remote DAS comes into play when accessing a remote machine running OpenFaaS.

It's imperative to highlight that a simultaneous connection to a RedisMongo and remote access is not supported. In other words, if a user's DAS is configured to use a RedisMongo-type atomDb, this DAS cannot establish remote connections.

Regarding performance, the remote DAS is expected to outperform for larger queries since processing occurs on a dedicated machine with substantial computing power. In contrast, the local DAS's performance relies on the user's machine. In the case of OpenFaaS, which is executed here through the CLI, it runs on your local machine. Therefore, response time is also contingent on your machine's capability. However, with functions running locally, there's no need to install Hyperon on your machine or update Python if using an unsupported version. Additionally, you can easily switch between different function versions.

## Usage

```bash
python3 main.py <command> <subcommand> [options]
```

- `config list`: Display the current configuration settings.
- `config set` : Set Redis and MongoDB configuration settings.
- `server start`: Start Redis and MongoDB containers.
- `server stop`: Stop and remove all currently running services.
- `faas start`: Start an OpenFaaS service.
- `faas stop`: Stop the running OpenFaaS service.
- `metta load`: Load Metta file(s) into the Canonical Load service.
- `metta validate`: Validate the syntax of a Metta file or directory.

## Local Distributed Atom Space

These steps provide a detailed guide on how to run the Distributed Atom Space, ensuring a smooth deployment process for local use.

Follow these steps to deploy DAS locally:

```bash
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

# Modify the examples/distributed_atom_space_remote.py file with the credentials added through the configuration command (MongoDB port, username, password, etc.).
python3 examples/distributed_atom_space_local.py
```

## Distributed Atom Space with OpenFaaS

These steps guide you through the process of deploying a Distributed Atom Space with OpenFaaS, ensuring a seamless setup for distributed computing using OpenFaaS functions.

Follow these steps to deploy DAS with OpenFaaS:

```bash
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

# Modify the examples/distributed_atom_space_remote.py file with the port openFaaS is running (default 8080).
python3 examples/distributed_atom_space_remote.py
```

## Getting Help

To view help information for any command or subcommand, you can use the `--help` option. This option provides detailed information about the usage, options, and arguments associated with the specified command.

### Examples

```bash
# View help for the main script
python3 das-cli.py --help

# View help for a specific command (e.g., server)
python3 das-cli.py server --help

# View help for a specific subcommand (e.g., start within the server command)
python3 das-cli.py server start --help

# View help for the OpenFaaS start command
python3 das-cli.py faas start --help
```

The `--help` option is a powerful tool to understand how to use each command effectively. Use it at any level in the command hierarchy to access relevant documentation and ensure correct command execution.

## Troubleshooting

If you encounter errors or issues when running Docker commands, follow these steps to troubleshoot common problems.

### Docker Permission Denied

If you receive a permission error when executing Docker commands, make sure that your user is in the `docker` group. Run the following command to add your user to the group:

```bash
sudo usermod -aG docker $USER
```

After adding your user to the `docker` group, it is necessary to start a new bash session for the changes to take effect.

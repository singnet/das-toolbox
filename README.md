# DAS Toolbox

## Overview

This CLI provides a set of commands to manage containerized services, OpenFaaS functions, and Metta operations. It includes functionalities to start and stop server services, manage OpenFaaS functions, load Metta files, and validate Metta file syntax.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Server Commands](#server-commands)
  - [OpenFaaS Commands](#openfaas-commands)
  - [Metta Commands](#metta-commands)
  - [Examples](#examples)
- [Configuration](#configuration)
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

## Usage

```bash
python3 main.py <command> <subcommand> [options]
```

### Server Commands

- `start`: Start required services (Redis and MongoDB).
- `stop`: Stop all currently running services.

### OpenFaaS Commands

- `start`: Start an OpenFaaS service.
- `stop`: Stop the running OpenFaaS service.

### Metta Commands

- `load`: Load Metta file(s) into the Canonical Load service.
- `validate`: Validate the syntax of a Metta file or directory.

### Examples

Here are some examples demonstrating the usage of the DAS Toolbox CLI:

```bash
# Set the configuration file
python3 main.py config set

# Start server services
python3 main.py server start

# Validate a Metta file or directory
python3 main.py metta validate --filepath $PWD/examples/data/

# Load Metta files
python3 main.py metta load --path $PWD/examples/data/animals.metta

# Start an OpenFaaS service
python3 main.py faas start --function queryengine --version 1.9.2
```

Additionally, you can install Hyperon-DAS using `pip3 install hyperon-das`. After that, modify the `examples/distributed_atom_space_local.py` file with the credentials added through the configuration command (MongoDB port, username, password, etc.). Run the following command to execute the example:

```bash
python3 examples/distributed_atom_space_local.py
```

This will provide output based on the data loaded using the `metta load` command with the local distributed atom space.

To test using the OpenFaaS function, adjust the port to match the OpenFaaS service and, after saving, run the following command:

```bash
python3 examples/distributed_atom_space_remote.py
```

The output should be similar to the previous command, showcasing the distributed atom space remotely.

## Configuration

Before using the CLI, make sure to initialize the configuration file:

```bash
python3 main.py config set
```

## Getting Help

To view help information for any command or subcommand, you can use the `--help` option. This option provides detailed information about the usage, options, and arguments associated with the specified command.

### Examples

```bash
# View help for the main script
python3 main.py --help

# View help for a specific command (e.g., server)
python3 main.py server --help

# View help for a specific subcommand (e.g., start within the server command)
python3 main.py server start --help

# View help for the OpenFaaS start command
python3 main.py faas start --help
```

The `--help` option is a powerful tool to understand how to use each command effectively. Use it at any level in the command hierarchy to access relevant documentation and ensure correct command execution.

## Troubleshooting

If you encounter errors or issues when running Docker commands, follow these steps to troubleshoot common problems.

### Docker Permission Denied

If you receive a permission error when executing Docker commands, make sure that your user is in the `docker` group. Run the following command to add your user to the group:

```bash
sudo usermod -aG docker $USER
```

After adding your user to the `docker` group, it is necessary to restart your computer for the changes to take effect.

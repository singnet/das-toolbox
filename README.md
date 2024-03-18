# DAS Toolbox

## Overview

This CLI provides a set of commands to manage containerized services, OpenFaaS functions, and Metta operations. It includes functionalities to start and stop server services, manage OpenFaaS functions, load Metta files, and validate Metta file syntax.

## Table of Contents

- [Overview](#overview)
- [Table of Contents](#table-of-contents)
- [Prerequisites](#prerequisites)
- [Installation](#installation)

  - [Installation via Repository](#installation-via-repository)
  - [Installation via Binary](#installation-via-binary)
  - [Installation via APT](#installation-via-apt)

- [Usage](#usage)

  - [DAS Deployment Options](#das-deployment-options)
  - [Synopsis](#synopsis)

- [Examples](#examples)

  - [Local Distributed Atom Space](#local-distributed-atom-space)
  - [Distributed Atom Space with OpenFaaS](#distributed-atom-space-with-openfaas)

- [Getting Help](#getting-help)
- [Troubleshooting](#troubleshooting)
  - [Docker Permission Denied](#docker-permission-denied)

## Prerequisites

Before using the DAS Toolbox, make sure you have the following prerequisites installed:

- Docker

## Installation

### Installation via Repository

To install the DAS Toolbox from the source code, you require the following prerequisites, in addition to those outlined in the Prerequisites section:

- Python 3.8.x
- Virtualenv (optional but recommended)
- Pip (Python package installer)

You can follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/singnet/das-toolbox.git
```

2. To ensure a clean and isolated environment for running the DAS Toolbox, it is recommended to use a virtual environment. This command will create a virtual environment named `env` in the current directory.:

```bash
python3 -m venv env
```

3. Now you need to activate the virtual environment. After activation, your shell prompt should change to indicate that you are now working within the virtual environment.

```bash
source env/bin/activate
```

4. Navigate to the source code directory:

```bash
cd das-toolbox/src
```

5. This command will install all the required dependencies for the DAS Toolbox within the virtual environment.:

```bash
pip3 install -r requirements.txt
```

6. Run the `das_cli.py` file directly:

```bash
python3 das_cli.py --help
```

7. When you've finished using the DAS Toolbox, you can deactivate the virtual environment, and your shell prompt will revert to its usual state. To activate the virtual environment again, simply execute the command from the third step.

```bash
deactivate
```

### Installation via Binary

You can also download the `das-cli` binary available in the [releases](https://github.com/singnet/das-toolbox/releases) of GitHub.

### Installation via APT

If you prefer, you can install the `das-cli` package through apt:

1. If this is your first time installing the DAS Toolbox on your computer, you'll need to set up our repository by executing the following command:

```bash
sudo bash -c "wget -O - http://45.77.4.33/apt-repo/setup.sh | bash"
```

2. Once you've completed that step, you can proceed to install the das-cli package:

```bash
sudo apt install das-cli
```

3. This will install the DAS CLI package, allowing you to start using the DAS Toolbox's command-line interface

```bash
das-cli --help
```

## Usage

### DAS Deployment Options

Before delving into usage, it's crucial to comprehend the two distinct deployment options available: LOCAL and REMOTE.

**LOCAL** deployment will setup the database backend required to to use a redis_mongo DAS locally, i.e. a DAS instantiated like this:

```
das = DistributedAtomSpace(query_engine='local', atomdb='redis_mongo', ... )
```

Both databases (Redis and MongoDB) will be set up in docker containers with (configurable) exposed ports. This deployment is supposed to be used by one single client locally, i.e. there's no concurrency management other than the ones provided by each DBMS and no DAS cache optimization will take place.

LOCAL deployment is meant for Python applications which uses DAS running in the same machine with a knowledge base which is large enough to not fit entirely in RAM but small enough to fit in one single machine. Once deployed, the user can either load a knowledge base (see instructions below) or use DAS api to populate it.

If you want to access a DAS from a remote machine, you need to deploy the REMOTE version of DAS.

**FAAS** deployment will setup an OpenFaaS server to answer connection requests as well as the database backend. A REMOTE deployment can be connected using a DAS instantiated like this:

```
das = DistributedAtomSpace(query_engine='remote', host=<host>, port=<port>, ...)
```

FAAS deployment is meant for creation of a DAS knowledge base which is supposed to be used concurrently by several clients in different remote machines.

### Synopsis

The commands outlined below should be executed within the "src" directory if you're running the code directly from its source using Python. Alternatively, if you're utilizing the package available from apt, you can simply run `das-cli` instead of python3 `das_cli.py`.

```bash
python3 das_cli.py <command> <subcommand> [options]
```

- `example local`: Echo commands for local setup.
- `example faas`: Echo commands for OpenFaaS setup.
- `config list`: Display the current configuration settings.
- `config set` : Set Redis and MongoDB configuration settings.
- `server start`: Start Redis and MongoDB containers.
- `server stop`: Stop and remove Redis and MongoDB containers.
- `faas start`: Start an OpenFaaS service inside a docker container.
- `faas stop`: Stop and remove the OpenFaaS container.
- `metta load`: Load a MeTTa file into the databases
- `metta validate`: Validate the syntax of a Metta file or directory.
- `logs redis`: Display Docker container log for Redis
- `logs mongodb`: Display Docker container log for MongoDB.
- `logs faas`: Display Docker container log for OpenFaas.

NB `server start` and `faas start` store information about containers in `~/.das/` so you should avoid remove containers by calling `docker` directly. You're supposed to use `server stop` and `faas stop`.

## Examples

### Local Distributed Atom Space

These steps provide a detailed guide on how to run the Distributed Atom Space, ensuring a smooth deployment process for local use.

Follow these steps to deploy DAS locally:

```bash
# Install Hyperon-DAS:
pip3 install hyperon-das

# Set the configuration file
python3 das_cli.py config set

# Start server services
python3 das_cli.py server start

# Validate a Metta file (absolute path to a single file)
python3 das_cli.py metta validate --path $PWD/examples/data/animals.metta

# Load a Metta file (absolute path to a single file)
python3 das_cli.py metta load --path $PWD/examples/data/animals.metta

# Modify the examples/distributed_atom_space_remote.py file with the credentials added through the configuration command (MongoDB port, username, password, etc.).
python3 examples/distributed_atom_space_local.py
```

### Distributed Atom Space with OpenFaaS

These steps guide you through the process of deploying a Distributed Atom Space with OpenFaaS, ensuring a seamless setup for distributed computing using OpenFaaS functions.

Follow these steps to deploy DAS with OpenFaaS:

```bash
# Set the configuration file
python3 das_cli.py config set

# Start server services
python3 das_cli.py server start

# Validate a Metta file (absolute path to a single file)
python3 das_cli.py metta validate --path $PWD/examples/data/animals.metta

# Load a Metta file (absolute path to a single file)
python3 das_cli.py metta load --path $PWD/examples/data/animals.metta

# Start OpenFaaS Service
python3 das_cli.py faas start --function queryengine --version 1.9.2

# Modify the examples/distributed_atom_space_remote.py file with the port openFaaS is running (default 8080).
python3 examples/distributed_atom_space_remote.py
```

## Getting Help

To view help information for any command or subcommand, you can use the `--help` option. This option provides detailed information about the usage, options, and arguments associated with the specified command.

```bash
# View help for the main script
python3 das_cli.py --help

# View help for a specific command (e.g., server)
python3 das_cli.py server --help

# View help for a specific subcommand (e.g., start within the server command)
python3 das_cli.py server start --help

# View help for the OpenFaaS start command
python3 das_cli.py faas start --help
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

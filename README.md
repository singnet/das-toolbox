# DAS Toolbox

## Overview

This CLI provides a set of commands to manage containerized services, OpenFaaS functions, and Metta operations. It includes functionalities to start and stop db services, manage OpenFaaS functions, load Metta files, and validate Metta file syntax.

## Table of Contents

- [DAS Toolbox](#das-toolbox)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Installation via APT](#installation-via-apt)
    - [Installation via Repository](#installation-via-repository)
    - [Installation via Binary](#installation-via-binary)
  - [Usage](#usage)
    - [DAS Deployment Options](#das-deployment-options)
    - [Synopsis](#synopsis)
  - [Examples](#examples)
  - [Getting Help](#getting-help)
  - [Integration Tests](#integration-tests)
  - [Troubleshooting](#troubleshooting)
    - [Docker Permission Denied](#docker-permission-denied)
    - [Temporary Directory Creation Error](#temporary-directory-creation-error)

## Prerequisites

Before using the DAS Toolbox, make sure you have the following prerequisites installed:

- Docker

## Installation

### Installation via APT

You can install the `das-cli` package through apt:

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

### Installation via Repository

To install the DAS Toolbox from the source code, you require the following prerequisites, in addition to those outlined in the Prerequisites section:

- Python 3.10.x
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

## Usage

### DAS Deployment Options

Before delving into usage, it's crucial to comprehend the two distinct deployment options available: LOCAL and REMOTE.

**LOCAL** deployment will setup the database backend required to use a redis_mongo DAS locally, i.e. a DAS instantiated like this:

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

The commands outlined below should be executed within the "src" directory if you're running the code directly from its source using Python. Alternatively, if you're utilizing the package available from apt, you can simply run `das-cli` instead of `python3 das_cli.py`.

```bash
python3 das_cli.py <command> <subcommand> [options]
```

- `--help`: Package help (global flag).
- `--version`: Package Version (global flag).
- `update-version`: Update Package Version.
- `example local`: Echo commands for local setup.
- `example faas`: Echo commands for OpenFaaS setup.
- `config list`: Display the current configuration settings.
- `config set` : Set Redis and MongoDB configuration settings.
- `db start`: Start Redis and MongoDB containers.
- `db stop`: Stop and remove Redis and MongoDB containers.
- `db restart`: Restart Redis and MongoDB containers.
- `db count-atoms`: Display the total Atoms within the databases.
- `faas start`: Start an OpenFaaS service inside a docker container.
- `faas stop`: Stop and remove the OpenFaaS container.
- `faas restart`: Restart OpenFaaS container.
- `faas update-version`: Update an OpenFaaS service to a newer version.
- `faas version`: Get OpenFaaS function version.
- `metta load`: Load a MeTTa file into the databases
- `metta check`: Check the syntax of a Metta file or directory.
- `logs redis`: Display Docker container log for Redis
- `logs mongodb`: Display Docker container log for MongoDB.
- `logs faas`: Display Docker container log for OpenFaas.
- `logs das`: Display logs for das.
- `jupyter-notebook start`: Start a Jupyter Notebook.
- `jupyter-notebook restart`: Restart Jupyter Notebook.
- `jupyter-notebook stop`: Stop a Jupyter Notebook.
- `python-library list`: List all major/minor versions of hyperon-das and hyperon-das-atomdb.
- `python-library set`: Allow setting specific versions for both hyperon-das and hyperon-das-atomdb libraries
- `python-library version`: Show currently installed and newest available versions of both, hyperon-das and hyperon-das-atomdb
- `python-library update`: Update both hyperon-das and hyperon-das-atomdb to the newest available version.
- `release-notes`: List available release notes versions.
- `dbms-adapter das-peer start`: Start a DAS peer container as a server for Atoms collection and storage.
- `dbms-adapter das-peer stop`: Stop and remove a DAS peer container.
- `dbms-adapter das-peer restart`: Restart a DAS peer container.
- `dbms-adapter dbms-peer run`: Start a DBMS peer client with specified database and context that connects to the DAS peer server.

## Examples

These steps provide a detailed guide on how to run the Distributed Atom Space, ensuring a smooth deployment process.

Follow these steps:

```bash
# Install Hyperon-DAS:
pip3 install hyperon-das

# Set the configuration file
python3 das_cli.py config set

# Start db services
python3 das_cli.py db start

# Check a Metta file (absolute path to a single file)
python3 das_cli.py metta check $PWD/examples/data/animals.metta

# Load a Metta file (absolute path to a single file)
python3 das_cli.py metta load $PWD/examples/data/animals.metta

# Start OpenFaaS Service
python3 das_cli.py faas start

# Start DAS peer server service
python3 das_cli.py dbms_adapter das_peer start

# Start DBMS peer client
python3 das_cli.py dbms_adapter dbms_peer run --client-hostname example.io --client-port 1234 --client-database myDatabase --client-username John --context $(pwd)/context.txt
```

## Getting Help

To view help information for any command or subcommand, you can use the `--help` option. This option provides detailed information about the usage, options, and arguments associated with the specified command.

```bash
# View help for the main script
python3 das_cli.py --help

# View help for a specific subcommand (e.g., start within the db command)
python3 das_cli.py db start --help

# View help for the OpenFaaS start command
python3 das_cli.py faas start --help
```

The `--help` option is a powerful tool to understand how to use each command effectively. Use it at any level in the command hierarchy to access relevant documentation and ensure correct command execution.

For users who install the deb package, a man page is available for additional reference. You can access it using the man command. This provides comprehensive documentation, including usage examples, descriptions of options, and more.

```bash
# View help for the main command
man das-cli

# View help for a specific subcommand (e.g., start within the db command)
man das-cli-db-start

# View help for the OpenFaaS start command
man das-cli-faas-start
```

## Integration Tests

To execute the integration tests, use the following commands:

1. **Without Cluster Tests:**

   ```bash
   make integration_tests
   ```

   This command runs all integration tests, excluding those that require a configured Redis cluster.

2. **With Cluster Tests:**

   ```bash
   DAS_CLI_TEST_CLUSTER=true make integration_tests
   ```

   Make sure you have configured the `tests/integration/fixtures/config/redis_cluster.json` file. Replace the `username` and `ip` for the cluster nodes. For the first node, you don't need to replace the `username` as it will automatically use the current server's user where the tests are running with `das-cli`. Do not change the `context` as it will be created during test execution.

## Troubleshooting

If you encounter errors or issues when running Docker commands, follow these steps to troubleshoot common problems.

### Docker Permission Denied

If you receive a permission error when executing Docker commands, make sure that your user is in the `docker` group. Run the following command to add your user to the group:

```bash
sudo usermod -aG docker $USER
```

After adding your user to the `docker` group, it is necessary to start a new bash session for the changes to take effect.

### Temporary Directory Creation Error

This error occurs because the `das-cli` executable includes a compressed support file that is unpacked into a temporary directory during execution. When the storage is full, the extraction process fails.

#### Solution

1. **Check the disk space**:

   - Run the `df -h` command in the terminal to check the available space.

2. **Free up disk space**:

   - Delete unnecessary files or move them to external storage to free up space on your disk.

With sufficient free space, you should be able to execute the commands as expected.

# DAS Toolbox

## Overview

**DAS Toolbox** is a CLI tool that simplifies the management of containerized services, OpenFaaS functions, and operations related to the Distributed Atomspace (DAS). It allows you to spin up databases, load MeTTa files, validate syntax, and more.

---

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)

  * [APT Package](#apt-package)
  * [From Source](#from-source)
  * [Binary Release](#binary-release)
* [Usage](#usage)

  * [Deployment Modes](#deployment-modes)
  * [General Syntax](#general-syntax)
* [Examples](#examples)
* [Help](#help)
* [Integration Tests](#integration-tests)
* [Troubleshooting](#troubleshooting)

---

## Requirements

* [Docker](https://www.docker.com/)
* For source installation:

  * Python 3.10.x
  * `virtualenv` (recommended)
  * `pip`

---

## Installation

### APT Package

1. Set up the repository:

  ```bash
  sudo bash -c "wget -O - http://45.77.4.33/apt-repo/setup.sh | bash"
  ```

2. Install the package:

  ```bash
  sudo apt install das-cli
  ```

3. Check installation:

  ```bash
  das-cli --help
  ```

---

### From Source

1. Clone the repository:

  ```bash
  git clone --recurse-submodules https://github.com/singnet/das-toolbox.git
  cd das-toolbox
  ```

2. (Recommended) Create and activate a virtual environment:

  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

3. Install dependencies:

  ```bash
  cd das-cli/src
  pip3 install -r requirements.txt
  ```

4. Run:

  ```bash
  python3 das_cli.py --help
  ```

---

### Binary Release

Download the latest precompiled binary from the [releases page](https://github.com/singnet/das-toolbox/releases).

---

## Usage

### Deployment Modes

#### LOCAL

Spins up Redis and MongoDB via Docker:

```python
das = DistributedAtomSpace(query_engine='local', atomdb='redis_mongo')
```

Recommended for local development and testing with moderate knowledge base sizes.

#### FAAS (REMOTE)

Spins up Redis, MongoDB, and a remote OpenFaaS query engine:

```python
das = DistributedAtomSpace(query_engine='remote', host=<host>, port=<port>)
```

Best suited for distributed environments with multiple clients.

---

### General Syntax

From source:

```bash
python3 das_cli.py <command> <subcommand> [options]
```

Or, if installed via APT:

```bash
das-cli <command> <subcommand> [options]
```

---

## Examples

```bash
# Install DAS Python package
pip3 install hyperon-das

# Configure Redis/Mongo
das-cli config set

# Start databases
das-cli db start

# Validate and load MeTTa file
das-cli metta check ./examples/data/animals.metta
das-cli metta load ./examples/data/animals.metta

# Start OpenFaaS
das-cli faas start

# Start DAS and DBMS peers
das-cli dbms-adapter das-peer start
das-cli dbms-adapter dbms-peer run \
  --client-hostname example.io \
  --client-port 1234 \
  --client-database myDatabase \
  --client-username John \
  --context $(pwd)/context.txt
```
---

## Help

You don't need to memorize all commands. DAS CLI offers a structured help system that lets you explore everything interactively.

### List All Command Groups

```bash
das-cli --help
```

This will show the main command categories such as `db`, `faas`, `metta`, `logs`, etc.

### View Help for a Command Group

To see the available subcommands within a group:

```bash
das-cli <command-group> --help
```

Example:

```bash
das-cli db --help
```

### Get Help for a Specific Subcommand

To understand how to use a specific command:

```bash
das-cli <command-group> <subcommand> --help
```

Example:

```bash
das-cli faas update-version --help
```

### Manual Pages (APT install only)

If you installed `das-cli` via the APT package, you can also view man pages:

```bash
man das-cli
man das-cli-faas-start
man das-cli-db-restart
```

> Man pages provide detailed documentation, flags, examples, and usage tips.

---

## Integration Tests

If you forgot `--recurse-submodules`, run:

```bash
git submodule update --init --recursive
```

### Without cluster tests:

```bash
make integration_tests
```

### With cluster tests:

```bash
DAS_CLI_TEST_CLUSTER=true make integration_tests
```

Make sure you have configured the `tests/integration/fixtures/config/redis_cluster.json` file. Replace the `username` and `ip` for the cluster nodes. For the first node, you don't need to replace the `username` as it will automatically use the current server's user where the tests are running with `das-cli`. Do not change the `context` as it will be created during test execution.

## Troubleshooting

### Docker permission denied

Add your user to the Docker group:

```bash
sudo usermod -aG docker $USER
# Restart your terminal session
```

### Temporary folder error

Ensure at least **32MB of free disk space**. DAS Toolbox extracts files to temporary folders during execution.

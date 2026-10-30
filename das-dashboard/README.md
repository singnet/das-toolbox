# DAS Dashboard

The Distributed Atomspace Dashboard is a web interface for configuring, operating, and monitoring a DAS environment. It is, basically, a wrapper around [das-cli](../das-cli/README.md): every start, stop, configuration, and query action runs `das-cli` underneath.

## Table of Contents

* [Screens](#screens)
* [Prerequisites](#prerequisites)
* [SSH access](#ssh-access)
* [Starting the interface](#starting-the-interface)
* [Using the dashboard](#using-the-dashboard)
  * [1. Profile](#1-profile)
  * [2. Configuration](#2-configuration)
  * [3. Dashboard](#3-dashboard)
  * [4. Query](#4-query)
  * [5. Common errors & troubleshooting](#5-common-errors--troubleshooting)

## Screens

The top bar has four pages.

| Page | Path | What it is for |
|---|---|---|
| Profile | `/profiles` | SSH username and private key used for every remote operation |
| Configuration | `/configuration` | AtomDB, agents, brokers, and their parameters |
| Dashboard | `/dashboard` | Machines discovered from the saved configuration, service status, and runtime metrics |
| Query | `/query` | Compose and run a query, then inspect the answers |

## Prerequisites

Install **das-cli** before starting the dashboard. The same version must be installed on the machine that runs the dashboard and on every machine that will take part in the architecture.

The dashboard container uses the binary at `/usr/bin/das-cli`. Install with the APT repository or a local `.deb` package, as described in the [das-cli installation](../das-cli/README.md#installation). A `pip install` inside a virtualenv does not put the binary on that path.

Docker must be installed on the dashboard machine and on every machine where `das-cli` will start a container. The SSH user configured below must be allowed to use Docker on each of those machines (typically by being in the `docker` group).

## SSH access

The Profile page stores one username and one private key. The dashboard uses that key for SCP, remote `das-cli` commands, and the Docker contexts that start databases on other machines. The matching **public** key has to be in `authorized_keys` for that user on every machine in the architecture.

Create a key pair on the machine where you will open the dashboard:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/das-dashboard -N ""
```

`~/.ssh/das-dashboard` is the private key you will upload on the **Profile** page. `~/.ssh/das-dashboard.pub` is the public key.

On each machine, as the user who will run `das-cli` (the same username you will type in Profile; `root` is not accepted, das-cli will block any operations on root user.):

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
# paste the contents of das-dashboard.pub, then press Ctrl-D
chmod 600 ~/.ssh/authorized_keys
```

Confirm the key works before using the dashboard:

```bash
ssh -i ~/.ssh/das-dashboard <username>@<host> das-cli --version
```

## Starting the interface

From `das-dashboard/`:

```bash
./scripts/start_interface.sh
```

The script builds the frontend and backend images and starts both containers on the host network.

| Service | URL |
|---|---|
| Dashboard | http://localhost:5173 |
| Backend | http://localhost:8000 |
| Backend API docs | http://localhost:8000/docs |

Override the ports with the following variables: `FRONT_PORT` and `BACK_PORT`.
Example: ` FRONT_PORT=4000 BACK_PORT=5000 ./scripts/start_interface `

## Using the dashboard

### 1. Profile

Open **Profile** and set:

* **Username.** The SSH account on the remote machines. It must be at least 3 characters and cannot be `root`.
* **SSH Key File.** The private key created above (`~/.ssh/das-dashboard`), not the `.pub` file.

Save the profile before configuring anything that has to reach another machine.

### 2. Configuration

Open **Configuration**.

This page edits the DAS configuration: AtomDB, agents (Query Agent, Link Creation Agent, and the others), brokers, and the parameters of each component. If you already have a `config.json`, use **Load** and select that file.

**Save** writes the file on the dashboard machine and runs `das-cli config set --file` there. When the configuration names other machines, the same file is copied to each of them and `das-cli config set --file` runs on those machines as well. That step registers the Docker contexts the CLI uses to start containers remotely.

### 3. Dashboard

Open **Dashboard**.

The page reads the saved configuration and lists the machines it defines. From here you can start and stop the databases and the agents, and follow whether each service is up. The page also shows runtime metrics for those machines.

Start the databases before the agents, the same order used with `das-cli db start` and then `das-cli query start`.

### 4. Query

Open **Query** after the Query Agent and the Attention Broker are running.

Type the query, turn on **Use MeTTa query** when the text is MeTTa, adjust the parameters in the side panel, and run it. The answers come back on the same page.

### 5. Common errors & troubleshooting:

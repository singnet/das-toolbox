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

Profile only sets the SSH user and the private key used to reach the machines in the architecture. Skip it when the whole DAS runs on this machine.

Enter the username, select the private key, and save. If a later step fails with an authentication error, the public key is not authorized for that user on the target machine. See [SSH access](#ssh-access).

### 2. Configuration

Configuration is where you place each DAS agent: which machine, by IP, runs which agent.

Saving generates a `config.json` and sets it as the current DAS configuration. If the file names any remote machine, the dashboard copies it there and runs `das-cli config set --file` on that machine. That copy fails with an authentication error when the SSH key from Profile is not set up on the target.

An existing configuration file can be brought in with **Load**.

### 3. Dashboard

Dashboard is where you operate the DAS and watch it. Opening the page loads the saved configuration and connects to every machine listed in it.

Two views:

* **Servers.** One server at a time, and the agents running on it. The table on this view can stop or restart an agent on that machine. **Metrics collection** records finer-grained performance data for those agents.
* **Agents.** Everything in one list: the databases and the agents across all machines in this DAS.

Three actions apply to the whole architecture:

* **Start AtomDB.** Starts the AtomDB. When it is configured on another machine, the container is started there.
* **Start Architecture.** Choose which parts of the architecture to start. Each one starts on the machine it was assigned to in Configuration.
* **Load Metta Database.** Loads a MeTTa file into the AtomDB. When that database is on another machine, the file is copied there and then loaded.

### 4. Query

Query runs a query from the browser and shows the result as it arrives. The query can be written in MeTTa or in the default syntax. The page updates live, including charts for answer importance and for how many answers arrive per second.

Query parameters are edited on the same page: answer limits and the other parameters of the query.

**Pre-requisites:** The page needs a running architecture with at least an Attention Broker, a Query Agent, and a Command Router, and a database that already has data loaded.

### 5. Common errors & troubleshooting:

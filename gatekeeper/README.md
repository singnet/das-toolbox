# Gatekeeper

**Gatekeeper** is a complete system for managing reserved network ports and registered instances in a distributed infrastructure. It consists of the following core components:

* A **REST API** that centralizes data about ports and instances.
* A **CLI** to register instances and manage port allocation.
* A lightweight **SQLite** database for local and efficient data persistence.
* An **Agent** that runs periodically to scan active ports on each registered instance.

---

## Overview

Each machine (instance) can register itself through the CLI and interact with the API to:

* Reserve available ports.
* Release unused ports.
* View the port usage history.
* List all registered instances.

In addition, the system includes an **Agent** that automatically monitors the local environment and keeps the system in sync.

---

## Components

### API

The central service that stores and exposes data about:

* Registered instances
* Reserved ports and their status
* Port usage history

### CLI

A command-line interface (`gkctl`) that allows users to:

* Register a new instance (`join`)
* Reserve or release ports
* View historical and real-time port data
* List known instances

### Agent

A lightweight background process that runs **every 5 minutes** on each instance to:

* Detect new ports being listened on
* Identify ports that are no longer in use
* Sync this data with the API in real time

This ensures the API always reflects the actual state of each machine without requiring user input.

### SQLite Database

A local, file-based relational database used by the API to store:

* Instance metadata (hardware details, hostnames, etc.)
* Port allocations and historical bindings
* Activity timestamps for audits and analysis

---

## Getting Started

### 1. Start the API (Server)

```bash
python3 api/src/main.py
```

The server will be available at `http://localhost:5000`.

### 2. Use the CLI

Example commands:

```bash
# Register the current machine
python cli/src/gkctl.py instance join

# List registered instances
python cli/src/gkctl.py instance list

# Reserve a new available port
python cli/src/gkctl.py port reserve

# Release a port that is no longer in use
python cli/src/gkctl.py port release --port 8080

# View the port usage history
python cli/src/gkctl.py port history
```

To see full CLI options:

```bash
python cli/src/gkctl.py --help
```

---

## How It Works

### CLI ↔ API Communication

The CLI communicates with the API to perform all operations related to instance and port management.

### Agent Monitoring

The agent runs automatically every **5 minutes**, scanning the system for port usage changes and reporting back to the API:

* Detects **new ports** that start being listened on.
* Detects **ports that stopped** being listened on.
* Keeps the database synchronized with real-time activity on each instance.

---

## 📌 Requirements

* Python 3.10+
* Linux (for port detection using `psutil`)

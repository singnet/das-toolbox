# DAS UI for Configuration & Setup

The DAS UI is a simple and intuitive web interface designed to simplify the configuration, deployment, and monitoring of DAS environments through a visual workflow.

## Requirements

* Node.js **22.0.0 or later**

You can verify your installed Node.js version with:

```bash
node -v
```

If your version is below 22, we recommend installing the latest LTS release:

```bash
nvm install node --lts
```

Make sure that NVM is installed on your system. If it is not, follow the installation instructions available in the NVM repository.

## Prerequisites

Before using the dashboard, ensure that:

* You are running the latest version of **das-cli**.
* All machines that will participate in the DAS architecture are running the latest version of **das-cli**.
* All machines in the architecture have a shared SSH key configured and properly authorized.

## Starting the Interface

Run the following script:

```bash
./scripts/start_interface.sh
```

## Recommended Usage Flow

### 1. Create an SSH Profile

Navigate to the **Profile** page and configure an SSH profile.

A profile consists of:

* **Username**
* **SSH Private Key** (used for all remote operations performed by the dashboard)

### 2. Configure DAS Services

Navigate to the **Configuration** page.

This page allows you to define the settings, parameters, and deployment options for all Distributed AtomSpace components, including:

* AtomDB
* Agents (such as Query Agents and Link Creation Agents)
* Brokers
* Component-specific configuration parameters

If you already have a DAS configuration file, you can import it by clicking **Load** and selecting a valid configuration JSON file.

### 3. Save Your Configuration

After customizing the configuration according to your environment, click **Save** to persist the settings.

### 4. Open the Dashboard

Navigate to the **Dashboard** page.

The dashboard automatically loads the previously saved configuration and discovers the configured machines based on the architecture definition.

Once loaded, the dashboard will:

* Connect to each configured machine.
* Collect and display runtime metrics.
* Monitor the status of deployed services.
* Provide visibility into resource utilization across the architecture.

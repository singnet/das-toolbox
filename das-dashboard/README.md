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
    * [Keeping the defaults](#keeping-the-defaults)
    * [Changing a few values](#changing-a-few-values)
    * [Running the DAS on more than one machine](#running-the-das-on-more-than-one-machine)
    * [Running Redis or MongoDB as a cluster](#running-redis-or-mongodb-as-a-cluster)
    * [Using another AtomDB](#using-another-atomdb)
    * [Loading a configuration you already have](#loading-a-configuration-you-already-have)
    * [Checking before you save](#checking-before-you-save)
    * [Starting over](#starting-over)
  * [3. Dashboard](#3-dashboard)
  * [4. Query](#4-query)
  * [5. Common errors & troubleshooting](#5-common-errors--troubleshooting)
* [Reference](#reference)
  * [Profile page](#profile-page)
  * [Configuration page](#configuration-page)
    * [Page actions](#page-actions)
    * [Addresses](#addresses)
    * [AtomDB section](#atomdb-section)
    * [Agents section](#agents-section)
    * [Environment section](#environment-section)

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

On each machine, log in as the same username you will type on the Profile page. That account must not be `root`. See [Profile](#1-profile).

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
Example: `FRONT_PORT=4000 BACK_PORT=5000 ./scripts/start_interface.sh`

## Using the dashboard

A first run goes in this order: save your SSH profile, save a configuration, start the DAS on the Dashboard page, and run queries on the Query page.

If the whole DAS runs on this machine with the default values, skip Profile. Open Configuration and click **Save**.

### 1. Profile

![SSH Profile page](docs/static/profile.png)

Do this first when the DAS will use more than one machine. The dashboard reaches every other machine with this user and key.

1. Create the key pair and authorize it on every machine, as described in [SSH access](#ssh-access).
2. Open **Profile** and type the SSH user. It cannot be `root`.
3. Click **Select SSH Key File** and pick the private key, the file without `.pub`.
4. Click **Save Profile**.

When you come back to change something, select the key again: the page keeps the username but not the key. If a later step fails with an authentication error, the public key is not authorized for that user on that machine.

### 2. Configuration

This page sets up the DAS environment and its agents. Changing anything here is optional: with the default values, one **Save** is enough.

The sidebar splits the configuration into **AtomDB**, **Agents**, and **Environment**. Every change follows the same steps: change the fields, click **Apply … settings** at the bottom of that section, then click **Save**. Apply alone stores nothing, and Save only stores what was applied.

#### Keeping the defaults

If the default values are enough, click **Save**. The defaults put the whole DAS on this machine. The dashboard stores the configuration and sets it as the current DAS configuration. If the file names another machine, Save also copies it there and runs `das-cli config set` on that machine. That copy needs the SSH user and key from [Profile](#1-profile).

After a successful save, the page asks **Save a local copy?**. Downloading that copy is optional. **Not now** leaves the file on the server at `/opt/web-das/.das/config.json`.

#### Changing a few values

To change a port, a parameter, or the database password:

1. Open the section in the sidebar. For an agent, open **Agents** and pick it from the list.
2. Change the fields.
3. Click **Apply … settings**. The page confirms that the settings were applied.
4. Repeat for any other section you want to change.
5. Click **Save**.

If you move to another section without clicking Apply, the edits you made there are not in the file.

#### Running the DAS on more than one machine

The addresses on this page are not only where the dashboard starts each part. The DAS reads them back, and that is how its parts find each other. The Link Creation Agent, the Evolution Agent, and the Context Broker look for the Query Agent at its address. The agents look for the Attention Broker at its address. The members of a database cluster reach each other at theirs.

So type addresses with that in mind. The default `0.0.0.0` only works when everything is on one machine. For anything that runs on another machine, type the IP the other machines use to reach it.

![Query Agent placed on another machine](docs/static/configuration_agents_query_agent.png)

1. Save your [Profile](#1-profile), and authorize the key on every machine.
2. Decide which machine runs each part, and note the IP each machine is reached at.
3. Open **AtomDB** and type the IP of the database machine in the endpoint fields. Click **Apply AtomDB settings**.
4. Open **Agents**. For each agent on another machine, type that machine's IP and click **Apply**. Do the Query Agent and the Attention Broker first: the other agents look for them.
5. Click **Save**. The dashboard copies the file to every machine named in it and makes it the active configuration there. The confirmation lists the machines it reached.

Then open the Dashboard page to start each part on its machine.

#### Running Redis or MongoDB as a cluster

Cluster mode is optional. Use it when Redis or MongoDB should run on several machines and work as one database.

![Redis + MongoDB with both clusters enabled](docs/static/configuration_db_redis_mongo_clusters.png)

1. Save your [Profile](#1-profile). Every member of the cluster is started over SSH with it.
2. Open **AtomDB** and choose **Redis + MongoDB**. Mork + MongoDB works too, but only MongoDB can be a cluster there.
3. Check **Redis Cluster**, **Mongo Cluster**, or both.
4. In the list that opens, fill one row per machine: the IP of the machine that will run that member, and the username saved in Profile. Click **+ Add Another Server** for each extra machine. das-cli expects at least three members.
5. Make sure the port above the list is free on all of those machines. Every member listens on it.
6. Click **Apply AtomDB settings**, then **Save**.

When the AtomDB is started, das-cli connects to each row over SSH, starts the database there, and joins the members into one cluster. The machines need to reach each other on that port.

#### Using another AtomDB

A DAS uses one AtomDB. Redis + MongoDB is the default. To use another one, choose it in **Database Type**, fill it in, and click **Apply AtomDB settings**. The new type replaces the old one. Then click **Save**.

**Mork + MongoDB.** Same steps as Redis + MongoDB, with MorkDB in place of Redis.

**In Memory.** Nothing to fill in and no database to start. Choose it, apply, and save. The atoms live only in memory, so they are gone when the process stops.

**Remote DB.** A set of peers, each with its own database. The dashboard does not start those databases: they must already be running at the addresses you type.

![Remote DB with two peers](docs/static/configuration_db_remotedb.png)

1. Click **+ Add Peer** once for each peer.
2. For each peer, choose the **Main Connection** and fill its addresses and ports.
3. Choose the **Local Persistence Type** for each peer. In Memory needs nothing else.
4. Click **Apply AtomDB settings**. A peer with an empty port is left out.

**AdapterDB.** Maps an external PostgreSQL database into atoms.

![AdapterDB connection, credentials, and context mapping](docs/static/configuration_db_adapterdb1.png)

1. Under **Adapter Connection**, set where the adapter will listen.
2. Under **Database Credentials**, type the PostgreSQL database to map.
3. Under **Context Mapping**, keep **Paste content**. Paste the mapping, or click **Load from file** and pick the `.sql` file. Click the **Save** next to Context Mapping.
4. Scroll down to **AtomDB Backend** and choose where the mapped atoms will be stored. Fill it in the same way as that AtomDB type.
5. Click **Apply AtomDB settings**, then **Save**.

![AdapterDB mapping options and backend](docs/static/configuration_db_adapterdb2.png)

Choose **Use file path** in step 3 only if the configuration will also be used outside the dashboard. Then type the path of the mapping file instead.

#### Loading a configuration you already have

1. Click **Load** and pick the `.json` file.
2. Confirm. The file replaces the configuration on this dashboard, and the form shows its values.
3. To change something, edit the section, click **Apply**, then **Save**.

Load only changes this dashboard. If the file names other machines, click **Save** after loading to copy it to them.

#### Checking before you save

Click **Preview** to see what Save will store. If a change you made is missing, go back to that section and click **Apply**.

#### Starting over

Click **Reset** and confirm. Every section goes back to the DAS defaults, and what you typed is lost. The file already saved stays as it is until you click **Save** again.

### 3. Dashboard

Dashboard is where you operate the DAS and watch it. Opening the page loads the saved configuration and connects to every machine listed in it.

Two views:

* **Servers.** One server at a time, and the agents running on it. The table on this view can stop or restart an agent on that machine. **Metrics collection** records finer-grained performance data for those agents.
* **Agents.** Everything in one list: the databases and the agents across all machines in this DAS.

Three actions apply to the whole architecture:

* **Start AtomDB.** Starts the AtomDB. When it is configured on another machine, the container is started there.
* **Start Architecture.** Choose which parts of the architecture to start. Each one starts on the machine it was assigned to in Configuration.
* **Load MeTTa Database.** Loads a MeTTa file into the AtomDB. When that database is on another machine, the file is copied there and then loaded.

### 4. Query

Query runs a query from the browser and shows the result as it arrives. The query can be written in MeTTa or in the default syntax. The page updates live, including charts for answer importance and for how many answers arrive per second.

Query parameters are edited on the same page: answer limits and the other parameters of the query.

**Pre-requisites:** The page needs a running architecture with at least an Attention Broker, a Query Agent, and a Command Router, and a database that already has data loaded.

### 5. Common errors & troubleshooting

## Reference

### Profile page

Path: `/profiles`.

| Control | What it does |
|---|---|
| SSH user | Account used on every machine. The same account that owns the `authorized_keys` entry and can run Docker and `das-cli`. |
| SSH Key File | Name of the private key chosen for this save. Stays empty until a file is selected. A key saved earlier is not shown again. |
| Select SSH Key File | Opens the file picker. Hidden folders can be revealed with Ctrl+H on Linux, or Command+Shift+. on macOS. |
| Save Profile | Stores the username and the private key. Both are required. |

Rules:

* `root` is rejected. Root is refused for security, and das-cli blocks operations run as that user.
* The username needs at least 3 characters. Allowed characters are letters, digits, `.`, `_`, and `-`.
* Saving always asks for the key file again. Reopening the page restores only the username.

Messages:

| Message | Cause |
|---|---|
| Profile saved successfully. | Username and key were stored. |
| SSH Username must have at least 3 characters and cannot contain invalid characters. | The username is shorter than 3 characters, contains another character, or is `root`. |
| SSH Key File is required. | No key file was selected. |

### Configuration page

Path: `/configuration`.

#### Page actions

| Button | What it does |
|---|---|
| Apply … settings | At the bottom of each section. Puts that section's fields into the configuration that Save will store. Shows **… settings applied**. |
| Save | Stores the applied sections at `/opt/web-das/.das/config.json` and activates it with `das-cli config set`. Copies the file over SSH to every other machine named in it and activates it there. Then offers a local copy. |
| Load | Opens a `.json` file. After confirmation, the file must have `atomdb` and `agents`. It becomes the active configuration on this dashboard and fills the form. It is not copied to other machines. |
| Preview | Shows the applied values of each section. Values not yet applied are not shown. Read only. |
| Reset | Asks for confirmation, then fills every section with the DAS defaults. The saved file is not changed until the next Save. |

#### Addresses

* `localhost`, `127.0.0.1`, and `0.0.0.0` mean this machine. Any other address is treated as another machine, and Save copies the file to it.
* The Link Creation Agent, Evolution Agent, and Context Broker read the Query Agent endpoint to connect to it.
* The services on the DAS bus read the Attention Broker endpoint.
* Each cluster row is reached as `username@ip` over SSH. A Docker context is created for it.
* A cluster row with an empty username, `root`, or `default` is saved with the Profile username.

#### AtomDB section

**Database Type**

| Option | Value in the file | What `das-cli db start` brings up |
|---|---|---|
| Redis + MongoDB | `redismongodb` | Redis and MongoDB |
| Mork + MongoDB | `morkdb` | MorkDB and MongoDB |
| In Memory | `inmemorydb` | Nothing |
| Remote DB (Multi-Peer) | `remotedb` | Nothing. The peers' databases must already be running. |
| AdapterDB | `adapterdb` | The databases of the AtomDB Backend chosen. The mapping runs with `das-cli database-adapter run`. |

**Redis + MongoDB**

| Field | Default | Notes |
|---|---|---|
| Redis Endpoint | `0.0.0.0` | |
| Redis Port | `40020` | Also the port of every Redis cluster member. |
| MongoDB Endpoint | `0.0.0.0` | |
| MongoDB Port | `40021` | Also the port of every MongoDB cluster member. |
| MongoDB Username | `admin` | |
| MongoDB Password | `admin` | |
| Mongo Cluster | Off | Opens **MongoDB Cluster Nodes**. |
| Redis Cluster | Off | Opens **Redis Cluster Nodes**. |

Each cluster list has one row per member, with **Username** and **IP Address**. **+ Add Another Server** adds a row, and the trash icon removes it. A cluster turned on with no rows is rejected on Save.

**Mork + MongoDB**

![Mork + MongoDB](docs/static/configuration_db_morkmongo.png)

| Field | Default | Notes |
|---|---|---|
| MorkDB Endpoint | `0.0.0.0` | |
| MorkDB Port | `40022` | |
| MongoDB fields | As in Redis + MongoDB | Including **Mongo Cluster**. MorkDB has no cluster option. |

**In Memory**

![In Memory AtomDB](docs/static/configuration_db_inmemory.png)

No fields.

**Remote DB (Multi-Peer)**

| Field | Default | Notes |
|---|---|---|
| + Add Peer | | Adds a peer. The list starts empty. |
| Peer UID | `peer1`, `peer2`, … | Assigned by the form. Read only. |
| Main Connection | Redis + Mongo | Or Mork + Mongo. Opens the endpoint, port, Mongo User, and Mongo Pass fields. No cluster option. |
| Local Persistence Type | In Memory | Or Redis + MongoDB, or MorkDB + MongoDB, which open the same connection fields. |
| Trash icon | | Removes the peer. |

A peer with an empty port is dropped when you apply.

**AdapterDB**

| Field | Default | Notes |
|---|---|---|
| Adapter Type | PostgreSQL | The only option. |
| Adapter Endpoint | `0.0.0.0` | Where the adapter listens. |
| Adapter Port | `40023` | |
| Database Host | `database-host` | The PostgreSQL server to map. |
| Database Port | `5432` | |
| Database Name | `admindb` | |
| Username | `admin` | |
| Password | `admin` | |
| Paste content / Use file path | Paste content | How the context mapping is given. |
| Load from file | | Paste content mode. Reads a `.sql` file into the box. |
| Context Mapping File Path | | Use file path mode. Path of the mapping file. |
| MeTTa Output Path | | Use file path mode. Where the MeTTa files are written. |
| Save (Context Mapping) | | Stores the mapping. In Paste content mode, the server picks the file path. |
| Export MeTTa on Mapping | On | Writes MeTTa files when the mapping runs. |
| Reuse MongoDB Persistence | On | Keeps the adapter's existing MongoDB. |
| Backend Type | MorkDB + MongoDB | Or In Memory, or Redis + MongoDB. Opens the fields of that type, including its cluster options. |

#### Agents section

Every agent except Base Query has **IP Address** and **Port**: where it listens, and where the others look for it. Most also have **Port range start** and **Port range end**, the ports its workers may use. All IPs default to `0.0.0.0`.

| Agent | Started with | Port | Port range |
|---|---|---|---|
| Base Query | Not started. Shared query defaults. | | |
| Query Agent | `das-cli query-agent start` | `40002` | `42000`–`42999` |
| Link Creation Agent | `das-cli link-creation-agent start` | `40003` | `43000`–`43999` |
| Evolution Agent | `das-cli evolution-agent start` | `40005` | `45000`–`45999` |
| Command Router | `das-cli command-router start` | `40008` | `48000`–`48999` |
| Attention Broker | `das-cli attention-broker start` | `40001` | None |
| Context Broker | `das-cli context-broker start` | `40006` | `46000`–`46999` |
| AtomDB Broker | `das-cli atomdb-broker start` | `40007` | `47000`–`47999` |

The Command Router also has **HTTP API endpoint**, read only and the same host as its IP, and **HTTP API port**, default `40009`.

Parameters are stored under `agents.<agent>.params` in the file.

**Base Query**

![Base Query parameters](docs/static/configuration_agents_base_parameters.png)

| Field | Key | Default |
|---|---|---|
| Max Answers | `max_answers` | `0` |
| Max Bundle Size | `max_bundle_size` | `1000` |
| Attention Update | `attention_update` | `0` |
| Attention Correlation | `attention_correlation` | `0` |
| Attention Focus Strictness | `attention_focus_strictness` | `0.0`. Slider from 0 to 1, in steps of 0.1. |
| Unique Assignment | `unique_assignment_flag` | Off |
| Use Link Template Cache | `use_link_template_cache` | Off |
| Metta Mapping | `populate_metta_mapping` | Off |
| Use Metta Tokens | `use_metta_as_query_tokens` | Off |
| Allow Incomplete Chain Path | `allow_incomplete_chain_path` | Off |

**Query Agent**

| Field | Key | Default |
|---|---|---|
| Positive Importance | `positive_importance_flag` | Off |
| Disregard Importance | `disregard_importance_flag` | Off |
| Unique Value Flag | `unique_value_flag` | Off |
| Count Flag | `count_flag` | Off |

**Link Creation Agent**

| Field | Key | Default |
|---|---|---|
| Max Answers | `max_answers` | `10` |
| Repeat Count | `repeat_count` | `1` |
| Context | `context` | `context` |
| Attention Update | `attention_update` | `0` |
| Attention Correlation | `attention_correlation` | `0` |
| Query Interval | `query_interval` | `0` |
| Query Timeout | `query_timeout` | `0` |
| Positive Importance | `positive_importance_flag` | On |
| Use MeTTa as Query Tokens | `use_metta_as_query_tokens` | Off |

**Evolution Agent**

| Field | Key | Default |
|---|---|---|
| Population Size | `population_size` | `1000` |
| Max Generations | `max_generations` | `100` |
| Elitism Rate | `elitism_rate` | `0.01` |
| Selection Rate | `selection_rate` | `0.1` |

**Context Broker**

| Field | Key | Default |
|---|---|---|
| Context Name | `context` | `context` |
| Initial Rent Rate | `initial_rent_rate` | `0.75` |
| Spread Lowerbound | `initial_spreading_rate_lowerbound` | `0.1` |
| Spread Upperbound | `initial_spreading_rate_upperbound` | `0.1` |
| Use Cache | `use_cache` | On |
| Force Cache Reset | `enforce_cache_recreation` | Off |

The Command Router, Attention Broker, and AtomDB Broker have no parameters.

#### Environment section

| Field | Default | Notes |
|---|---|---|
| Jupyter Notebook Port | `40019` | Port of the notebook started with `das-cli jupyter-notebook start`. The host stays as saved, `0.0.0.0` by default. |

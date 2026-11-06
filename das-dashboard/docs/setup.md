# Setting up the environment

Do this once, before opening the dashboard. When the whole DAS runs on one machine, steps 1 and 3 are enough. When it uses more than one machine, do step 2 as well.

## Contents

* [1. Install das-cli and Docker](#1-install-das-cli-and-docker)
* [2. Set up SSH access](#2-set-up-ssh-access)
* [3. Start the interface](#3-start-the-interface)

## 1. Install das-cli and Docker

Install **das-cli** before starting the dashboard. The same version must be installed on the machine that runs the dashboard and on every machine that will take part in the architecture.

The dashboard container uses the binary at `/usr/bin/das-cli`. Install with the APT repository or a local `.deb` package, as described in the [das-cli installation](../../das-cli/README.md#installation). A `pip install` inside a virtualenv does not put the binary on that path.

Docker must be installed on the dashboard machine and on every machine where `das-cli` will start a container. The SSH user from step 2 must be allowed to use Docker on each of those machines (typically by being in the `docker` group).

## 2. Set up SSH access

Skip this step when the whole DAS runs on this machine.

The Profile page stores one username and one private key. The dashboard uses that key for SCP, remote `das-cli` commands, and the Docker contexts that start databases on other machines. The matching **public** key has to be in `authorized_keys` for that user on every machine in the architecture.

Create a key pair on the machine where you will open the dashboard:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/das-dashboard -N ""
```

`~/.ssh/das-dashboard` is the private key you will upload on the **Profile** page. `~/.ssh/das-dashboard.pub` is the public key.

On each machine, log in as the same username you will type on the Profile page. That account must not be `root`. See [Profile](using-the-dashboard.md#1-profile).

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

## 3. Start the interface

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

Open the dashboard in the browser, then continue with [Using the dashboard](using-the-dashboard.md).

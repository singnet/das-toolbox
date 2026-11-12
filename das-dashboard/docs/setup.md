# Setting up the environment

Do this once, before opening the dashboard.

- If the whole DAS (Distributed Atomspace) runs on one machine, do steps 1 and 3.
- If it uses more than one machine, do steps 1, 2, and 3.

## Contents

- [Setting up the environment](#setting-up-the-environment)
  - [Contents](#contents)
  - [1. Install das-cli and Docker](#1-install-das-cli-and-docker)
  - [2. Set up SSH access](#2-set-up-ssh-access)
    - [Generate a key pair](#generate-a-key-pair)
    - [Authorize the public key on remote machines](#authorize-the-public-key-on-remote-machines)
    - [Test the connection](#test-the-connection)
  - [3. Start the interface](#3-start-the-interface)

## 1. Install das-cli and Docker

Install **das-cli** before starting the dashboard. The same version must be installed on the machine that runs the dashboard and on every machine that will take part in the architecture.

The dashboard container uses the binary at `/usr/bin/das-cli`. Install with the APT repository or a local `.deb` package, as described in the [das-cli installation](../../das-cli/README.md#installation). A `pip install` inside a virtualenv does not put the binary on that path.

Docker must be installed on the dashboard machine and on every machine where `das-cli` will start a container. The SSH user from step 2 must be allowed to use Docker on each of those machines (typically by being in the `docker` group).

## 2. Set up SSH access

Skip this step if all DAS components run on the same machine as the Dashboard.

The Dashboard uses SSH to access remote machines. It stores one username and one private key. The matching public key must be authorized on every remote machine, in that user's `authorized_keys` file.

### Generate a key pair

On the **Dashboard machine**, run:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/das-dashboard -N ""
```

This creates two files:

- ~/.ssh/das-dashboard: **Private key**, to upload on the Dashboard's **Profile** page.
- ~/.ssh/das-dashboard.pub: **Public key**, to install on remote machines.

### Authorize the public key on remote machines

1. On the **Dashboard machine**, display the public key:

   ```bash
   cat ~/.ssh/das-dashboard.pub
   ```

   Copy the whole output. It is one line that starts with `ssh-ed25519`.

2. On each **Remote machine**, log in as the same username you will type on the **Profile** page of the dashboard. The account must not be `root`. See [Profile](using-the-dashboard.md#2-profile).

3. On that same **Remote machine**, run the commands below. Replace `<paste the public key here>` with the line you copied, and keep the quotes:

   ```bash
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   echo "<paste the public key here>" >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

4. Repeat steps 2 and 3 on every other remote machine.

### Test the connection

On the **Dashboard machine**, run:

```bash
ssh -i ~/.ssh/das-dashboard <username>@<host> das-cli --version
```

## 3. Start the interface

On the **Dashboard machine**, run the following command in the `das-dashboard/` directory:

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
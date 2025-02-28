## GitHub Actions Runner Management

This script manages GitHub Actions self-hosted runners using Docker.

### Setup

Before running the script, you need to set up a **Python virtual environment** and install the required dependencies.

#### 1️. Clone the Repository and Set Up the Virtual Environment

```bash
git clone https://github.com/singnet/das-toolbox.git
cd das-toolbox
python3 -m venv venv
```

**Activate the Virtual Environment:**  
- **Linux/macOS:**  
  ```bash
  source venv/bin/activate
  ```

#### 2️. Navigate to `das-runner-manager` and Install Dependencies

```bash
cd das-runner-manager
pip install -r src/requirements.txt
```

---

### Usage

#### Start a Runner
Starts the specified number of runners for a given repository. If the GitHub token is not provided, the script will prompt for it interactively.

```bash
python3 src/cli/main.py start --repository das --runners 5
```
- **`--repository das`** → Specifies the repository name.
- **`--runners 5`** → Defines the number of runners to start.
- The script will **ask for your GitHub personal token** if not provided.

#### List Runners  
Lists all the runners that have been started for a specific repository.

```bash
python3 src/cli/main.py list --repository das
```
- **`--repository das`** → Specifies the repository name.

#### Stop a Runner
Stops all active runners for a given repository.

```bash
python3 src/cli/main.py stop --repository das
```
- **`--repository das`** → Specifies the repository whose runners should be stopped.

### Build the Binary  
To generate the binary, navigate to the `das-runner-manager` directory and run:

```bash
make build
```
- This will require **Docker** to be installed, as it uses a Docker image to generate the build.
- After running the build, a new directory called `dist` will be created within the `das-runner-manager` directory, containing the binary.


SHORT_HELP_UPD_VERSION = "Update the DAS CLI version (Ubuntu only)."

HELP_UPD_VERSION = """
NAME

update-version - Update the DAS CLI version (Ubuntu only)

DESCRIPTION

This command updates the DAS CLI to the latest version available via the APT repository.
It is intended for Ubuntu Linux distributions only and must be run with sudo privileges.

.SH OPTIONS
--version, -v     Specify the version of the package to install (format: x.y.z).
                  If omitted, the latest available version will be installed.

REQUIREMENTS

- Must be executed as a compiled binary, not as a Python script.
- Requires root privileges (sudo).
- The CLI must have been installed via APT.

EXAMPLES

Update the DAS CLI to the latest version available via APT:

    $ sudo das-cli update-version

Update the DAS CLI to a specific version (e.g. 1.2.3):

    $ sudo das-cli update-version --version=1.2.3
"""

SHORT_HELP_DAS_CLI = "'das-cli' offers a suite of commands to efficiently manage a wide range of tasks including management of containerized services"

HELP_DAS_CLI = """
NAME

das-cli - Command-line interface for managing DAS services

DESCRIPTION

'das-cli' offers a suite of commands to efficiently manage a wide range of tasks, including:

- Containerized service orchestration
- OpenFaaS function management
- Knowledge base operations
- System package management (via APT)

REMOTE EXECUTION

Any command can be executed on a remote server via SSH by enabling the --remote flag and providing connection parameters.

OPTIONS FOR REMOTE EXECUTION

--remote              Run the command on a remote server over SSH
--host, -H            Hostname or IP address of the remote server
--user, -H            SSH login user
--port, -H            SSH port (default: 22)
--key-file            Path to the SSH private key file (for key-based authentication)
--password            SSH password (not recommended for production)
--connect-timeout     SSH connection timeout in seconds (default: 10)

EXAMPLES

Run command remotely using SSH key:

    $ das-cli deploy --remote --host 192.168.0.10 --user ubuntu --key-file ~/.ssh/id_rsa

Run command remotely using password:

    $ das-cli update --remote --host 10.0.0.2 --user root --password yourpassword

"""

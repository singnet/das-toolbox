HELP_RELEASE_NOTES = """
NAME

    release-notes - Display available release notes for DAS

SYNOPSIS

    das-cli release-notes [--module=<module_name>] [--list]

DESCRIPTION

    Allows you to view release notes for DAS.
    This command retrieves information from the release notes document hosted at:
    https://github.com/singnet/das/blob/master/docs/release-notes.md.

    It displays the release notes for the latest DAS version available or for a specified module.

OPTIONS

    --module=<module_name>

        Specify the name of the module to view release notes for a specific component of DAS.

    --list

        Display only a list of available versions for each component without showing the full changelog.

EXAMPLES

    View release notes for the latest DAS version:

        $ das-cli release-notes

    View release notes for the hyperon-das component:

        $ das-cli release-notes --module=hyperon-das

    View a list of available versions for each component without the full changelog:

        $ das-cli release-notes --list
"""

SHORT_HELP_RELEASE_NOTES = "Display available release notes."
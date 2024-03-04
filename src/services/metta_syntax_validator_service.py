import glob
import click
from exceptions import ValidateFailed
from services.metta_parser_container_service import MettaParserContainerService


class MettaSyntaxValidatorService:
    def check_syntax(self, file_path):
        metta_parser_service = MettaParserContainerService()

        metta_parser_service.start_container(file_path)
        click.secho("Checking syntax... OK", fg="green")

    def validate_file(self, file_path):
        click.echo(f"Checking file {file_path}:")
        try:
            self.check_syntax(file_path)
        except IsADirectoryError:
            click.secho(f"The specified path '{file_path}' is a directory.", fg="red")
        except FileNotFoundError:
            click.secho(
                f"The specified file path '{file_path}' does not exist.", fg="red"
            )
        except ValidateFailed:
            click.secho("Checking syntax... FAILED", fg="red")

    def validate_directory(self, directory_path):
        files = glob.glob(f"{directory_path}/*")
        for file_path in files:
            self.validate_file(file_path)

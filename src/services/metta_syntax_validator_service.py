import glob
import click
from services.metta_parser_container_service import MettaParserContainerService
from exceptions import MettaSyntaxException


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
            raise IsADirectoryError(f"The specified path '{file_path}' is a directory.")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"The specified file path '{file_path}' does not exist."
            )
        except MettaSyntaxException:
            click.secho("Checking syntax... FAILED", fg="red")

    def validate_directory(self, directory_path):
        files = glob.glob(f"{directory_path}/*")
        for file_path in files:
            self.validate_file(file_path)

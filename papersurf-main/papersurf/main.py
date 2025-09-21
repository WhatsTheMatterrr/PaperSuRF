# Copyright (c) 2025 Robinson Fuller Ltd
# Licensed under the MIT License.

from neo4j import GraphDatabase


from conf import settings
from analysis import Analysis
from visualisation import Visualisation
from command_line import CommandLineInterface


class PaperSurf:
    def __init__(self):
        # Initialize core components
        self.analyzer = Analysis()
        self.cli = CommandLineInterface()
        self.vis = Visualisation()

        self.driver = GraphDatabase.driver(
            settings.DATABASE_URI,
            auth=(settings.DATABASE_USERNAME, settings.DATABASE_PASSWORD),
        )
        self.driver.verify_connectivity()

    def initialize(self) -> None:
        """
        Performs initial setup operations before running the application.
        """

        print("Initializing")

    def run(self) -> None:
        """
        Executes the main logic of the application.
        """

        print("Running")

        self.cli.run(self.analyzer, self.driver.session())

    def terminate(self) -> None:
        """
        Handles any cleanup or termination logic after the application finishes running.
        """

        print("Terminating")

        pass

    def exec(self) -> None:
        """
        Executes the full application lifecycle: initialize, run, and terminate.
        """

        self.initialize()
        self.run()
        self.terminate()


def main() -> None:
    """
    Main entry point of the program.

    Args:
        None: This method does not take any arguments.

    Returns:
        None: This method does not return anything.
    """

    app = PaperSurf()
    app.exec()

# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# Unit test to ensure all command strings in the CommandLineInterface map to valid, callable functions.
#
# This test instantiates the CommandLineInterface and iterates through its `commands` dictionary,
# asserting that each command maps to a callable function or method. It helps catch issues like
# undefined or incorrectly assigned handlers.

from command_line import CommandLineInterface


def test_command_handler():
    cli = CommandLineInterface()

    for command, func in cli.commands.items():
        assert callable(
            func
        ), f"Command '{command}' does not map to a callable function"

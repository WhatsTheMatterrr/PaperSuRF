# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# This unit test ensures that the CommandLineInterface initializes with the correct set of command words.
# It verifies that the predefined commands remain unchanged, preventing unintended modifications.
# If the assertion fails, it indicates that the set of recognized commands has been altered.

import pytest
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.application import Application
from command_line import CommandLineInterface


commands = [
    "exit",
    "help",
    "list",
    "search",
    "vsearch",
    "simsearch",
    "vsimsearch",
    "add",
    "e",
    "h",
    "lp",
    "st",
    "sa",
    "sp",
    "ss",
    "vsh",
    "vss",
    "a",
]


def dummy_init(self, *args, **kwargs):
    kwargs["output"] = DummyOutput()
    self.__original_init__(*args, **kwargs)


@pytest.fixture(autouse=True)
def patch_application(monkeypatch):
    Application.__original_init__ = Application.__init__
    monkeypatch.setattr(Application, "__init__", dummy_init)


def test_command_words():
    cli = CommandLineInterface()
    cli_words = list(cli.commands.keys())

    assert cli_words == commands, "Commands must match"

# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# Unit test to verify that the Neo4j database configuration in the `settings` module is correct.
#
# This test compares the values of `DATABASE_URI`, `DATABASE_USERNAME`, and `DATABASE_PASSWORD`
# from the `settings` configuration with known expected constants. It ensures that the application
# is connecting to the correct database endpoint with the appropriate credentials.
#
# This helps catch misconfigurations early, especially in deployment or environment setup.

from conf import settings

DATABASE_URI = "neo4j+ssc://8e0ec871.databases.neo4j.io"
DATABASE_USERNAME = "neo4j"
DATABASE_PASSWORD = "43JUeFm3Pw58JMoNCL3OresNvEZd8QxCtqEZeBdK5BI"


def test_neo4j_config():
    assert settings.DATABASE_URI == DATABASE_URI, "Database URI must match"
    assert (
        settings.DATABASE_USERNAME == DATABASE_USERNAME
    ), "Database Username must match"
    assert (
        settings.DATABASE_PASSWORD == DATABASE_PASSWORD
    ), "Database Password must match"

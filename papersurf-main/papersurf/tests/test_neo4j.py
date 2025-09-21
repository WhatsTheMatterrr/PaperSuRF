# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# This test verifies that a connection can be established to the Neo4j database
# using the credentials and URI provided in the settings module. It runs a basic
# Cypher query to confirm successful communication with the database and checks
# that a valid result is returned. The connection is properly closed after the test.

from neo4j import GraphDatabase

from conf import settings


def test_neo4j_connection():
    """Test Neo4j database connectivity and a simple query."""
    driver = GraphDatabase.driver(
        settings.DATABASE_URI,
        auth=(settings.DATABASE_USERNAME, settings.DATABASE_PASSWORD),
    )

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful' AS message")
            records = list(result)
            assert records, "No results returned from test query."

    finally:
        driver.close()

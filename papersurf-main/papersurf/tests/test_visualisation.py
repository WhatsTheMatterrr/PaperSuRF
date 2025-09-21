# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# test_visualisation.py
# This unit test suite ensures that the `visualise_output` function from the `visualisation` module
# operates correctly in various scenarios.
# The tests include:
#   1) Generating a visualization without similarity-based edges,
#   2) Generating a visualization with similarity-based edges,
#   3) Handling an empty list of papers.
# If any assertion fails, it indicates a problem with the function's logic or output,
# such as failing to generate an HTML file or raising an unexpected exception.

import os
import pytest
from visualisation import visualise_output


@pytest.fixture
def sample_papers_no_similarity():
    return [
        {
            "Title": "Paper Title 1",
            "DOI": "10.1234/xyz123",
            "Author": "Author A",
        },
        {
            "Title": "Paper Title 2",
            "DOI": "10.5678/uvw456",
            "Author": "Author B",
        },
    ]


@pytest.fixture
def sample_papers_with_similarity():
    return [
        {
            "Title": "Similar Paper 1",
            "DOI": "10.9999/paper111",
            "Author": "Author C",
            "Similarity": 0.9,
        },
        {
            "Title": "Less Similar Paper 2",
            "DOI": "10.8888/paper222",
            "Author": "Author D",
            "Similarity": 0.3,
        },
    ]


def test_visualise_output_no_similarity(tmp_path, sample_papers_no_similarity):
    """
    This unit test verifies that the `visualise_output` function can generate a visualization
    when no similarity scores are provided, without opening a browser window.
    If the assertion fails, it indicates the function threw an exception or did not produce
    the expected HTML file.
    """
    output_file = tmp_path / "test_no_similarity.html"

    try:
        visualise_output(
            papers=sample_papers_no_similarity,
            central_label="TestNoSimilarity",
            output_file=str(output_file),
            use_similarity=False,
            open_browser=False,  # Disable browser popup during testing
        )
    except Exception as e:
        pytest.fail(f"`visualise_output` raised an exception without similarity: {e}")

    # Verify the HTML file was generated
    assert output_file.exists(), "HTML file was not generated."


def test_visualise_output_with_similarity(tmp_path, sample_papers_with_similarity):
    """
    This unit test ensures that the `visualise_output` function can successfully handle
    similarity scores and produce the correct visualization without automatically
    opening a browser window. If the assertion fails, it indicates the function threw
    an exception or did not produce the expected output file.
    """
    output_file = tmp_path / "test_with_similarity.html"

    try:
        visualise_output(
            papers=sample_papers_with_similarity,
            central_label="TestWithSimilarity",
            output_file=str(output_file),
            use_similarity=True,
            open_browser=False,  # Disable browser popup during testing
        )
    except Exception as e:
        pytest.fail(f"`visualise_output` raised an exception with similarity: {e}")

    # Verify the HTML file was generated
    assert output_file.exists(), "HTML file was not generated."


def test_visualise_output_empty_papers(tmp_path):
    """
    This unit test verifies that the `visualise_output` function can handle an empty
    list of papers without raising exceptions. If the assertion fails, it indicates
    the function was unable to gracefully handle an empty data set or did not produce
    the expected output file.
    """
    output_file = tmp_path / "test_empty.html"

    try:
        visualise_output(
            papers=[],
            central_label="EmptyPapers",
            output_file=str(output_file),
            use_similarity=False,
            open_browser=False,  # Disable browser popup during testing
        )
    except Exception as e:
        pytest.fail(f"`visualise_output` raised an exception on empty papers: {e}")

    # Verify that a minimal HTML file was still generated
    assert output_file.exists(), "HTML file was not generated for empty papers."

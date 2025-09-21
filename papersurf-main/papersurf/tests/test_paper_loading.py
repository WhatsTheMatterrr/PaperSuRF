# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# Here we will load a predfined list of papers which we know what the output should be
# We will test to ensure that our loading functionality produces the expected results.

import os
import json
from keybert import KeyBERT
from paper import Paper
from command_line import papers_load

keyword_extractor = KeyBERT()

paper_path = "data/test"

expected = [
    {
        "filename": "1-s2.0-S0002822399003077-main.pdf",
        "title": "doi:10.1016/S0002-8223(99)00307-7",
        "authors": "",
        "topics": [],
        "doi": "https://doi.org/10.1016/S0002-8223(99)00307-7",
        "main_keyphrase": "No keyphrase",
    },
    {
        "filename": "1-s2.0-S027322971400046X-main.pdf",
        "title": "How approximate and exact number skills are related to each other across development: A review☆",
        "authors": "Christophe Mussolin",
        "topics": [
            "skills in the domain of number cognition",
            "approximate number skills and culturally acquired numerical",
            "evidence shows that the approximate number skills",
            "number skills reﬁnes the approximate number skills",
            "number skills are built on the approximate",
        ],
        "doi": "https://doi.org/10.1016/j.dr.2014.11.001",
        "main_keyphrase": "skills in the domain of number cognition",
    },
]


def test_load_papers():
    loaded_papers = papers_load(paper_path, keyword_extractor)
    assert len(loaded_papers) == len(
        expected
    ), f"Expected {len(expected)} papers, got {len(loaded_papers)}"

    for i, (paper, exp) in enumerate(zip(loaded_papers, expected)):
        assert paper.filename == exp["filename"], f"[{i}] filename mismatch"
        assert paper.title == exp["title"], f"[{i}] title mismatch"
        assert paper.author == exp["authors"], f"[{i}] authors mismatch"
        assert paper.topics == exp["topics"], f"[{i}] topics mismatch"
        assert paper.doi == exp["doi"], f"[{i}] doi mismatch"
        assert (
            paper.main_keyphrase == exp["main_keyphrase"]
        ), f"[{i}] main_keyphrase mismatch"

    print("test_load_papers passed.")

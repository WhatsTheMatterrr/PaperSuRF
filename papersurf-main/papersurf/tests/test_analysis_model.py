# © 2025 PaperSuRF. Licensed under the MIT License.
# Free to use, modify, and distribute without warranty.

# Unit test to ensure the Analysis class initialises with the correct semantic model.
#
# This test creates an instance of the Analysis class and verifies that its `model` attribute
# is set to "all-MiniLM-L6-v2", which is the expected default model for semantic similarity operations.
#
# It helps catch issues such as incorrect model loading or unintended changes to the default configuration.
#


from analysis import Analysis


def test_analysis_model():
    a = Analysis()
    assert a.model == "all-MiniLM-L6-v2", "Analysis model must match"

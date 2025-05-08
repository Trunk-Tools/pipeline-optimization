import json

import pytest
from pipeline_optimization.orchestrator import TaskOrchestrator


@pytest.fixture
def test_cases():
    with open("src/pipeline_optimization/resources/test_cases.json") as f:
        return json.load(f)


@pytest.fixture
def orchestrator():
    return TaskOrchestrator()


def test_small_case(orchestrator, test_cases):
    """Test that the orchestrator correctly processes the small test case."""
    test_case = test_cases["small"]
    result = orchestrator.process_text(test_case["text"])

    # Check that all expected anagrams are present
    for anagram, count in test_case["expected"]["anagram_counts"].items():
        assert anagram in result["anagram_counts"], f"Missing anagram: {anagram}"
        assert result["anagram_counts"][anagram] == count, f"Wrong count for {anagram}"

    # Check that no unexpected anagrams are present
    for anagram in result["anagram_counts"]:
        assert anagram in test_case["expected"]["anagram_counts"], (
            f"Unexpected anagram: {anagram}"
        )


def test_input_validation(orchestrator):
    """Test that the orchestrator properly validates input."""
    with pytest.raises(ValueError):
        orchestrator.process_text(123)  # Not a string


def test_empty_input(orchestrator):
    """Test that the orchestrator handles empty input."""
    result = orchestrator.process_text("")
    assert result["anagram_counts"] == {}, "Empty input should produce no anagrams"

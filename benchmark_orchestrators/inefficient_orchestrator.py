import json
import time
from typing import Any, Dict, List

from pipeline_optimization.tasks.filter_input_task import filter_input
from pipeline_optimization.tasks.find_anagrams_task import find_anagrams
from pipeline_optimization.tasks.get_words_task import get_words


class TaskOrchestrator:
    """
    A deliberately inefficient pipeline orchestrator.

    This class contains multiple performance issues and poor design patterns that
    candidates are expected to identify and optimize during the interview exercise.

    Key inefficiencies include:
    - Sequential processing of all tasks
    - No error handling or retries for task failures
    - Repeated loading of resources
    - Lack of caching for expensive operations
    - Inefficient data structures and algorithms
    """

    def __init__(self) -> None:
        # INEFFICIENCY: Loading the dictionary on every instantiation
        # This should be done once at module level or cached
        self.dictionary = None
        self._load_dictionary()

    def _load_dictionary(self) -> None:
        # INEFFICIENCY: Expensive JSON parsing operation performed unnecessarily
        # This could be cached or loaded only once
        with open("src/pipeline_optimization/resources/english_dictionary.json") as f:
            self.dictionary = json.load(f)

    async def process_text(self, text_input: str) -> Dict[str, Any]:
        """
        Process the input text through the pipeline, finding anagrams and
        counting occurrences.

        Args:
            text_input: The text input to process

        Returns:
            Dictionary containing anagram counts and execution metrics
        """
        # Start timing the pipeline execution
        start_time = time.perf_counter()

        # INEFFICIENCY: No input validation
        if not isinstance(text_input, str):
            raise ValueError("Input must be a string")

        # INEFFICIENCY: Processing input sequentially with no parallelism
        # Stage 1: Filter the input text
        filtered_input = await filter_input(text_input)

        # Stage 2: Get individual words from the filtered input
        words = await get_words(filtered_input)

        # INEFFICIENCY: Sequential processing of words
        # This could be parallelized to improve performance
        all_anagrams: List[str] = []
        for word in words:
            # INEFFICIENCY: No caching of anagram results for repeated words
            print(f"Finding anagrams for {word}")
            anagrams = await find_anagrams(word)
            all_anagrams.extend(anagrams)

        # INEFFICIENCY: Inefficient counting algorithm
        # Could use Counter from collections instead
        anagram_counts: Dict[str, int] = {}
        for anagram in all_anagrams:
            # INEFFICIENCY: Repeated dictionary lookups
            if anagram not in anagram_counts:
                anagram_counts[anagram] = 0
            anagram_counts[anagram] += 1

        # INEFFICIENCY: No error handling for task failures
        # Should implement retries with exponential backoff

        # Calculate execution time
        end_time = time.perf_counter()
        runtime_ms = (end_time - start_time) * 1000

        # INEFFICIENCY: No error handling - just raises the error
        return {"runtime": runtime_ms, "anagram_counts": anagram_counts}

"""
====================================================================
START HERE — Data Pipeline Optimization Exercise
====================================================================

Welcome! This file (`orchestrator.py`) is the ONLY file you should
edit. Everything below is here to get you started.

1. SETUP
   This project uses `uv` to manage Python and dependencies.
   - Install it (one-time):
       macOS/Linux:  curl -LsSf https://astral.sh/uv/install.sh | sh
       Windows:      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
       (or `brew install uv` / `pip install uv`)
   - Then run the pipeline (uv sets up the venv + Python for you):
       uv run main --test-case small

2. GET ORIENTED
   Open `src/pipeline_optimization/resources/test_cases.json` to see
   the kind of input/output this pipeline deals with. Running `main`
   executes against these test cases.

3. MEASURE
   Benchmark the current (deliberately inefficient) implementation so
   you have a baseline to improve against:
       uv run benchmark --test-case small
   Re-run it as you optimize to track your impact.

4. THINK OUT LOUD — AND PLEASE DON'T USE AI ASSISTANTS
   This exercise is mostly about how you *think* about data pipelines,
   not about memorizing syntax. Please talk through your thought
   process as you go: what you notice, the trade-offs you're weighing,
   and why you choose a given approach. Don't worry about getting
   syntax perfect — your interviewer is happy to help with that if
   needed. Just please don't use Copilot, Cursor AI, ChatGPT, or
   similar tools; we want to see your own reasoning.

Good luck!
====================================================================
"""

import asyncio
import json
import sys
import time
from typing import Any

from pipeline_optimization.tasks.filter_input_task import filter_input
from pipeline_optimization.tasks.find_anagrams_task import find_anagrams
from pipeline_optimization.tasks.get_words_task import get_words

# TODO: ONLY edit this file


class TaskOrchestrator:
    """
    A deliberately inefficient pipeline orchestrator.

    This class contains multiple performance issues and poor design patterns that
    candidates are expected to identify and optimize during the interview exercise.
    """

    def __init__(self) -> None:
        self.dictionary = None
        self._load_dictionary()

    def _load_dictionary(self) -> None:
        with open("src/pipeline_optimization/resources/english_dictionary.json") as f:
            self.dictionary = json.load(f)

    async def process_text(self, text_input: str) -> dict[str, Any]:
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

        # Stage 1: Filter the input text
        filtered_input = await filter_input(text_input)

        # Stage 2: Get individual words from the filtered input
        words = await get_words(filtered_input)

        # Stage 3: Find anagrams for each word
        all_anagrams: list[str] = []
        for word in words:
            print(f"Finding anagrams for {word}")
            anagrams = await find_anagrams(word)
            all_anagrams.extend(anagrams)

        # Stage 4: Count the anagrams
        anagram_counts: dict[str, int] = {}
        for anagram in all_anagrams:
            if anagram not in anagram_counts:
                anagram_counts[anagram] = 0
            anagram_counts[anagram] += 1

        # Calculate execution time
        end_time = time.perf_counter()
        runtime_ms = (end_time - start_time) * 1000

        return {
            "runtime": runtime_ms,
            "anagram_counts": anagram_counts,
        }


async def main():
    """Main entry point for the orchestrator script."""
    # Get input text from command line argument or use a default
    text_input = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Hello world, this is a test input for anagram processing."
    )

    orchestrator = TaskOrchestrator()
    result = await orchestrator.process_text(text_input)

    print(f"Pipeline runtime: {result['runtime']:.2f} ms")
    print("Anagram counts:")
    for anagram, count in result["anagram_counts"].items():
        print(f"  {anagram}: {count}")


def main_sync():
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()

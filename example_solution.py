"""
Example solution for the data pipeline optimization exercise.

This file is for interviewer reference only and shows one possible approach
to optimizing the inefficient orchestrator. The candidate's solution may
differ but should address similar concerns.
"""

import asyncio
import json
import logging
import time
from collections import Counter
from functools import lru_cache
from typing import Any, Callable, Dict, List

from pipeline_optimization.tasks.filter_input_task import filter_input
from pipeline_optimization.tasks.find_anagrams_task import find_anagrams
from pipeline_optimization.tasks.get_words_task import get_words

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OptimizedOrchestrator")

# Load the dictionary once at module level
with open("src/pipeline_optimization/resources/english_dictionary.json") as f:
    ENGLISH_DICTIONARY = json.load(f)


class OptimizedOrchestrator:
    """
    An optimized implementation of the pipeline orchestrator.

    Key improvements:
    - Dictionary loaded once at module level
    - Async processing of words with controlled concurrency
    - Retry mechanism with exponential backoff
    - Caching of anagram results
    - Efficient counting using Counter
    """

    def __init__(
        self, max_workers: int = 5, max_retries: int = 3, initial_backoff: float = 0.1
    ) -> None:
        """
        Initialize the optimized orchestrator.

        Args:
            max_workers: Maximum number of concurrent workers
            max_retries: Maximum number of retry attempts for failed tasks
            initial_backoff: Initial backoff time in seconds (doubles with each retry)
        """
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

        # In-memory cache for anagrams
        self.anagram_cache: Dict[str, List[str]] = {}

    async def process_text(self, text_input: str) -> Dict[str, Any]:
        """
        Process the input text through the pipeline, finding anagrams and
        counting occurrences.

        Args:
            text_input: The text input to process

        Returns:
            Dictionary containing anagram counts and execution metrics
        """
        start_time = time.perf_counter()

        try:
            # Input validation
            if not isinstance(text_input, str):
                raise ValueError("Input must be a string")

            # Stage 1: Filter the input text (with retries)
            filtered_input = await self._execute_with_retry(
                task=filter_input, input_data=text_input, task_name="filter_input"
            )

            # Stage 2: Get individual words from the filtered input (with retries)
            words = await self._execute_with_retry(
                task=get_words, input_data=filtered_input, task_name="get_words"
            )

            # Stage 3: Find anagrams for all words concurrently
            all_anagrams = await self._process_words_concurrently(words)

            # Stage 4: Count anagram occurrences efficiently
            anagram_counts = dict(Counter(all_anagrams))

            # Calculate execution time
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000

            return {"runtime": runtime_ms, "anagram_counts": anagram_counts}

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

    async def _execute_with_retry(
        self, task: Callable, input_data: Any, task_name: str
    ) -> Any:
        """
        Execute a task with retry logic and exponential backoff.

        Args:
            task: The task function to execute
            input_data: Input data for the task
            task_name: Name of the task for logging

        Returns:
            Result of the successful task execution

        Raises:
            Exception: If the task fails after all retry attempts
        """
        backoff = self.initial_backoff

        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for {task_name}")

                result = task(input_data)

                if attempt > 0:
                    logger.info(f"Task {task_name} succeeded after {attempt} retries")

                return result

            except Exception as e:
                if attempt == self.max_retries:
                    logger.error(
                        f"Task {task_name} failed after {attempt + 1} attempts: {str(e)}"
                    )
                    raise

                logger.warning(
                    f"Task {task_name} failed (attempt {attempt + 1}): {str(e)}"
                )

                # Exponential backoff
                await asyncio.sleep(backoff)
                backoff *= 2

    @lru_cache(maxsize=1000)
    async def _find_anagrams_cached(self, word: str) -> List[str]:
        """
        Find anagrams for a word with caching and retry logic.

        Args:
            word: The word to find anagrams for

        Returns:
            List of anagrams for the word
        """
        return await self._execute_with_retry(
            task=find_anagrams, input_data=word, task_name=f"find_anagrams({word})"
        )

    async def _process_words_concurrently(self, words: List[str]) -> List[str]:
        """
        Process words concurrently to find anagrams.

        Args:
            words: List of words to process

        Returns:
            List of all anagrams found
        """
        # Deduplicate words to avoid redundant processing
        unique_words = set(words)
        logger.info(
            f"Processing {len(unique_words)} unique words (from {len(words)} total)"
        )

        # Process words concurrently with a bounded semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_word(word: str) -> List[str]:
            async with semaphore:
                return await self._find_anagrams_cached(word)

        # Create tasks for all words
        tasks = [process_word(word) for word in unique_words]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, filtering out exceptions
        all_anagrams = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Failed to process word: {str(result)}")
            else:
                all_anagrams.extend(result)

        return all_anagrams

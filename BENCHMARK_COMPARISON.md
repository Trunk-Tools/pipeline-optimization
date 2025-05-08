# Benchmark Comparison Tool

This tool allows you to compare the performance of multiple orchestrator implementations against the baseline inefficient implementation. It helps to evaluate different optimization approaches and strategies.

## Prerequisites

- Make sure you have [hatch](https://hatch.pypa.io/latest/) installed
- All orchestrator implementations should be placed in a directory with `.py` files
- Each file should contain a `TaskOrchestrator` class

## Running the Comparison

To run the benchmark comparison:

```bash
hatch run compare-benchmarks --compare-dir benchmark_orchestrators
```

This will:

1. Load the baseline inefficient orchestrator
2. Load each orchestrator implementation from the specified directory
3. Run benchmarks for all test cases for each orchestrator
4. Display a side-by-side comparison of performance metrics

## Command Line Options

- `--compare-dir`: Directory containing orchestrator implementations (required)
- `--test-case`: Specific test case to run (`small`, `medium`, `large`, or `all`)
- `--iterations`: Number of iterations for each benchmark (default: 3)
- `--detailed`: Show detailed metrics for each orchestrator

## Example

```bash
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --iterations 5
```

This will run 5 iterations of each test case for each orchestrator found in the `benchmark_orchestrators` directory.

## Included Orchestrator Implementations

This repository comes with two example optimized orchestrators:

1. **optimized_orchestrator.py**

   - Uses async/await for concurrency
   - Implements retry with exponential backoff
   - Caches anagram results with LRU cache
   - Deduplicates words to avoid redundant processing

2. **threaded_orchestrator.py**
   - Uses thread pools instead of asyncio
   - Implements retry with jitter
   - Caches anagram results
   - Uses efficient data structures for counting

## Creating Your Own Orchestrator

To create a new orchestrator implementation:

1. Create a Python file in the comparison directory
2. Implement a class named `TaskOrchestrator`
3. Include at least a `process_text(text_input: str) -> Dict[str, Any]` method
4. The method should return a dictionary with:
   - `runtime`: Execution time in milliseconds
   - `anagram_counts`: Dictionary mapping anagrams to their counts

## Metrics Explanation

The comparison shows the following metrics:

- **Avg Runtime (ms)**: Average execution time in milliseconds (lower is better)
- **Success Rate (%)**: Percentage of successful runs (higher is better)
- **Throughput (words/sec)**: Number of words processed per second (higher is better)
- **Peak Memory (MB)**: Maximum memory usage (lower is better)
- **Avg CPU Usage (%)**: Average CPU utilization

The best value for each metric (except CPU Usage) is highlighted in green.

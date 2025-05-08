# Orchestrator Benchmark Comparison Tool

This tool allows you to compare multiple TaskOrchestrator implementations to evaluate their performance metrics side-by-side.

## Overview

The benchmark comparison tool:

1. Runs each benchmark against the same test cases
2. Collects metrics on runtime, success rate, throughput, memory usage, and CPU usage
3. Displays a side-by-side comparison of all implementations
4. Highlights the best values in each metric category

## Quick Start

To run the comparison benchmark with included optimized orchestrators:

```bash
./run_comparison.sh
```

This script will:

1. Run the baseline benchmark with the inefficient orchestrator
2. Run a comparison between all orchestrators in the `benchmark_orchestrators` directory

## Manual Usage

You can also run the comparison tool manually with various options:

```bash
# Run comparison with specific test cases
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --test-case small,medium

# Run comparison with more iterations
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --iterations 5

# Show detailed metrics for each orchestrator
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --detailed
```

## Included Implementations

The repository includes the following orchestrator implementations:

1. **Baseline (TaskOrchestrator)**

   - Intentionally inefficient implementation
   - No concurrency or caching
   - Weak error handling

2. **Simple Optimized Orchestrator**

   - Basic optimizations including caching and retry logic
   - Efficient data structures
   - Focuses on simplicity and maintainability

3. **Thread-based Optimized Orchestrator**

   - Uses thread pools for concurrent processing
   - Includes backoff and jitter for retries
   - Robust error handling

4. **Async-based Optimized Orchestrator** (currently not working)
   - Uses asyncio for concurrency
   - Shows an alternative concurrency model

## Understanding Metrics

The comparison report displays the following metrics:

- **Average Runtime (ms)**: Lower is better
- **Success Rate (%)**: Higher is better
- **Throughput (words/sec)**: Higher is better
- **Peak Memory (MB)**: Lower is better
- **Average CPU Usage (%)**: Neither higher nor lower is inherently better

## Creating Your Own Implementation

To create your own implementation for comparison:

1. Create a Python file in the `benchmark_orchestrators` directory
2. Implement a class named `TaskOrchestrator`
3. Ensure it has a `process_text(text_input: str) -> Dict[str, Any]` method

See the existing implementations for examples of optimal solutions.

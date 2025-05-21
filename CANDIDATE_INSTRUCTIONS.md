# Data Pipeline Optimization Exercise

## Overview

In this exercise, you'll optimize an inefficient data pipeline that processes text to find anagrams. The current implementation suffers from various performance issues and reliability problems. Your goal is to significantly improve its efficiency, reliability, and resource utilization without changing the core functionality.

## Getting Started

1. Ensure you have [hatch](https://hatch.pypa.io/latest/) installed
2. Clone the repository and `cd` into it
3. Benchmark the current performance:
   ```
   hatch run benchmark --test-case small
   ```

## Exercise Requirements

Your task is to optimize the provided pipeline by improving the `TaskOrchestrator` class located in `src/pipeline_optimization/orchestrator.py`. The orchestrator currently has several inefficiencies and issues that need to be addressed:

1. **Inefficient Resource Loading**: Dictionary loading happens repeatedly
2. **Sequential Processing**: No concurrency or parallelism
3. **Poor Error Handling**: No retry mechanisms for task failures
4. **Inefficient Data Structures**: Suboptimal algorithms for counting and data transformation
5. **Lack of Caching**: Expensive operations are performed unnecessarily

### What to Change

You should **ONLY** modify the `src/pipeline_optimization/orchestrator.py` file. The tasks (`filter_input`, `get_words`, `find_anagrams`) are designed to occasionally fail randomly, which you'll need to handle in your optimized implementation.

### Constraints

- **DO NOT modify any files in the `tasks/` directory**
- Focus on optimizing the orchestrator implementation
- Maintain the same output format and correctness
- You have 45-60 minutes to complete the exercise

## Required Optimizations

You should implement the following optimizations:

1. **Implement Concurrent Execution**

   - Use async/await, threading, or multiprocessing to parallelize word processing
   - Ensure proper resource management and concurrency control

2. **Add Robust Error Handling**

   - Implement retry mechanisms with exponential backoff
   - Handle task failures gracefully
   - Ensure pipeline is resilient to intermittent failures

3. **Optimize Resource Usage**

   - Cache expensive operations
   - Optimize memory and CPU utilization
   - Use efficient data structures and algorithms

4. **Improve Performance**
   - Reduce end-to-end runtime
   - Increase throughput (words processed per second)
   - Minimize unnecessary operations

## Testing Your Solution

After implementing your optimizations, benchmark your implementation:

```
hatch run benchmark
```

This will run all test cases and display metrics including:

- Runtime performance
- Success rate
- Memory usage
- CPU utilization
- Throughput

## Evaluation Criteria

Your solution will be evaluated based on:

1. **Performance Improvement**

   - Reduction in runtime
   - Increased throughput
   - Better resource utilization

2. **Reliability**

   - Improved success rate
   - Graceful handling of failures
   - Consistent results across runs

3. **Code Quality**

   - Clean, readable implementation
   - Appropriate use of Python features
   - Well-structured error handling

4. **Design Decisions**
   - Appropriate choice of concurrency model
   - Efficient caching strategy
   - Effective retry mechanisms

## Tips for Success

- Analyze the current implementation to understand the inefficiencies
- Focus on the largest bottlenecks first
- Implement one optimization at a time and measure the impact
- Use Python's built-in tools and standard library where appropriate
- Don't sacrifice reliability for speed

Remember, a well-designed, reliable solution that's moderately faster is better than a highly optimized but brittle one. Good luck!

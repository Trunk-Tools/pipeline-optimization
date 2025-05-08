# Data Pipeline Optimization Exercise - Interviewer Guide

## Overview

This exercise evaluates a candidate's ability to optimize a deliberately inefficient data pipeline. It focuses on key skills for a Staff Engineer:

- Concurrent programming with async/await
- Error handling and resilience
- Resource optimization
- Performance tuning

The exercise is designed to be completed in 45-60 minutes and provides clear metrics to evaluate the candidate's solution.

## Exercise Structure

The repository is structured as follows:

- `src/pipeline_optimization/orchestrator.py`: Contains the inefficient implementation that candidates need to optimize
- `src/pipeline_optimization/tasks/`: Contains task functions with random failures (should not be modified)
- `src/pipeline_optimization/metrics.py`: Implements metrics collection
- `src/pipeline_optimization/benchmark.py`: Implements benchmarking functionality
- `src/pipeline_optimization/run_benchmark.py`: Script to run benchmarks
- `CANDIDATE_INSTRUCTIONS.md`: Instructions for the candidate
- `example_solution.py`: A reference implementation showing potential optimizations

## Evaluation Criteria

The candidate's solution should be evaluated on:

1. **Performance Improvement**

   - How much did they improve runtime and throughput?
   - Did they optimize memory and CPU usage?

2. **Reliability**

   - Does the solution handle random task failures?
   - Is the error handling robust and properly implemented?

3. **Code Quality**

   - Is the code clean, well-structured, and maintainable?
   - Is the solution properly typed and documented?

4. **Design Decisions**
   - Did they make appropriate choices for concurrency, caching, and error handling?
   - Can they explain the tradeoffs of their approach?

## Running the Exercise

1. Prepare the environment:

   ```
   pip install hatch
   hatch run pipeline --test-case small
   ```

2. Have the candidate review `CANDIDATE_INSTRUCTIONS.md`

3. Have the candidate run benchmarks to see the current performance:

   ```
   hatch run benchmark
   ```

4. Instruct them to optimize `src/pipeline_optimization/orchestrator.py`

5. After they're done, have them run benchmarks again to measure improvement:
   ```
   hatch run benchmark
   ```

## Expected Improvements

A good solution should show:

- 2-10x improvement in runtime
- Near 100% success rate (vs. frequent failures in the original)
- Lower and more stable memory usage
- Significantly higher throughput

## Discussion Points

After the exercise, discuss:

1. What optimizations did you implement and why?
2. How did you decide on your concurrency approach?
3. What was your strategy for handling task failures?
4. What additional improvements would you make given more time?
5. How would you make this pipeline production-ready?

## Reference Solution

The file `example_solution.py` contains one possible solution with:

- Module-level dictionary loading
- Async processing with controlled concurrency
- Retry mechanism with exponential backoff
- Caching with `lru_cache`
- Efficient data structures like `Counter`
- Deduplication of repeated words

This is just one approach - the candidate may implement different but equally valid solutions.

## Timing Guide

- 5 minutes: Introduce the exercise, have them read instructions
- 40-45 minutes: Candidate implements optimizations
- 10-15 minutes: Test the solution, discuss results and approach

## Troubleshooting

1. If the benchmark runs too slowly, the `--test-case small` flag can be used to test only the smallest test case.
2. If there are dependency issues, ensure the candidate uses the provided `hatch` environment.

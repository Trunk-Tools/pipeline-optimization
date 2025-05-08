# Data Pipeline Take Home Exercise

Hi! Welcome to the data pipeline take home exercise.

We've fabricated a made-up pipeline with the following requirements:

1. Accept a blob of text as input
2. Blob should be analyzed for unique anagrams and report back the number of occurrences of words with those anagrams.

For example, given the input "cat". The output should be:

```
{
  "act": 1,
  "cat": 1,
  "tac": 1
}
```

The first version of the pipeline is implemented in `main.py`.
We've provided you with some test cases in `resources/test_cases.json` that you can use to test your implementation. In fact, just running `main.py` will run the test cases for you.

In order to simulate some real-life data pipeline behavior we've added some random failures at various stages. See `src/pipeline_optimization/tasks/task_decorator.py` its usages for more detail.

Your task is to improve this pipeline. You can do this in any way you see fit. You can refactor the code, add tests, add new features, or anything else you think would make the pipeline better so long as it continues to fulfill its function.

We're interested in seeing how you think about data pipelines.

- How efficient is it?
- How durable is it?
- How maintainable is it?
- How scalable is it?
- How testable is it?
- How observable is it?

As you complete the exercise, please document your thought process in a README.md file. This is your opportunity to show us how you think about data pipelines and what you think is important in building them.

## Getting Started

1. You'll need to install [hatch](https://hatch.pypa.io/latest/)
2. Clone this repo
3. `cd pipeline-optimization`
4. `hatch run pipeline`. This will setup your local virtual environment and run the pipeline for the "small" test case.
   1. To run a specific test case or to run all of them use the `--test-case` flagrun: `hatch run pipeline --test-case small|medium|large|all`

## Benchmarking Tools

The repository includes two powerful benchmark tools to help you evaluate your optimizations:

### Single Implementation Benchmark

The `benchmark` command runs performance metrics on a single orchestrator implementation:

```bash
# Run benchmark on all test cases
hatch run benchmark

# Run benchmark on a specific test case
hatch run benchmark --test-case small

# Run with more iterations for better statistical significance
hatch run benchmark --iterations 5

# Show detailed metrics
hatch run benchmark --detailed
```

This tool measures:

- Success rate (percentage of runs that complete without errors)
- Average runtime (in milliseconds)
- Throughput (words processed per second)
- Memory usage (peak and growth)
- CPU utilization

### Orchestrator Comparison Benchmark

The `compare-benchmarks` command allows you to compare multiple orchestrator implementations side-by-side:

```bash
# Compare all orchestrators in a directory
hatch run compare-benchmarks --compare-dir benchmark_orchestrators

# Compare specific test case
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --test-case small

# Run more iterations for each test
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --iterations 5

# Show detailed metrics
hatch run compare-benchmarks --compare-dir benchmark_orchestrators --detailed
```

This tool:

- Loads all Python files from the specified directory that contain a `TaskOrchestrator` class
- Runs benchmarks for each implementation with the same test cases
- Generates a side-by-side comparison table highlighting the best performers
- Helps identify which optimization strategies are most effective

For convenience, the repository includes a shell script `run_comparison.sh` that runs both the baseline benchmark and a comparison across all orchestrators in the `benchmark_orchestrators` directory.

### Interpreting Benchmark Results

When evaluating different implementations, consider these key metrics:

- **Success Rate**: Higher is better - measures reliability and error handling
- **Runtime**: Lower is better - measures overall performance
- **Throughput**: Higher is better - measures processing efficiency
- **Memory Usage**: Lower is better - measures resource efficiency

The comparison benchmark will highlight the best value for each metric in green, making it easy to identify which implementation performs best in each category.

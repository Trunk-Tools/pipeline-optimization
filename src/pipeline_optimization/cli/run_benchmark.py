#!/usr/bin/env python3
"""
Benchmark script for the data pipeline exercise.

This script provides a dedicated command to run benchmarks against the
inefficient orchestrator. Candidates should optimize the orchestrator and
then compare the performance before and after their changes.
"""

import argparse
import asyncio
import json

from pipeline_optimization.benchmarks.benchmarker import PipelineBenchmarker
from pipeline_optimization.benchmarks.metrics import MetricsCollector
from pipeline_optimization.orchestrator import TaskOrchestrator


async def main() -> None:
    """
    Main benchmark runner.

    This sets up the benchmark environment and runs the specified test cases,
    collecting and reporting performance metrics.
    """
    parser = argparse.ArgumentParser(
        description="Benchmark the data pipeline implementation."
    )
    parser.add_argument(
        "--test-case",
        type=str,
        default="all",
        help="Specify which test case to benchmark. Options: small, medium, large, all",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations for each benchmark",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed metrics for each test case",
    )

    args = parser.parse_args()

    # Create the orchestrator - candidates will replace this with their optimized version
    orchestrator = TaskOrchestrator()

    # Create metrics collector
    metrics_collector = MetricsCollector()

    # Create benchmarker
    benchmarker = PipelineBenchmarker(orchestrator, metrics_collector)

    # Load test cases
    with open("src/pipeline_optimization/resources/test_cases.json") as file:
        test_cases = json.load(file)

    print("=" * 80)
    print(f"Running benchmarks with {args.iterations} iterations per test case")
    print("=" * 80)

    # Run benchmarks
    if args.test_case != "all" and args.test_case in test_cases:
        # Run benchmark for a specific test case
        result = await benchmarker.run_benchmark(args.test_case, args.iterations)
        benchmarker.print_benchmark_report({args.test_case: result})

        if args.detailed:
            print("\nDetailed Metrics:")
            print(json.dumps(result.to_dict(), indent=2))
    else:
        # Run benchmarks for all test cases
        results = await benchmarker.run_all_benchmarks(args.iterations)
        benchmarker.print_benchmark_report(results)

        if args.detailed:
            print("\nDetailed Metrics:")
            detailed_results = {
                name: result.to_dict() for name, result in results.items()
            }
            print(json.dumps(detailed_results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

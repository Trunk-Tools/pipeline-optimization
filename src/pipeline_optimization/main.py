import argparse
import asyncio
import json
import time
from typing import Any, Dict

from pipeline_optimization.benchmarks.benchmarker import PipelineBenchmarker
from pipeline_optimization.benchmarks.metrics import MetricsCollector
from pipeline_optimization.orchestrator import TaskOrchestrator


async def run_pipeline(
    test_case_name: str,
    test_case: Dict[str, Any],
    orchestrator: TaskOrchestrator,
) -> None:
    """
    Run the pipeline for a single test case and validate the results.

    Args:
        test_case_name: Name of the test case
        test_case: Test case dictionary containing input text and expected results
        orchestrator: Pipeline orchestrator implementation
    """
    print(f"Running test case: {test_case_name}")

    # Run the pipeline
    start_time = time.perf_counter()
    result = orchestrator.process_text(test_case["text"])
    end_time = time.perf_counter()

    runtime_ms = (end_time - start_time) * 1000

    print(f"Pipeline execution completed in {runtime_ms:.2f}ms")
    print(json.dumps(result, indent=2))

    # Validate results
    expected_runtime = test_case["expected"]["runtime"]
    if runtime_ms > expected_runtime:
        print(f"⚠️ Runtime {runtime_ms:.2f}ms exceeds expected {expected_runtime}ms")
    else:
        print(f"✅ Runtime {runtime_ms:.2f}ms is within expected {expected_runtime}ms")

    for anagram, count in test_case["expected"]["anagram_counts"].items():
        if anagram not in result["anagram_counts"]:
            print(f"❌ Anagram '{anagram}' not found in result")
        elif result["anagram_counts"][anagram] != count:
            print(
                f"❌ Anagram '{anagram}' count {result['anagram_counts'][anagram]} differs from expected {count}"
            )
        else:
            pass  # Anagram count correct


async def main() -> None:
    """
    Main entry point for the pipeline exercise.

    This function parses command line arguments and runs either a single test case
    or a full benchmark depending on the arguments provided.
    """
    parser = argparse.ArgumentParser(
        description="Run the data pipeline with a specified test case."
    )
    parser.add_argument(
        "--test-case",
        type=str,
        default="small",
        help="Specify which test case to run. Options: small, medium, large, all",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmarks instead of a single execution",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations for benchmarking",
    )

    args = parser.parse_args()

    # Create the orchestrator
    orchestrator = TaskOrchestrator()

    # Create metrics collector
    metrics_collector = MetricsCollector()

    # Load test cases
    with open("src/pipeline_optimization/resources/test_cases.json") as file:
        test_cases = json.load(file)

    if args.benchmark:
        # Run benchmarks
        benchmarker = PipelineBenchmarker(orchestrator, metrics_collector)

        if args.test_case != "all" and args.test_case in test_cases:
            # Run benchmark for a specific test case
            result = await benchmarker.run_benchmark(args.test_case, args.iterations)
            benchmarker.print_benchmark_report({args.test_case: result})
        else:
            # Run benchmarks for all test cases
            results = await benchmarker.run_all_benchmarks(args.iterations)
            benchmarker.print_benchmark_report(results)
    else:
        # Run a single test case or all test cases
        if args.test_case == "all":
            for case_name, test_case in test_cases.items():
                await run_pipeline(case_name, test_case, orchestrator)
        elif args.test_case in test_cases:
            await run_pipeline(args.test_case, test_cases[args.test_case], orchestrator)
        else:
            print(f"Unknown test case: {args.test_case}")
            print(f"Available test cases: {', '.join(test_cases.keys())}")


if __name__ == "__main__":
    asyncio.run(main())

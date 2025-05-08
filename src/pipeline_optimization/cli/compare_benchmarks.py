#!/usr/bin/env python3
"""
Benchmark comparison script for the data pipeline exercise.

This script runs benchmarks for multiple orchestrator implementations
and compares their performance side-by-side.
"""

import argparse
import asyncio
import importlib.util
import json
import os
import sys
from typing import Any, Dict

from pipeline_optimization.benchmarks.benchmarker import PipelineBenchmarker
from pipeline_optimization.benchmarks.metrics import MetricsCollector
from pipeline_optimization.orchestrator import TaskOrchestrator
from tabulate import tabulate


def load_orchestrator_from_file(file_path: str) -> Any:
    """
    Dynamically load an orchestrator class from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        Instance of the TaskOrchestrator class

    Raises:
        RuntimeError: If the file doesn't contain a TaskOrchestrator class
    """
    # Get module name from file name
    module_name = os.path.basename(file_path).replace(".py", "")

    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Check for TaskOrchestrator class
    if not hasattr(module, "TaskOrchestrator"):
        raise RuntimeError(f"File {file_path} doesn't contain a TaskOrchestrator class")

    # Create an instance of the orchestrator
    return module.TaskOrchestrator()


def find_orchestrators(compare_dir: str) -> Dict[str, Any]:
    """
    Find all Python files in the specified directory and load their orchestrators.

    Args:
        compare_dir: Directory containing orchestrator implementations

    Returns:
        Dictionary mapping orchestrator names to instances
    """
    orchestrators = {"baseline": TaskOrchestrator()}

    if not os.path.exists(compare_dir) or not os.path.isdir(compare_dir):
        print(f"Warning: Directory {compare_dir} does not exist or is not a directory")
        return orchestrators

    # Find all Python files
    for file_name in os.listdir(compare_dir):
        if file_name.endswith(".py"):
            file_path = os.path.join(compare_dir, file_name)
            try:
                orchestrator = load_orchestrator_from_file(file_path)
                orchestrators[file_name] = orchestrator
                print(f"Loaded orchestrator from {file_name}")
            except Exception as e:
                print(f"Error loading orchestrator from {file_name}: {str(e)}")

    return orchestrators


def color_text(text: str, is_best: bool = False) -> str:
    """
    Apply ANSI color formatting to text.

    Args:
        text: Text to color
        is_best: Whether this is the best value (green if True)

    Returns:
        Colored text string
    """
    # ANSI color codes
    GREEN = "\033[92m"  # Best value
    RESET = "\033[0m"  # Reset formatting

    if is_best:
        return f"{GREEN}{text}{RESET}"
    return text


def format_value(value: float, is_best: bool, format_str: str = "{:.2f}") -> str:
    """
    Format a value and apply coloring if it's the best value.

    Args:
        value: Value to format
        is_best: Whether this is the best value
        format_str: Format string to use

    Returns:
        Formatted and possibly colored value string
    """
    formatted = format_str.format(value)
    return color_text(formatted, is_best)


async def run_benchmarks(
    orchestrators: Dict[str, Any],
    iterations: int = 3,
    test_case: str = "all",
    show_details: bool = False,
) -> Dict[str, Dict[str, Any]]:
    """
    Run benchmarks for all orchestrators and collect results.

    Args:
        orchestrators: Dictionary mapping orchestrator names to instances
        iterations: Number of iterations for each benchmark
        test_case: Specific test case to run or "all"
        show_details: Whether to show detailed metrics

    Returns:
        Dictionary mapping orchestrator names to benchmark results
    """
    # Load test cases
    with open("src/pipeline_optimization/resources/test_cases.json") as file:
        test_cases = json.load(file)

    # Prepare results structure
    all_results: Dict[str, Dict[str, Any]] = {}

    # Run benchmarks for each orchestrator
    for name, orchestrator in orchestrators.items():
        print(f"\n{'=' * 80}")
        print(f"Running benchmarks for orchestrator: {name}")
        print(f"{'=' * 80}")

        metrics_collector = MetricsCollector()
        benchmarker = PipelineBenchmarker(orchestrator, metrics_collector)

        # Run benchmarks
        if test_case != "all" and test_case in test_cases:
            results = {
                test_case: await benchmarker.run_benchmark(test_case, iterations)
            }
        else:
            results = await benchmarker.run_all_benchmarks(iterations)

        # Store results
        all_results[name] = results

        # Print individual report
        if show_details:
            benchmarker.print_benchmark_report(results)

    return all_results


def aggregate_metrics(
    all_results: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate metrics across all test cases for each orchestrator.

    Args:
        all_results: Dictionary mapping orchestrator names to test case results

    Returns:
        Dictionary mapping orchestrator names to aggregated metrics
    """
    summary = {}

    for name, case_results in all_results.items():
        runtimes = []
        success_rates = []
        throughputs = []
        memory_peaks = []
        cpu_percents = []

        for test_case, result in case_results.items():
            if result.execution_times_ms:
                runtimes.append(result.average_runtime_ms)
            success_rates.append(result.success_rate)

            aggregated = result.get_aggregated_metrics()

            # Extract throughput
            if (
                "pipeline_metrics" in aggregated
                and "avg_throughput_words_per_second" in aggregated["pipeline_metrics"]
            ):
                throughputs.append(
                    aggregated["pipeline_metrics"]["avg_throughput_words_per_second"]
                )

            # Extract memory and CPU metrics
            if "resource_metrics" in aggregated:
                memory_peaks.append(
                    aggregated["resource_metrics"].get("avg_peak_memory_mb", 0)
                )
                cpu_percents.append(
                    aggregated["resource_metrics"].get("avg_cpu_percent", 0)
                )

        # Calculate averages
        summary[name] = {
            "avg_runtime_ms": sum(runtimes) / len(runtimes) if runtimes else 0,
            "success_rate": sum(success_rates) / len(success_rates)
            if success_rates
            else 0,
            "throughput_words_per_sec": sum(throughputs) / len(throughputs)
            if throughputs
            else 0,
            "peak_memory_mb": sum(memory_peaks) / len(memory_peaks)
            if memory_peaks
            else 0,
            "avg_cpu_percent": sum(cpu_percents) / len(cpu_percents)
            if cpu_percents
            else 0,
        }

    return summary


def print_comparison_table(summary: Dict[str, Dict[str, Any]]) -> None:
    """
    Print a side-by-side comparison table of all orchestrators.

    Args:
        summary: Dictionary mapping orchestrator names to aggregated metrics
    """
    if not summary:
        print("No results to compare")
        return

    # Prepare headers and metric types (lower is better or higher is better)
    metrics_info = [
        ("Avg Runtime (ms)", "avg_runtime_ms", False),  # Lower is better
        ("Success Rate (%)", "success_rate", True),  # Higher is better
        (
            "Throughput (words/sec)",
            "throughput_words_per_sec",
            True,
        ),  # Higher is better
        ("Peak Memory (MB)", "peak_memory_mb", False),  # Lower is better
        ("Avg CPU Usage (%)", "avg_cpu_percent", None),  # Neither better nor worse
    ]

    # Find best values for each metric
    best_values = {}
    for _, metric_key, higher_is_better in metrics_info:
        if higher_is_better is None:
            continue

        values = [data[metric_key] for data in summary.values() if data[metric_key] > 0]
        if not values:
            continue

        best_values[metric_key] = max(values) if higher_is_better else min(values)

    # Prepare table data
    headers = ["Metric"] + list(summary.keys())
    rows = []

    for display_name, metric_key, higher_is_better in metrics_info:
        row = [display_name]

        for orch_name in summary.keys():
            value = summary[orch_name][metric_key]

            # Determine if this is the best value
            is_best = False
            if higher_is_better is not None and metric_key in best_values and value > 0:
                is_best = value == best_values[metric_key]

            # Format the value appropriately
            if metric_key == "success_rate":
                formatted = format_value(value * 100, is_best, "{:.1f}")
            elif metric_key == "throughput_words_per_sec":
                formatted = format_value(value, is_best, "{:.1f}")
            else:
                formatted = format_value(value, is_best, "{:.2f}")

            row.append(formatted)

        rows.append(row)

    # Print the table
    print("\n" + "=" * 80)
    print("ORCHESTRATOR COMPARISON")
    print("=" * 80)
    print(tabulate(rows, headers, tablefmt="grid"))
    print("\n" + "=" * 80)
    print("Notes:")
    print("- Green values indicate best performance in that category")
    print("- Runtime and Memory: lower is better")
    print("- Success Rate and Throughput: higher is better")
    print("- CPU Usage: neither higher nor lower is inherently better")
    print("=" * 80)


async def main() -> None:
    """
    Main function to run the benchmark comparison.
    """
    parser = argparse.ArgumentParser(
        description="Compare multiple orchestrator implementations in the data pipeline."
    )
    parser.add_argument(
        "--compare-dir",
        type=str,
        required=True,
        help="Directory containing orchestrator implementations to compare",
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
        help="Show detailed metrics for each orchestrator",
    )

    args = parser.parse_args()

    # Load orchestrators from the specified directory
    orchestrators = find_orchestrators(args.compare_dir)

    if len(orchestrators) <= 1:
        print(
            "Warning: Only found the baseline orchestrator. No comparison will be made."
        )
        print(
            f"Please ensure {args.compare_dir} contains Python files with TaskOrchestrator classes."
        )
        return

    # Run benchmarks for all orchestrators
    all_results = await run_benchmarks(
        orchestrators,
        iterations=args.iterations,
        test_case=args.test_case,
        show_details=args.detailed,
    )

    # Aggregate metrics
    summary = aggregate_metrics(all_results)

    # Print comparison table
    print_comparison_table(summary)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import inspect
import json
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from pipeline_optimization.benchmarks.metrics import MetricsCollector
from pipeline_optimization.orchestrator import TaskOrchestrator


@dataclass
class BenchmarkResult:
    """Results of a benchmark run"""

    test_case: str
    iterations: int
    successful_iterations: int
    execution_times_ms: List[float] = field(default_factory=list)
    errors: List[Exception] = field(default_factory=list)
    metrics_reports: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of benchmark iterations"""
        if self.iterations == 0:
            return 0.0
        return self.successful_iterations / self.iterations

    @property
    def average_runtime_ms(self) -> float:
        """Calculate the average runtime in milliseconds"""
        if not self.execution_times_ms:
            return 0.0
        return statistics.mean(self.execution_times_ms)

    @property
    def min_runtime_ms(self) -> float:
        """Get the minimum runtime in milliseconds"""
        if not self.execution_times_ms:
            return 0.0
        return min(self.execution_times_ms)

    @property
    def max_runtime_ms(self) -> float:
        """Get the maximum runtime in milliseconds"""
        if not self.execution_times_ms:
            return 0.0
        return max(self.execution_times_ms)

    @property
    def stddev_runtime_ms(self) -> float:
        """Calculate the standard deviation of runtimes"""
        if len(self.execution_times_ms) < 2:
            return 0.0
        return statistics.stdev(self.execution_times_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert benchmark result to dictionary for reporting"""
        return {
            "test_case": self.test_case,
            "iterations": self.iterations,
            "successful_iterations": self.successful_iterations,
            "success_rate": self.success_rate,
            "average_runtime_ms": round(self.average_runtime_ms, 4),
            "min_runtime_ms": round(self.min_runtime_ms, 4),
            "max_runtime_ms": round(self.max_runtime_ms, 4),
            "stddev_runtime_ms": round(self.stddev_runtime_ms, 4),
            "metrics": self.get_aggregated_metrics(),
        }

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics from all successful runs"""
        if not self.metrics_reports:
            return {}

        # Extract key metrics and average them
        result = {
            "pipeline_metrics": {
                "avg_runtime_ms": self.average_runtime_ms,
                "success_rate": self.success_rate,
            },
            "resource_metrics": {
                "avg_peak_memory_mb": 0.0,
                "avg_memory_growth_mb": 0.0,
                "avg_cpu_percent": 0.0,
            },
            "task_metrics": {},
        }

        # Aggregate resource metrics
        memory_peaks = []
        memory_growths = []
        cpu_avgs = []
        throughputs = []

        # Task metrics collection
        task_metrics: Dict[str, Dict[str, List[float]]] = {}

        for report in self.metrics_reports:
            if "resource_metrics" in report:
                memory_peaks.append(report["resource_metrics"].get("peak_memory_mb", 0))
                memory_growths.append(
                    report["resource_metrics"].get("memory_growth_mb", 0)
                )
                cpu_avgs.append(report["resource_metrics"].get("avg_cpu_percent", 0))

            if "pipeline_metrics" in report:
                throughputs.append(
                    report["pipeline_metrics"].get("throughput_words_per_second", 0)
                )

            if "task_metrics" in report:
                for task_name, task_data in report["task_metrics"].items():
                    if task_name not in task_metrics:
                        task_metrics[task_name] = {
                            "success_rates": [],
                            "avg_execution_times_ms": [],
                            "attempts": [],
                        }

                    task_metrics[task_name]["success_rates"].append(
                        task_data.get("success_rate", 0)
                    )
                    task_metrics[task_name]["avg_execution_times_ms"].append(
                        task_data.get("average_execution_time_ms", 0)
                    )
                    task_metrics[task_name]["attempts"].append(
                        task_data.get("total_attempts", 0)
                    )

        # Calculate averages for resource metrics
        if memory_peaks:
            result["resource_metrics"]["avg_peak_memory_mb"] = round(
                statistics.mean(memory_peaks), 2
            )
        if memory_growths:
            result["resource_metrics"]["avg_memory_growth_mb"] = round(
                statistics.mean(memory_growths), 2
            )
        if cpu_avgs:
            result["resource_metrics"]["avg_cpu_percent"] = round(
                statistics.mean(cpu_avgs), 3
            )
        if throughputs:
            result["pipeline_metrics"]["avg_throughput_words_per_second"] = round(
                statistics.mean(throughputs), 1
            )

        # Calculate averages for task metrics
        for task_name, metrics_data in task_metrics.items():
            result["task_metrics"][task_name] = {
                "avg_success_rate": round(
                    statistics.mean(metrics_data["success_rates"]), 2
                ),
                "avg_execution_time_ms": round(
                    statistics.mean(metrics_data["avg_execution_times_ms"]), 4
                ),
                "avg_attempts": round(statistics.mean(metrics_data["attempts"]), 2),
            }

        return result


class PipelineBenchmarker:
    """
    Benchmarks pipeline implementations with different test cases and configurations.

    This class runs multiple iterations of pipeline executions to gather
    reliable performance metrics and identify potential optimizations.
    """

    def __init__(
        self,
        orchestrator: TaskOrchestrator,
        metrics_collector: MetricsCollector,
        test_cases_path: str = "src/pipeline_optimization/resources/test_cases.json",
    ) -> None:
        """
        Initialize the benchmarker with an orchestrator and test cases.

        Args:
            orchestrator: The pipeline orchestrator to benchmark
            metrics_collector: The metrics collector for gathering performance data
            test_cases_path: Path to the JSON file containing test cases
        """
        self.orchestrator = orchestrator
        self.metrics_collector = metrics_collector

        # Load test cases
        with open(test_cases_path) as f:
            self.test_cases = json.load(f)

    async def run_benchmark(
        self, test_case_name: str, iterations: int = 3
    ) -> BenchmarkResult:
        """
        Run a benchmark for a specific test case.

        Args:
            test_case_name: Name of the test case to benchmark
            iterations: Number of times to run the test case

        Returns:
            BenchmarkResult containing performance metrics
        """
        if test_case_name not in self.test_cases:
            raise ValueError(f"Unknown test case: {test_case_name}")

        test_case = self.test_cases[test_case_name]

        result = BenchmarkResult(
            test_case=test_case_name, iterations=iterations, successful_iterations=0
        )

        print(
            f"Running benchmark for test case '{test_case_name}' ({iterations} iterations)..."
        )

        # Detect if process_text is a coroutine function (async def)
        is_async = asyncio.iscoroutinefunction(
            self.orchestrator.process_text
        ) or inspect.iscoroutinefunction(self.orchestrator.process_text)

        for i in range(iterations):
            print(f"  Iteration {i + 1}/{iterations}")
            try:
                # Start metrics collection
                self.metrics_collector.start_pipeline()

                # Run the pipeline
                start_time = time.perf_counter()

                if is_async:
                    # Handle async process_text - we use a custom executor to run it
                    pipeline_result = await self.orchestrator.process_text(
                        test_case["text"]
                    )
                else:
                    # Handle synchronous process_text
                    pipeline_result = self.orchestrator.process_text(test_case["text"])

                end_time = time.perf_counter()

                # Record execution time
                execution_time_ms = (end_time - start_time) * 1000
                result.execution_times_ms.append(execution_time_ms)

                # Validate result
                self._validate_result(
                    test_case_name, pipeline_result, test_case["expected"]
                )

                # End metrics collection
                word_count = len(test_case["text"].split())
                self.metrics_collector.end_pipeline(True, word_count)

                # Get metrics report
                metrics_report = self.metrics_collector.get_metrics_report()
                result.metrics_reports.append(metrics_report)

                result.successful_iterations += 1
                print(f"    ✅ Completed in {execution_time_ms:.2f}ms")

            except Exception as e:
                print(f"    ❌ Failed: {str(e)}")
                result.errors.append(e)

                # End metrics collection (failed run)
                try:
                    word_count = len(test_case["text"].split())
                    self.metrics_collector.end_pipeline(False, word_count)
                    metrics_report = self.metrics_collector.get_metrics_report()
                    result.metrics_reports.append(metrics_report)
                except Exception:
                    pass

        return result

    def _validate_result(
        self, test_case_name: str, result: Dict[str, Any], expected: Dict[str, Any]
    ) -> None:
        """
        Validate that the pipeline result matches the expected output.

        Args:
            test_case_name: Name of the test case
            result: Actual result from the pipeline
            expected: Expected result from the test case

        Raises:
            AssertionError: If the result doesn't match the expected output
        """
        # Check that all expected anagrams are present with correct counts
        for anagram, count in expected["anagram_counts"].items():
            if anagram not in result["anagram_counts"]:
                raise AssertionError(f"Missing anagram '{anagram}' in result")

            if result["anagram_counts"][anagram] != count:
                raise AssertionError(
                    f"Anagram '{anagram}' count {result['anagram_counts'][anagram]} differs from expected {count}"
                )

    async def run_all_benchmarks(
        self, iterations: int = 3
    ) -> Dict[str, BenchmarkResult]:
        """
        Run benchmarks for all test cases.

        Args:
            iterations: Number of times to run each test case

        Returns:
            Dictionary mapping test case names to BenchmarkResult objects
        """
        results: Dict[str, BenchmarkResult] = {}

        for test_case_name in self.test_cases.keys():
            result = await self.run_benchmark(test_case_name, iterations)
            results[test_case_name] = result

        return results

    def print_benchmark_report(self, results: Dict[str, BenchmarkResult]) -> None:
        """
        Print a formatted report of benchmark results.

        Args:
            results: Dictionary mapping test case names to BenchmarkResult objects
        """
        print("\n" + "=" * 80)
        print("PIPELINE BENCHMARK REPORT")
        print("=" * 80)

        for test_case_name, result in results.items():
            print(f"\nTest Case: {test_case_name}")
            print("-" * 40)
            print(
                f"Success Rate: {result.success_rate * 100:.1f}% ({result.successful_iterations}/{result.iterations})"
            )
            print(
                f"Average Runtime: {result.average_runtime_ms:.2f}ms (±{result.stddev_runtime_ms:.2f}ms)"
            )
            print(
                f"Min/Max Runtime: {result.min_runtime_ms:.2f}ms / {result.max_runtime_ms:.2f}ms"
            )

            if result.metrics_reports:
                agg_metrics = result.get_aggregated_metrics()

                # Show throughput if available
                if (
                    "pipeline_metrics" in agg_metrics
                    and "avg_throughput_words_per_second"
                    in agg_metrics["pipeline_metrics"]
                ):
                    print(
                        f"Throughput: {agg_metrics['pipeline_metrics']['avg_throughput_words_per_second']:.2f} words/sec"
                    )

                # Show resource metrics
                if "resource_metrics" in agg_metrics:
                    rm = agg_metrics["resource_metrics"]
                    print(
                        f"Avg Peak Memory: {rm.get('avg_peak_memory_mb', 0):.2f}MB (Growth: {rm.get('avg_memory_growth_mb', 0):.2f}MB)"
                    )
                    print(f"Avg CPU Usage: {rm.get('avg_cpu_percent', 0):.2f}%")

                # Show task metrics
                if "task_metrics" in agg_metrics and agg_metrics["task_metrics"]:
                    print("\nTask Performance:")
                    print(
                        f"{'Task':<20} {'Success Rate':<15} {'Avg Time (ms)':<15} {'Avg Attempts':<15}"
                    )
                    print("-" * 80)

                    for task_name, metrics in agg_metrics["task_metrics"].items():
                        success_rate = f"{metrics['avg_success_rate'] * 100:.1f}%"
                        avg_time = f"{metrics['avg_execution_time_ms']:.2f}"
                        avg_attempts = f"{metrics['avg_attempts']:.2f}"

                        print(
                            f"{task_name:<20} {success_rate:<15} {avg_time:<15} {avg_attempts:<15}"
                        )

        print("\n" + "=" * 80)

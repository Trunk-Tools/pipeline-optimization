import gc
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class TaskMetrics:
    """Tracks metrics for an individual task"""

    name: str
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    total_execution_time: float = 0.0
    execution_times: List[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of this task"""
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts

    @property
    def average_execution_time(self) -> float:
        """Calculate the average execution time of successful task runs"""
        if self.successes == 0:
            return 0.0
        return self.total_execution_time / self.successes


class MetricsCollector:
    """
    Class for collecting and reporting pipeline metrics.

    This collects detailed metrics about task execution, pipeline performance,
    and resource usage to help candidates evaluate their optimizations.
    """

    def __init__(self) -> None:
        self.task_metrics: Dict[str, TaskMetrics] = defaultdict(
            lambda: TaskMetrics("unknown")
        )
        self.pipeline_start_time: Optional[float] = None
        self.pipeline_end_time: Optional[float] = None
        self.pipeline_runs: int = 0
        self.successful_runs: int = 0

        # Resource usage metrics
        self.initial_memory: float = 0.0
        self.peak_memory: float = 0.0
        self.cpu_utilization: List[float] = []

        # Performance metrics
        self.throughput_word_per_sec: List[float] = []

    def start_pipeline(self) -> None:
        """Record the start of a pipeline execution and capture initial resource usage"""
        self.pipeline_start_time = time.perf_counter()

        # Garbage collect to get more accurate memory measurement
        gc.collect()

        # Capture initial memory
        process = psutil.Process()
        self.initial_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB
        self.peak_memory = self.initial_memory

        # Reset per-pipeline metrics
        self.cpu_utilization = []

    def update_resource_metrics(self) -> None:
        """Update resource usage metrics during pipeline execution"""
        process = psutil.Process()

        # Update memory metrics
        current_memory = process.memory_info().rss / (1024 * 1024)  # Convert to MB
        self.peak_memory = max(self.peak_memory, current_memory)

        # Update CPU metrics
        current_cpu = process.cpu_percent(interval=0.1)
        self.cpu_utilization.append(current_cpu)

    def end_pipeline(self, success: bool, word_count: int) -> None:
        """Record the end of a pipeline execution"""
        if self.pipeline_start_time is None:
            raise ValueError("Pipeline end recorded before start")

        self.pipeline_end_time = time.perf_counter()
        self.pipeline_runs += 1

        if success:
            self.successful_runs += 1

            # Calculate throughput (words per second)
            duration = self.pipeline_end_time - self.pipeline_start_time
            if duration > 0 and word_count > 0:
                throughput = word_count / duration
                self.throughput_word_per_sec.append(throughput)

        # Final resource update
        self.update_resource_metrics()

    def record_task_execution(
        self, task_name: str, execution_time: float, attempts: int, success: bool
    ) -> None:
        """
        Record metrics for a task execution.

        Args:
            task_name: Name of the task
            execution_time: Time taken to execute the task (in seconds)
            attempts: Number of attempts before success or giving up
            success: Whether the task succeeded
        """
        metric = self.task_metrics[task_name]
        metric.name = task_name
        metric.attempts += attempts

        if success:
            metric.successes += 1
            metric.total_execution_time += execution_time
            metric.execution_times.append(execution_time)
        else:
            metric.failures += 1

    def get_metrics_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive metrics report.

        Returns:
            Dictionary containing metrics about pipeline and task execution
        """
        if self.pipeline_start_time is None or self.pipeline_end_time is None:
            return {"error": "No pipeline execution recorded"}

        # Calculate aggregated metrics
        total_pipeline_duration = self.pipeline_end_time - self.pipeline_start_time
        avg_throughput = (
            sum(self.throughput_word_per_sec) / len(self.throughput_word_per_sec)
            if self.throughput_word_per_sec
            else 0
        )

        # CPU utilization
        avg_cpu = (
            sum(self.cpu_utilization) / len(self.cpu_utilization)
            if self.cpu_utilization
            else 0
        )
        max_cpu = max(self.cpu_utilization) if self.cpu_utilization else 0

        # Memory usage
        memory_growth = self.peak_memory - self.initial_memory

        # Task metrics
        task_metrics = {}
        for task_name, metric in self.task_metrics.items():
            task_metrics[task_name] = {
                "success_rate": metric.success_rate,
                "average_execution_time_ms": metric.average_execution_time * 1000,
                "total_attempts": metric.attempts,
                "successes": metric.successes,
                "failures": metric.failures,
            }

        return {
            "pipeline_metrics": {
                "total_runtime_ms": total_pipeline_duration * 1000,
                "success_rate": self.successful_runs / self.pipeline_runs
                if self.pipeline_runs > 0
                else 0,
                "throughput_words_per_second": avg_throughput,
            },
            "resource_metrics": {
                "initial_memory_mb": self.initial_memory,
                "peak_memory_mb": self.peak_memory,
                "memory_growth_mb": memory_growth,
                "avg_cpu_percent": avg_cpu,
                "max_cpu_percent": max_cpu,
            },
            "task_metrics": task_metrics,
        }

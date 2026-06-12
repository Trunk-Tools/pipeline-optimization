# Benchmark Comparison Tool

Compare multiple `TaskOrchestrator` implementations side by side against the same test cases — useful for evaluating different optimization strategies.

## Quick Start

Run the baseline benchmark plus a comparison of everything in `benchmark_orchestrators/`:

```bash
./run_comparison.sh
```

Or run the comparison directly:

```bash
uv run compare-benchmarks --compare-dir benchmark_orchestrators
```

Options: `--test-case small|medium|large|all`, `--iterations N`, `--detailed`.

## Included Implementations

`benchmark_orchestrators/` contains sample orchestrators to compare:

- `inefficient_orchestrator.py` — the baseline
- `throughput_optimized.py` — tuned for throughput
- `memory_optimized.py` — tuned for memory use
- `async_optimized.py` — asyncio-based concurrency

## Adding Your Own

Drop a `.py` file in `benchmark_orchestrators/` that defines a `TaskOrchestrator` class with a `process_text(text_input: str) -> dict[str, Any]` method returning `{"runtime": <ms>, "anagram_counts": {...}}`.

## Metrics

- **Avg Runtime (ms)** — lower is better
- **Success Rate (%)** — higher is better
- **Throughput (words/sec)** — higher is better
- **Peak Memory (MB)** — lower is better
- **Avg CPU Usage (%)** — informational

The best value in each metric (except CPU) is highlighted.

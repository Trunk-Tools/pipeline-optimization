# Data Pipeline Optimization Exercise — Interviewer Guide

## Overview

This exercise evaluates how a candidate approaches a deliberately inefficient data pipeline: what they notice, how they prioritize, and how they reason about trade-offs. Relevant skills include concurrency, error handling/resilience, resource and algorithmic optimization, and performance tuning.

Plan for ~35-45 minutes of working time plus 5-10 minutes for the candidate's questions.

## Key Files

- `src/pipeline_optimization/orchestrator.py` — the inefficient implementation the candidate optimizes (the only file they should edit)
- `src/pipeline_optimization/tasks/` — task functions with intermittent random failures; framed to the candidate as external APIs they can't modify
- `src/pipeline_optimization/benchmarks/` — metrics and benchmarking logic
- `src/pipeline_optimization/cli/` — the `run_benchmark` and `compare_benchmarks` entry points
- `README.md` — what the candidate reads
- `example_solution.py` — one reference solution
- `benchmark_orchestrators/` — sample implementations for the comparison tool

## Running the Exercise

1. Have the candidate read `README.md` and the header in `orchestrator.py`.
2. Have them establish a baseline: `uv run benchmark --test-case small`
3. Let them optimize `orchestrator.py`, thinking out loud as they go.
4. Re-run `uv run benchmark` to measure the improvement.

We deliberately don't hand the candidate a checklist of problems — discovering and prioritizing the issues is part of the evaluation. You can help with syntax so it doesn't block their thinking; candidates should not use AI assistants.

## What to Look For

- **Problem identification** — Did they find the issues that matter by reading and running the code?
- **Prioritization** — Did they spend limited time on the highest-impact changes?
- **Reasoning** — Can they explain their trade-offs and their concurrency / caching / error-handling choices?
- **Reliability** — Does the solution stay correct and handle the random failures gracefully?
- **Code quality** — Clean, readable, and sensibly typed.

A strong solution typically shows a large runtime/throughput improvement, a near-100% success rate (vs. frequent failures in the baseline), and steadier memory use.

## Discussion Points

- What did you change, and why those things first?
- How did you choose your concurrency approach?
- What was your strategy for the failing tasks?
- What would you do with more time, or to make this production-ready?

## Reference Solution

`example_solution.py` shows one approach: module-level dictionary loading, async processing with bounded concurrency, retry with exponential backoff, `lru_cache`, `Counter`, and word deduplication. Candidates may take different but equally valid paths.

## Troubleshooting

- Use `--test-case small` if benchmarks run too slowly.
- For dependency issues, ensure they're using the `uv` environment (`uv sync`).

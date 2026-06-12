# Data Pipeline Optimization Exercise

Hi! Welcome to the data pipeline exercise. We'll work through this together — read the code, run it, and talk us through your thinking as you go.

We've built a small, made-up pipeline that:

1. Accepts a blob of text as input
2. Finds the unique anagrams in it and reports how many times words with those anagrams occur

For example, given the input "cat", the output should be:

```
{
  "act": 1,
  "cat": 1,
  "tac": 1
}
```

The current version lives in `src/pipeline_optimization/orchestrator.py`, and `resources/test_cases.json` holds the inputs it runs against — running `main` executes them for you.

Treat the task functions (`filter_input`, `get_words`, `find_anagrams`) as calls to external APIs you don't control and can't change.

Your task is to improve this pipeline however you see fit, so long as it keeps producing the same output. We're less interested in a checklist of fixes than in how you think about data pipelines:

- How efficient is it?
- How durable is it?
- How maintainable is it?
- How scalable is it?
- How testable is it?
- How observable is it?

## Getting Started

1. Install [uv](https://docs.astral.sh/uv/) (it sets up Python and the dependencies for you)
2. Clone this repo and `cd pipeline-optimization`
3. Run the pipeline on the small test case:
   ```
   uv run main --test-case small
   ```
   Use `--test-case small|medium|large|all` to pick which case(s) to run.

## Benchmarking

Measure the current implementation, then re-measure as you optimize:

```
uv run benchmark --test-case small
```

Flags: `--test-case`, `--iterations N`, `--detailed`. To compare several implementations side by side, see `README_COMPARISON.md`.

## Ground Rules

- **Only modify `src/pipeline_optimization/orchestrator.py`**
- **Don't modify anything in the `tasks/` directory**
- Keep the same output format and correctness
- Plan for ~35-45 minutes of work — we'll save the last 5-10 minutes for any questions you have

## What We're Looking For

- **Problem identification** – Did you find the issues that matter by reading and running the code?
- **Prioritization** – Did you focus your limited time on the things with the biggest impact?
- **Reasoning** – Can you explain your trade-offs and why you chose a given approach?
- **Reliability** – Does the pipeline still produce correct results and handle failures gracefully?
- **Code quality** – Is the implementation clean, readable, and a sensible use of Python?

Make one change at a time, measure its impact, and talk us through your thinking. Remember: a well-designed, reliable solution that's moderately faster beats a highly optimized but brittle one. Good luck!

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

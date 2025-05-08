import re

from pipeline_optimization.tasks.task_decorator import task


@task(failure_rate=0.1)
def filter_input(text_input: str):
    result = re.sub(r"-", " ", text_input)
    result = re.sub(r"[^a-zA-Z0-9\s]", "", result)
    return result

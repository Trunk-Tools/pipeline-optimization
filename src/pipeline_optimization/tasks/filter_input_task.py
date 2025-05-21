import re

from pipeline_optimization.tasks.task_decorator import task


@task(failure_rate=0.2, sleep_time=1)
async def filter_input(text_input: str):
    result = re.sub(r"-", " ", text_input)
    result = re.sub(r"[^a-zA-Z0-9\s]", "", result)
    return result

from pipeline_optimization.tasks.task_decorator import task


@task(failure_rate=0.25, sleep_time=1.0)
async def get_words(text_input: str):
    return text_input.split()

from pipeline_optimization.tasks.task_decorator import task


@task(failure_rate=0.1)
def get_words(text_input: str):
    return text_input.split()

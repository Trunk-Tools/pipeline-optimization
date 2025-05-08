import json

from pipeline_optimization.tasks.permutations_task import permutations
from pipeline_optimization.tasks.task_decorator import task

with open("src/pipeline_optimization/resources/english_dictionary.json") as file:
    english_dictionary = json.load(file)


@task(failure_rate=0.1)
def find_anagrams(word: str):
    perms = ["".join(p) for p in permutations(word)]
    anagrams = {}
    for p in perms:
        p_lower = p.lower()
        if p_lower in english_dictionary:
            anagrams[p_lower] = True

    return list(anagrams)

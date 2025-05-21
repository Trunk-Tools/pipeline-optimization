from pipeline_optimization.tasks.task_decorator import task


@task(failure_rate=0.01, sleep_time=0.1)
async def permutations(word: str):
    if len(word) == 0:
        return []
    if len(word) == 1:
        return [word]

    chars = list(word)

    perms = []
    for i in range(len(chars)):
        first_char = chars[i]
        tail = chars.copy()

        # Swap the first and ith character, then remove the first char
        tail[i] = chars[0]
        tail.pop(0)

        tail_perms = await permutations("".join(tail))

        for tail_perm in tail_perms:
            perms.append(first_char + tail_perm)

    return perms

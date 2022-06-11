# Running some tasks in separate processes and getiing their results
# as soon as each process finishes.

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import timedelta
from functools import partial
from time import perf_counter


def CountTo(num: int) -> str:
    startTime = perf_counter()
    idx = 0
    while idx < num:
        idx += 1
    finishedTime = perf_counter()
    duration = timedelta(seconds=(finishedTime - startTime))
    return f'Counting to {idx} took {duration}'


if __name__ == '__main__':
    COUNTS = [
        100_000,
        1_000_000,
        1_000,]
    with ProcessPoolExecutor(max_workers=6) as executor:
        countFutures = [
            executor.submit(CountTo, n)
            for n in COUNTS]

        for future in as_completed(countFutures):
            if future.cancelled():
                print('One task was cancelled.')
            elif future.done():
                print(future.result())
            else:
                print(future.exception())

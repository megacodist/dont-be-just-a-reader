"""In this module we create a number of coroutines, each of them sleeps
for the same amount of time and run them concurrently not sequentially.
"""

import asyncio
from datetime import timedelta
from time import perf_counter


async def WaitFor(dur: int) -> None:
    await asyncio.sleep(dur)


async def main_Thrd(num: int) -> None:
    startTime = perf_counter()
    results = await asyncio.gather(
        *(WaitFor(2) for _ in range(num)))
    print(results)
    duration = timedelta(
        seconds=(perf_counter() - startTime))
    print(duration)


if __name__ == '__main__':
    asyncio.run(main_Thrd(5))

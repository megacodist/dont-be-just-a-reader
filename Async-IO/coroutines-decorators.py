# This code snippet defines a decorator for coroutines.

import asyncio
from datetime import timedelta
from functools import wraps
from msvcrt import getwche
from time import perf_counter


def duration(coro):
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        startTime = perf_counter()
        result = await coro(*args, **kwargs)
        finishedTime = perf_counter()

        return result, timedelta(seconds=(finishedTime - startTime))
    
    return wrapper


@duration
async def SomeCoro() -> None:
    await asyncio.sleep(4)


async def main_coro() -> None:
    result, duration = await SomeCoro()
    print(result, duration)


if __name__ == '__main__':
    asyncio.run(main_coro())
    getwche()

# One of the use cases of asyncio.as_completed() is when we want to process
# each result one by one when it become available, not process or 'gather'
# all results at once.

# Keywords:
# asyncio, aiohttp, ClientSession, as_completed, duration,
# WindowsSelectorEventLoopPolicy

from multiprocessing.connection import wait
import aiohttp
from aiohttp import ClientSession
import asyncio
from datetime import timedelta
from random import random
import sys
from time import perf_counter


async def GetStatus(
        session: ClientSession,
        url: str,
        num: int
        ) -> tuple[int, int]:
    await asyncio.sleep(5 * random())
    async with session.get(url) as resp:
        return num, resp.status


async def main() -> None:
    startTime = perf_counter()
    async with aiohttp.ClientSession() as session:
        requests_ = [
            GetStatus(session, 'https://www.example.com/', idx)
            for idx in range(100)]
        for resp in asyncio.as_completed(requests_):
            try:
                res = await resp
                print(res)
            except Exception as err:
                print(err)
    finishedTime = perf_counter()

    print(timedelta(seconds=(finishedTime - startTime)))


if __name__ == '__main__':
    # Changing default event loop from Proactor to Selector on Windows...
    if sys.platform.startswith('win'):
        if sys.version_info[:2] >= (3, 8,):
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
    
    # Running the application...
    asyncio.run(main())

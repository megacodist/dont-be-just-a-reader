# One of the use cases of asyncio.gather(return_exceptions=True) is when
# we want to 'gather' and process all results at once, not one by one as
# they have completed.

# Keywords:
# asyncio, aiohttp, ClientSession, gather, duration, pprint, defaultdict,
# WindowsSelectorEventLoopPolicy

import aiohttp
from aiohttp import ClientSession
import asyncio
from collections import defaultdict
from datetime import timedelta
from pprint import pprint
import sys
from time import perf_counter


async def GetStatus(
        session: ClientSession,
        url: str,
        results: defaultdict
        ) -> None:
    async with session.get(url) as resp:
        results[resp.status] += 1


async def main() -> None:
    results = defaultdict(int)
    startTime = perf_counter()
    async with aiohttp.ClientSession() as session:
        tsks = (
            GetStatus(session, 'https://www.example.com/', results)
            for _ in range(1_000))
        await asyncio.gather(*tsks, return_exceptions=True)
    finishedTime = perf_counter()

    print(timedelta(seconds=(finishedTime - startTime)))
    pprint(results)


if __name__ == '__main__':
    # Changing default event loop from Proactor to Selector on Windows...
    if sys.platform.startswith('win'):
        if sys.version_info[:2] >= (3, 8,):
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
    
    # Running the application...
    asyncio.run(main())

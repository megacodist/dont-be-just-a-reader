# A good way of doing some I/O tasks
#
# One of the use cases of asyncio.as_completed() is when we want to process
# each result one by one when it become available, not process or 'gather'
# all results at once.

# Keywords:
# asyncio, aiohttp, ClientSession, as_completed, duration,
# WindowsSelectorEventLoopPolicy

import asyncio
import json
import sys
from datetime import timedelta
from random import random
import signal
from time import perf_counter

import aiohttp
from aiohttp import ClientSession


async def GetRandomText(
        session: ClientSession,
        num: int
        ) -> tuple[int, str]:
    await asyncio.sleep(8 * random())
    kwargs = {
        'url': 'https://api.deepai.org/api/text-generator',
        'data': {'text': 'intelligence',},
        'headers': {'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}}
    async with session.post(**kwargs) as resp:
        obj = await resp.text()
        obj = json.loads(obj)
        return num, obj['output']


async def main() -> None:
    global pending

    startTime = perf_counter()
    async with aiohttp.ClientSession() as session:
        pending.extend(
            asyncio.create_task(GetRandomText(session, idx))
            for idx in range(5))
        while pending:
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED)
            for tsk in done:
                if tsk.exception():
                    print(tsk.exception())
                else:
                    result_ = tsk.result()
                    print(f'Request no. {result_[0]}'.ljust(50, '='))
                    print(result_[1])
    finishedTime = perf_counter()

    print(timedelta(seconds=(finishedTime - startTime)))


if __name__ == '__main__':
    # Changing default event loop from Proactor to Selector on Windows...
    if sys.platform.startswith('win'):
        if sys.version_info[:2] >= (3, 8,):
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    loop.add_signal_handler(
        signal.SIGINT,
    )
    
    # Running the application...
    loop.run_until_complete(main())

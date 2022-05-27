# This code snippet shows that Async IO tasks in Pyhton starts and
# schedules from next await statement not from create_task function.

import asyncio
from datetime import datetime
from time import sleep


async def main_task() -> None:
    print('Task is started at', datetime.now().strftime('%H:%M:%S'))
    await asyncio.sleep(3)
    print('Task is finished at', datetime.now().strftime('%H:%M:%S'))


async def main_coro() -> None:
    print('main is started at', datetime.now().strftime('%H:%M:%S'))
    tsk = asyncio.create_task(main_task())
    sleep(5)
    await asyncio.sleep(1)
    print('main is finished at', datetime.now().strftime('%H:%M:%S'))
    await tsk


asyncio.run(main_coro())

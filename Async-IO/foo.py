# In Async IO you have to avoid time.sleep function because it blocks
# the application (remember Async IO apps have only one thread, one process).

import asyncio
from datetime import datetime
import signal
from time import sleep
from types import FrameType
from typing import Any


isCanceled: bool = False


def OnKeyboardInterrupt(
        signum: int,
        frame: FrameType = None
        ) -> Any:

    global isCanceled
    isCanceled = True


async def DoSomethingIntensive() -> None:
    for _ in range(1000):
        await asyncio.sleep(1)


async def main_coro() -> None:
    tsk = asyncio.create_task(DoSomethingIntensive())
    # Forcing the task to be scheduled...
    await asyncio.sleep(0.01)
    print('Task was started at', datetime.now().strftime('%H:%M:%S'))
    print('Press CNTRL + C to cancel.')
    duration = 0
    # not (isCanceled or tsk.done()) = (not isCanceled) and (not tsk.done())
    while not (isCanceled or tsk.done()):
        await asyncio.sleep(1)
        duration += 1
        print(' ' * 50, end='\r', flush=True)
        print(f'Elapsed {duration} seconds', end='\r', flush=True)


if __name__ == '__main__':
    signal.signal(
        signal.SIGINT,
        OnKeyboardInterrupt)
    asyncio.run(main_coro())

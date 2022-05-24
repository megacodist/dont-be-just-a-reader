import asyncio
import signal
import sys
from time import sleep
from types import FrameType
from typing import Any


def OnKeyboardInterrupt(signum: int, frame: FrameType) -> Any:
    print('Quiting...')
    sleep(2)

    sys.exit(0)


async def SomeCoroutine():
    pass


if __name__ == '__main__':
    signal.signal(
        signal.SIGINT,
        OnKeyboardInterrupt)
    loop = asyncio.get_event_loop()
    loop.run_forever()

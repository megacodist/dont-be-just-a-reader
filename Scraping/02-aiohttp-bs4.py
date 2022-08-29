"""This python module reads the planned python events from
https://python.org/events/python-events/. It uses aiohttp and asyncio
modules to grab data from the Web. Analyzing performs with bs4
(BeautifulSoup) in a subprocess (multiprocessing).
"""

import asyncio
from asyncio import Future as AsyncFuture
import sys
from asyncio import AbstractEventLoop
from concurrent.futures import CancelledError
from concurrent.futures import Future as ConFuture
from concurrent.futures import ProcessPoolExecutor
from threading import Thread
from time import sleep

from aiohttp import ClientSession
import attrs
from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import etree


@attrs.define
class EventInfo:
    date = attrs.field(default='')
    location = attrs.field(default='')
    title = attrs.field(default='')


class AsyncioThrd(Thread):
    """Instances of this class encapsulate an asyncio event loop on a
    thread. The procedure to use this API is to instantiate the class via
    its constructor and call 'StartAsyncioThrd' method.
    """
    def __init__(
            self,
            prcPool: ProcessPoolExecutor
            ) -> None:

        super().__init__(name='AsyncioThrd')
        self._running = True
        self._isReady = False
        """Specifies whether loop and prcPool attributes are initialized."""
        self.loop: AbstractEventLoop | None = None
        self.session: ClientSession | None = None
        """Specifies an HTTP session for current application."""
        self.prcPool = prcPool
        """Specifies a pool of processes for CPU-intensive tasks"""
    
    def StartAsyncioThrd(self) -> None:
        self.start()
        while not self._isReady:
            sleep(0.1)
    
    def run(self) -> None:
        # Changing default event loop from Proactor to Selector on Windows
        # OS and Python 3.8+...
        if sys.platform.startswith('win'):
            if sys.version_info[:2] >= (3, 8,):
                asyncio.set_event_loop_policy(
                    asyncio.WindowsSelectorEventLoopPolicy())

        while self._running:
            try:
                # Setting up the asyncio event loop...
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self._isReady = True
                self.loop.run_forever()
            # Catching asyncio-related errors here...
            finally:
                self.loop.close()
                self.prcPool.shutdown()
    
    def close(self) -> None:
        """Closes the thread and releases all associated resources."""
        # Because we definitely call this method from a thread other than
        # the thread initiated by run method, we call
        # self.loop.call_soon_threadsafe(self.loop.stop). But if we were
        # on the same thread, we must have called self.loop.stop()
        self._running = False
        self.loop.call_soon_threadsafe(self.loop.stop)
    
    def LoadPythonEvents(self) -> AsyncFuture[list[EventInfo]]:
        """Submits a coroutine to this asyncio event loop to load
        Python.org events page."""
        return asyncio.run_coroutine_threadsafe(
            self._LoadPythonEvents(),
            self.loop)

    async def _LoadPythonEvents(self) -> AsyncFuture[list[EventInfo]]:
        PY_EVENTS_URL = r'https://www.python.org/events/python-events/'
        # Reading Python events page...
        async with ClientSession() as self.session:
            async with self.session.get(PY_EVENTS_URL) as resp:
                html = await resp.text()
        # Processing events...
        # run_in_executor returns an asyncio.Future object
        # So it is awaitable
        return await self.loop.run_in_executor(
            self.prcPool,
            _ProcessPythonEvents,
            html)
    

def _ProcessPythonEvents(html: str) -> list[EventInfo]:
    events: list[EventInfo] = []
    bs = BeautifulSoup(html, 'lxml')
    eventsLIs: list[Tag] = bs.find(
        name='ul',
        attrs={'class': 'list-recent-events'}).findAll('li')
    for eventLI in eventsLIs:
        event = EventInfo()
        event.title = eventLI.find(class_='event-title').text
        event.date = eventLI.find('time').text
        event.location = eventLI.find(class_='event-location').text
        events.append(event)
    return events


def WaitUntilFuture(msg: str, future: AsyncFuture, nDots: int = 4) -> None:
    maxMsgLen = len(msg) + nDots
    while True:
        print(end='\r', flush=True)
        print(' ' * maxMsgLen, end='\r', flush=True)
        print(msg, end='', flush=True)
        for idx in range(nDots):
            print('.', end='', flush=True)
            sleep(0.5)
            if future.done():
                break
        else:
            continue
        break
    print(end='\r', flush=True)
    print(' ' * maxMsgLen, end='\r', flush=True)


def PrintResult(future: AsyncFuture) -> None:
    try:
        events: list[EventInfo] = future.result()
        for event in events:
            print(event.title.ljust(60, '='))
            print(f'\t{event.date}')
            print(f'\t{event.location}')
    except CancelledError:
        print('Cancelled')
    except Exception as err:
        print(f'An error occurred: {str(err)}')


if __name__ == '__main__':
    prcPool = ProcessPoolExecutor()

    asyncioThrd = AsyncioThrd(prcPool)
    asyncioThrd.StartAsyncioThrd()

    future = asyncioThrd.LoadPythonEvents()
    WaitUntilFuture('Loading', future)
    PrintResult(future)

    # Quitting the program...
    asyncioThrd.close()

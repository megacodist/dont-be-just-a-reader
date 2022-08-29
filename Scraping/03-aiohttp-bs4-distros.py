"""This python module reads the planned python events from
https://python.org/events/python-events/. It uses aiohttp and asyncio
modules to grab data from the Web. Analyzing performs with bs4
(BeautifulSoup) in a subprocess (multiprocessing).
"""

import asyncio
from asyncio import Future as AsyncFuture
import sys
from asyncio import AbstractEventLoop
from concurrent.futures import CancelledError, wait
from concurrent.futures import Future as ConFuture
from concurrent.futures import ProcessPoolExecutor
from threading import Thread, Event
from time import sleep

from aiohttp import ClientSession
import attrs
from bs4 import BeautifulSoup
from bs4.element import Tag
from lxml import etree

from megacodist.console import WaitPromptingThrd


@attrs.define
class DistroRank:
    rank: int = attrs.field(default=None)
    name: str = attrs.field(default='')


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
    
    def LoadDistroList(self) -> AsyncFuture[list[DistroRank]]:
        """Submits a coroutine to this asyncio event loop to load
        Python.org events page."""
        return asyncio.run_coroutine_threadsafe(
            self._LoadDistroList(),
            self.loop)

    async def _LoadDistroList(self) -> AsyncFuture[list[DistroRank]]:
        PY_EVENTS_URL = r'https://distrowatch.com/'
        # Reading Python events page...
        headers = {
            'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        async with ClientSession(headers=headers) as self.session:
            async with self.session.get(PY_EVENTS_URL) as resp:
                html = await resp.text()
        # Processing events...
        # run_in_executor returns an asyncio.Future object
        # So it is awaitable
        return await self.loop.run_in_executor(
            self.prcPool,
            _FindDistroList,
            html)
    

def _FindDistroList(html: str) -> list[DistroRank]:
    from lxml.etree import HTMLParser, fromstring, ElementBase

    htmlParser = HTMLParser()
    dom: ElementBase = fromstring(html, htmlParser)
    rankings: list[ElementBase] = dom.xpath(
        '//table[@class="News"]//tr[th[@class="phr1"] and td[@class="phr2"] and td[@class="phr3"]]')
    for idx in range(len(rankings)):
        distro = DistroRank()
        distro.rank = int(rankings[idx].xpath('th[@class="phr1"]/text()')[0])
        distro.name = rankings[idx].xpath('td[@class="phr2"]/a/text()')[0]
        temp = rankings[idx]
        rankings[idx] = distro
        del temp
    return rankings


def PrintResult(future: AsyncFuture) -> None:
    try:
        rankings: list[DistroRank] = future.result()
        for rank in rankings:
            print(f'{rank.rank}: {rank.name}')
    except CancelledError:
        print('Cancelled')
    except Exception as err:
        print(f'An error occurred: {str(err)}')


if __name__ == '__main__':
    prcPool = ProcessPoolExecutor()
    doneEvent = Event()
    waitingPrompt = WaitPromptingThrd(
        doneEvent,
        waitMsg='Looking up')

    asyncioThrd = AsyncioThrd(prcPool)
    asyncioThrd.StartAsyncioThrd()

    waitingPrompt.start()
    future = asyncioThrd.LoadDistroList()
    wait([future])
    doneEvent.set()
    waitingPrompt.join()
    PrintResult(future)

    # Quitting the program...
    asyncioThrd.close()

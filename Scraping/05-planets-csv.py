"""Reads information about planets of the solar system from
https://www.encyclopedia.com and save them into a CSV file in the folder
that this file lies.
"""


import asyncio
from asyncio import AbstractEventLoop, CancelledError
from asyncio import Future as AsyncFuture
from concurrent.futures import ProcessPoolExecutor, wait
import os
from pathlib import Path
from pprint import pprint
import sys
from threading import Event, Thread
from time import sleep

from aiohttp import ClientSession
import attrs
from megacodist.console import WaitPromptingThrd


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
    
    def SavePlanetsInfo(self, csvFile: Path | str) -> AsyncFuture[None]:
        """Submits a coroutine to this asyncio event loop to load
        Python.org events page."""
        return asyncio.run_coroutine_threadsafe(
            self._SavePlanetsInfo(csvFile),
            self.loop)

    async def _SavePlanetsInfo(
            self,
            csvFile: Path | str
            ) -> AsyncFuture[None]:
        import platform

        PLANETS_URL = (
            r'https://www.encyclopedia.com/reference/encyclopedias-almanacs-transcripts-and-maps/major-planets-solar-system-table')
        # Reading Python events page...
        pltfrm = platform.system_alias(
                platform.system(),
                platform.release(),
                platform.version())
        headers = {
            'User-Agent': (
                'Mozilla/5.0, '
                + f'({pltfrm}) '
                + (
                    '(compatible; planets-crawler; '
                    + '+https://github.com/megacodist/a-bit-more-of-an-interest)'))}
        async with ClientSession(headers=headers) as self.session:
            async with self.session.get(PLANETS_URL) as resp:
                html = await resp.text()
        # Processing events...
        # run_in_executor returns an asyncio.Future object
        # So it is awaitable
        return await self.loop.run_in_executor(
            self.prcPool,
            _ProcessPlanets,
            html,
            csvFile)


def _ProcessPlanets(html: str, csvFile: Path | str) -> None:
    import csv
    from lxml.etree import HTML, _ElementTree, _Element

    root: _Element = HTML(html)
    trs: list[_Element] = root.xpath(
        r'//div[contains(@class, "doccontentwrapper")]/table/tr')
    nInfos = max(len(tr.xpath('td')) for tr in trs)
    with open(csvFile, mode='wt', newline='') as csvFile:
        writer = csv.writer(csvFile)
        for tr in trs:
            tds = tr.xpath('td/text()')
            if len(tds) == nInfos:
                writer.writerow(tds)


if __name__ == '__main__':
    prcPool = ProcessPoolExecutor()
    doneEvent = Event()
    waitingPrompt = WaitPromptingThrd(
        doneEvent,
        waitMsg='Looking up')

    asyncioThrd = AsyncioThrd(prcPool)
    asyncioThrd.StartAsyncioThrd()

    # Suggeesting CSV file name...
    csvFile = Path(__file__).resolve().parent / 'planets.csv'

    waitingPrompt.start()
    future = asyncioThrd.SavePlanetsInfo(csvFile)
    wait([future])
    doneEvent.set()
    waitingPrompt.join()
    os.system(f'notepad.exe "{csvFile}"')

    # Quitting the program...
    asyncioThrd.close()

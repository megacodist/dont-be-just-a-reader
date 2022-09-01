"""
"""


import asyncio
from asyncio import AbstractEventLoop, CancelledError
from asyncio import Future as AsyncFuture
from concurrent.futures import ProcessPoolExecutor, wait
import sys
from threading import Event, Thread
from time import sleep

from aiohttp import ClientSession
import attrs
from megacodist.console import WaitPromptingThrd


@attrs.define
class PodInfo:
    title = attrs.field(default='')
    url = attrs.field(default='')
    category = attrs.field(default='')


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
    
    def LoadNprPods(self) -> AsyncFuture[list[PodInfo]]:
        """Submits a coroutine to this asyncio event loop to load
        Python.org events page."""
        return asyncio.run_coroutine_threadsafe(
            self._LoadNprPods(),
            self.loop)

    async def _LoadNprPods(self) -> AsyncFuture[list[PodInfo]]:
        PY_EVENTS_URL = (
            r'https://www.npr.org/podcasts/376087396/featured-npr-podcasts')
        # Reading Python events page...
        async with ClientSession() as self.session:
            async with self.session.get(PY_EVENTS_URL) as resp:
                html = await resp.text()
        # Processing events...
        # run_in_executor returns an asyncio.Future object
        # So it is awaitable
        return await self.loop.run_in_executor(
            self.prcPool,
            _ProcessPods,
            html)


def _ProcessPods(html: str) ->list[PodInfo]:
    from lxml.etree import fromstring, HTMLParser, _ElementTree, _Element
    htmlParser = HTMLParser()
    dom: _ElementTree = fromstring(html, htmlParser)
    pods: list[_Element] = dom.xpath(
        r'//article[contains(@class, "item") and  contains(@class, "item-podcast")]')
    infos: list[_Element] = []
    for pod in pods:
        podInfo = PodInfo()
        podInfo.title = pod.xpath(r'//h1[@class="title"]/a/text()')
        podInfo.url = pod.xpath(r'//h1[@class="title"]/a/@href')
        infos.append(podInfo)
    return infos


def PrintResult(future: AsyncFuture) -> None:
    try:
        infos: list[PodInfo] = future.result()
        for pod in infos:
            print(f'{pod.title}: {pod.url}')
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
    future = asyncioThrd.LoadNprPods()
    wait([future])
    doneEvent.set()
    waitingPrompt.join()
    PrintResult(future)

    # Quitting the program...
    asyncioThrd.close()

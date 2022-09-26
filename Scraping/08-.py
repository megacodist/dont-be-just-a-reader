
from asyncio import AbstractEventLoop
import asyncio
from concurrent.futures import ProcessPoolExecutor, wait
from pathlib import Path
from pprint import pprint
import sys
from threading import Thread, Event
from time import sleep

from aiohttp import ClientSession
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
        asyncio.run_coroutine_threadsafe(
            self._CreateSession(),
            self.loop)
    
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
        future = asyncio.run_coroutine_threadsafe(
            self.session.close(),
            self.loop)
        wait([future,])
        self.loop.call_soon_threadsafe(self.loop.stop)
    
    async def _CreateSession(self) -> None:
        self.session = ClientSession()
    
    def DownloadAudio(
            self,
            url: str,
            dir: str | Path
            ) -> None:
        return asyncio.run_coroutine_threadsafe(
            self._DownloadAudio(url, dir),
            self.loop)

    async def _DownloadAudio(
            self,
            url: str,
            dir: str | Path
            ) -> None:
        from yarl import URL
        from io import BytesIO
        from time import perf_counter

        filename = URL(url).path
        filename = Path(filename).name
        async with self.session.get(url, allow_redirects=True) as resp:
            length = resp.content_length
            startTime = perf_counter()
            with BytesIO() as buf:
                async for chunk, _ in resp.content.iter_chunks():
                    finishedTime = perf_counter()
                    duration = finishedTime - startTime
                    startTime = finishedTime
                    buf.write(chunk)
                    prog = round(len(buf.getvalue()) / length * 100, 2)
                    print(
                        prog,
                        f'{duration:.1E}',
                        len(chunk))
                with open(filename, mode='wb') as fileobj:
                    fileobj.write(buf.getvalue())


if __name__ == '__main__':
    URL = r'https://play.podtrac.com/npr-510351/edge1.pod.npr.org/anon.npr-podcasts/podcast/npr/dailyscience/2019/11/20191118_dailyscience_pandas-6c0c2bf1-255f-4765-b04f-84187a5faeeb.mp3?d=630&size=10064469&e=779777827&t=podcast&p=510351&awEpisodeId=779777827&awCollectionId=510351&sc=siteplayer&aw_0_1st.playerid=siteplayer'
    finished = Event()

    with ProcessPoolExecutor() as prcPool:
        asyncioThrd = AsyncioThrd(prcPool)
        asyncioThrd.StartAsyncioThrd()

        future = asyncioThrd.DownloadAudio(URL, 'aaa.mp3')
        wait([future,])
        print(future.result())

        asyncioThrd.close()

import aiohttp
import asyncio
from aiohttp import ClientSession
from datetime import datetime, time
import sys


async def main() -> None:
    async with ClientSession() as inetSession:
        kwargs = {
            'url': 'http://www.randomnumberapi.com/api/v1.0/random',
            'data': {
                'min': 100,
                'max': 1000,
                'count': 10}}
        async with inetSession.get(**kwargs) as resp:
            print(await resp.text())
    while True:
        await asyncio.sleep(1)
        print(datetime.now().strftime('%H:%M:%S'), end='\r')


if __name__ == '__main__':
    # Changing default event loop from Proactor to Selector on Windows...
    if sys.platform.startswith('win'):
        if sys.version_info[:2] >= (3, 8,):
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())

    # Running the application...
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.stop()
        # Do some cleaning up in here...
    finally:
        loop.close()

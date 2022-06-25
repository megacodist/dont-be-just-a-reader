import asyncio
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor

import requests


def GetStatusCode_Thrd(index: int, url: str) -> tuple[int, int]:
    resp = requests.get(url)
    return index, resp.status_code


async def main() -> None:
    EXAMPLE_COM = 'https://example.com/'
    THRDS_NUM = 300

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=THRDS_NUM/3) as thPool:
        resps = [
            loop.run_in_executor(
                thPool,   # we can use None for default executor
                GetStatusCode_Thrd,
                idx,
                EXAMPLE_COM)
            for idx in range(THRDS_NUM)]
        for future in as_completed(resps):
            result = await future
            try:
                print(result)
            except Exception:
                print(future.exception())


if __name__ == '__main__':
    asyncio.run(main())

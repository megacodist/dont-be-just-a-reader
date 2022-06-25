import asyncio
from asyncio import as_completed

import requests


def GetStatusCode_Thrd(index: int, url: str) -> tuple[int, int]:
    resp = requests.get(url)
    return index, resp.status_code


async def main() -> None:
    EXAMPLE_COM = 'https://example.com/'
    THRDS_NUM = 300
    loop = asyncio.get_running_loop()

    resps = [
        asyncio.to_thread(
            GetStatusCode_Thrd,
            idx,
            EXAMPLE_COM)
        for idx in range(THRDS_NUM)]
    for future in as_completed(resps):
        try:
            result = await future
            print(result)
        except Exception as err:
            print(err)


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
from queue import Queue
import requests
from threading import Thread


# Defining of global variables...
qStatusCode = Queue()


def GetStatusCode_Thrd(index: int, url: str) -> int:
    global qStatusCode

    resp = requests.get(url)
    qStatusCode.put((index, resp.status_code))


async def main() -> None:
    global qStatusCode
    EXAMPLE_COM = 'https://example.com/'
    THRDS_NUM = 300

    threads = [
        Thread(
            target=GetStatusCode_Thrd,
            args=(idx, EXAMPLE_COM,),
            name=f'thread no. {idx}')
        for idx in range(THRDS_NUM)]
    for thread in threads:
        thread.start()
    for idx in range(THRDS_NUM):
        index, statusCode = qStatusCode.get()
        print(f'Thread no. {index} returns {statusCode}')


if __name__ == '__main__':
    asyncio.run(main())

"""From SuperFastPython.com
"""

from concurrent.futures import ThreadPoolExecutor
from msvcrt import getwche
from queue import Queue
from random import random
from time import sleep


def main_rndm(num: int) -> None:
    global q
    sleep(random())
    q.put(num, block=True)


def main_program(
        max: int,
        use_async=False
        ) -> None:

    global q
    with ThreadPoolExecutor(max_workers=max) as executor:
        fs = executor.map(
            main_rndm,
            range(max))
    # By exiting the with, __exit__ will be called
    # In this case executor.shutdown()
    # Resulting waiti for all tasks to complete
    if use_async:
        while not q.empty():
            sleep(0.1)
            print(q.get())
    else:
        for future in fs:
            print(future)


if __name__ == '__main__':
    max = 100
    q = Queue(maxsize=max)
    main_program(max, use_async=True)
    getwche()

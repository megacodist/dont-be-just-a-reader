from concurrent.futures import ThreadPoolExecutor, Future
from msvcrt import getwche
import sys
from random import random
from threading import Lock
from time import sleep


# Module global variables...
MAX_WAIT = 3
# Using a Lock object as a means of synchronization to avoid
# interference when printing
printLock = Lock()


def PrintResult(future: Future):
    printLock.acquire()
    print(future.result())
    printLock.release()


def main_someThrd(num: int) -> int:
    sleep(MAX_WAIT * random())
    return num


def main_thrd():
    MAX_THRDS = 10

    # Creating threads...
    with ThreadPoolExecutor(max_workers=MAX_THRDS) as executor:
        fs = []
        for idx in range(MAX_THRDS):
            future = executor.submit(
                main_someThrd,
                idx)
            future.add_done_callback(PrintResult)
            fs.append(future)
    # with block shut the executor down automatically
    # So we did not have to


if __name__ == '__main__':
    while True:
        main_thrd()

        print(
            "Press 'Q' to quit, anything else to repeat: ",
            end='',
            flush=True)
        userChoice = getwche()
        if userChoice.lower() == 'q':
            sys.exit(0)

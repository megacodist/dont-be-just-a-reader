from concurrent.futures import ThreadPoolExecutor, as_completed
from msvcrt import getwche
import sys
from random import random
from time import sleep


# Module global variables...
MAX_WAIT = 3


def main_someThrd(num: int):
    sleep(MAX_WAIT * random())
    return num


def main_thrd():
    MAX_THRDS = 10

    with ThreadPoolExecutor(max_workers=MAX_THRDS) as executor:
        fs = [
            executor.submit(
                main_someThrd,
                idx)
            for idx in range(MAX_THRDS)]

        while len(fs):
            doneFs = as_completed(fs)
            if not doneFs:
                sleep(0.1)
                continue
            for future in doneFs:
                fs.remove(future)
                print(future.result())
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

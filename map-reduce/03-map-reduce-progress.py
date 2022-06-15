# This is a MapReduce problem with communication between subprocesses

import asyncio
from asyncio import Future
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.sharedctypes import Synchronized, Value
from pathlib import Path
from random import random
from time import sleep
from typing import Iterator


# Global variables...
procsFinished: Synchronized


def SplitBy(data: list[str], linesNum: int) -> Iterator[list[str]]:
    rangeIter = range(0, len(data), linesNum)
    prevIdx = 0
    for curIdx in rangeIter:
        yield data[prevIdx:curIdx]
        prevIdx = curIdx


def CountWords(entries: list[str]) -> dict[str, int]:
    global procsFinished

    sleep(random())
    wordsCount = defaultdict(int)
    for entry in entries:
        for word in entry.split():
            wordsCount[word] += 1
    with procsFinished.get_lock():
        procsFinished.value += 1
    return wordsCount


def InitProcs(sharedInt: Synchronized) -> None:
    global procsFinished
    procsFinished = sharedInt


async def ShowProgress(procsNum: int) -> None:
    global procsFinished

    print()
    print(end='\r')
    while procsFinished.value < procsNum:
        progress = procsFinished.value / procsNum * 100
        print(' ' * 20, end='\r', flush=True)
        print(f'Counting words: {progress:.2f}%', end='\r', flush=True)
        await asyncio.sleep(0.1)
    print('Counting words finished')


async def main() -> None:
    global procsFinished

    # Getting Google Books Unigram file from user...
    while True:
        unigramPath = input('Enter the path of Google Books Unigram file: ')
        if Path(unigramPath).is_file():
            break
        print('\tThe file does not exist.\n')
    
    # Loading Google Books Unigram file into RAM...
    with open(
            file=unigramPath,
            mode='rt',
            encoding='utf-8'
            ) as hUnigrams:
        UNIGRAMS = hUnigrams.readlines()

    procsFinished = Value('i', 0)
    loop = asyncio.get_running_loop()
    procs: list[Future] = []
    with ProcessPoolExecutor(
            initializer=InitProcs,
            initargs=(procsFinished,)
            ) as pPool:
        for chunck in SplitBy(UNIGRAMS, 100):
            procs.append(
                loop.run_in_executor(
                    pPool,
                    CountWords,
                    chunck))
        monitor = await asyncio.create_task(ShowProgress(len(procs)))


if __name__ == '__main__':
    asyncio.run(main())

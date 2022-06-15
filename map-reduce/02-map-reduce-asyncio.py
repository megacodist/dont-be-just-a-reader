# Google Books Unigram file is a text file with every entry on one line in
# the following format:
# <word>\t<year>\t<num_of_occurrences>\t<num_of_books>

import asyncio
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import Iterator


def SplitBy(data: list[str], linesNum: int) -> Iterator[list[str]]:
    rangeIter = range(0, len(data), linesNum)
    prevIdx = 0
    for curIdx in rangeIter:
        yield data[prevIdx:curIdx]
        prevIdx = curIdx


def CountWords(entries: list[str]) -> dict[str, int]:
    wordsCount = defaultdict()
    for entry in entries:
        word, _, count, _ = entry.split('\t')
        wordsCount[word] += count
    return wordsCount


async def main_coro() -> None:
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
    
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pPool:
        procs = []
        for chunck in SplitBy(UNIGRAMS, 20_000):
            procs.append(
                loop.run_in_executor(
                    pPool,
                    CountWords,
                    chunck))


if __name__ == '__main__':
    asyncio.run(main_coro())

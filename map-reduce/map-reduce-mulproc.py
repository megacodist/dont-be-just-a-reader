from concurrent.futures import Future, as_completed, wait
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED
from datetime import timedelta
from msvcrt import getwche
from pathlib import Path
from time import perf_counter

from utils import Partition, CountWords, MergeResults


def CountWords_Proc(text: str) -> dict[str, int]:
    return CountWords(text)


def MergeResultsSerially(tasks: list[Future]) -> dict[str, int]:
    wordsCount: dict[str, int] = {}
    for future in as_completed(tasks):
        wordsCount = MergeResults(
            wordsCount,
            future.result())
    return wordsCount


def MergeResultsInAllCores(
        pool: ProcessPoolExecutor,
        tasks: list[Future]
        ) -> dict[str, int]:
    """Merges intermediate results from counting processes into one
    dictionary by taking advantage of all CPU cores.
    """
    pending = tasks
    leftover = None
    while pending:
        done, pending = wait(
            pending,
            return_when=FIRST_COMPLETED)
        if leftover:
            done.add(leftover)
            leftover = None
        while len(done) >= 2:
            pending.add(
                pool.submit(
                    MergeResults,
                    done.pop().result(),
                    done.pop().result()))
        if done:
            leftover = done.pop()
    return leftover.result()


def main() -> None:
    # Getting a path to a text file from the user...
    while True:
        filepath = input('Specify a text file: ')
        if Path(filepath).is_file():
            break
        print('\nSomething is wrong with this file.')

    # Loading the dataset into the RAM...
    startTime = perf_counter()
    with open(
            file=filepath,
            mode='rt',
            encoding='utf-8'
            ) as fileobj:
        text = fileobj.read()
    finishedTime = perf_counter()
    loadDur = timedelta(seconds=(finishedTime - startTime))

    # Counting words in one process (CPU core)...
    startTime = perf_counter()
    countOneProc = CountWords(text)
    finishedTime = perf_counter()
    countOneProcDur = timedelta(seconds=(finishedTime - startTime))

    # Counting words across all CPU cores...
    for chunckSize in range(10, len(text) // 2):
        startTime = perf_counter()
        with ProcessPoolExecutor() as pPool:
            procs: list[Future] = []
            for chunck in Partition(text, chunckSize):
                procs.append(
                    pPool.submit(
                        CountWords_Proc,
                        chunck))

            # Merging (reducing) intermediate results from processes...
            # We could merge them using one process (core) serially by
            # countMulProc = MergeResultsSerially(procs)
            countMulProc = MergeResultsInAllCores(pPool, procs)
        finishedTime = perf_counter()
        countMulProcDur = timedelta(seconds=(finishedTime - startTime))

        # Reporting durations...
        print(f'\n\t Chunck size: {chunckSize} characters', '=' * 30)
        print('Loading data set duration:', loadDur)
        print('Counting words in one process:', countOneProcDur)
        print('Counting words across cores:', countMulProcDur)
        isEqual = (countOneProc == countMulProc)
        print('Do both methods have the same output?', isEqual)
        if not isEqual:
            # A bug found
            # Printing some useful information...
            extraMemOneProc = set(countOneProc) - set(countMulProc)
            extraMemMulProc = set(countMulProc) - set(countOneProc)
            print('Extra members in one process:', extraMemOneProc)
            print('Extra members in multiple processes:', extraMemMulProc)
            for key in countOneProc:
                if countOneProc[key] != countMulProc[key]:
                    print(f'{key} in one process is {countOneProc[key]} '
                          + f'and across processes is {countMulProc[key]}')
            print('Press any key to continue', end='', flush=True)
            getwche()


if __name__ == '__main__':
    main()

from concurrent.futures import Future, as_completed
from concurrent.futures import ALL_COMPLETED, ProcessPoolExecutor
from utils import Partition, CountWords, MergeResults


def CountWords_Proc(text: str) -> dict[str, int]:
    return CountWords(text)


def MergeResults_Proc(
        a: dict[str, int],
        b: dict[str, int]
        ) -> dict[str, int]:
    return MergeResults(a, b)


def main() -> None:
    with open(
            r'H:\stackoverflow-14359906.txt',
            mode='rt',
            encoding='utf-8'
            ) as fileobj:
        text = fileobj.read()
    with ProcessPoolExecutor() as pPool:
        procs: list[Future] = []
        for chunck in Partition(text, 1_000):
            procs.append(
                pPool.submit(
                    CountWords_Proc,
                    chunck))

        wordsCount = {}
        for future in as_completed(procs):
            temp = future.result()
            wordsCount = future.result()


if __name__ == '__main__':
    main()

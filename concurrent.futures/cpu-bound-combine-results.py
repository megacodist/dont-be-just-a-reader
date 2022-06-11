# If we have some CPU-bound tasks to perform and the results of these
# tasks can be combined out of order, we can do it with the following
# procedurr.

from concurrent.futures import ProcessPoolExecutor, wait
from random import random
from time import sleep


def DoCpuBoundTask() -> None:
    a = 5 * random()
    sleep(a)
    print(a)
    return a


def CombineResults(
        num1: float,
        num2: float
        ) -> float:
    sleep(5* random())
    return num1 + num2


def main(n: int):
    with ProcessPoolExecutor(max_workers=n) as pPool:
        # Delegating some tasks to child processes...
        pending = [
            pPool.submit(DoCpuBoundTask)
            for _ in range(n)]
        
        # Combining results out of order...
        reserved = None
        while pending:
            done, pending = wait(
                pending,
                timeout=0.1)
            if reserved:
                done.add(reserved)
                reserved = None
            while len(done) >= 2:
                pending.add(
                    pPool.submit(
                        CombineResults,
                        done.pop().result(),
                        done.pop().result()))
            if done:
                reserved = done.pop()
        
        print(reserved.result())


if __name__ == '__main__':
    main(20)

# If we have some CPU-bound tasks to perform and the results of these
# tasks can be combined out of order, we can do it with the following
# procedure.
#
# Pay special attention to max_worker parameter of ProcessPoolExecutor.
# If you do not specify this parameter, the default is the number of cores
# of your CPU or the number of threads of your CPU if your CPU supports
# Intel® Hyperthreading or AMD® Simultaneous Multithreading or any similar
# technology. This is good when some CPU-bound tasks must be done and
# switching between them does not provide any benefit. Instead the overhead
# of context switch might increase the total time.

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
        leftover = None
        while pending:
            done, pending = wait(
                pending,
                timeout=0.1)
            if leftover:
                done.add(leftover)
                leftover = None
            while len(done) >= 2:
                pending.add(
                    pPool.submit(
                        CombineResults,
                        done.pop().result(),
                        done.pop().result()))
            if done:
                leftover = done.pop()
        
        print(leftover.result())


if __name__ == '__main__':
    main(20)

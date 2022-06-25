# When we are using ThreadPoolExecutor, it is vitally important to set
# max_worker parameter to an optimal value, that is if we set it to a small
# integer I/O-bouns tasks might wait long for previous tasks to complete
# and thus the execution time will be increased. If max_worker is to big,
# lots of OS resources will get involved and performance degrades.

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def GetStatusCode_Thrd(index: int, url: str) -> tuple[int, int]:
    resp = requests.get(url)
    return index, resp.status_code


def main() -> None:
    EXAMPLE_COM = 'https://example.com/'
    THRDS_NUM = 300

    with ThreadPoolExecutor(max_workers=(THRDS_NUM/4)) as thPool:
        resps = [
            thPool.submit(GetStatusCode_Thrd, idx, EXAMPLE_COM)
            for idx in range(THRDS_NUM)]
        for future in as_completed(resps):
            if future.done():
                print(future.result())
            else:
                print(future.exception())


if __name__ == '__main__':
    main()
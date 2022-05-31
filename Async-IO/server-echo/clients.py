from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from random import randrange
from requests import Session
import socket


def GetARandomText(session: Session) -> str:
    resp = session.post(
        url='https://api.deepai.org/api/text-generator',
        data={'text': 'intelligence',},
        headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'})
    obj = json.loads(resp.text)
    return obj['output']


def _GetRandomPort() -> int:
    testSock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    portStatus = 0
    while not portStatus:
        # Getting a random port...
        port = randrange(1024, 65535)
        portStatus = testSock.connect_ex(
            ('127.0.0.1', port,))
    return port


def proc_main(port: int) -> None:
    session = Session()

    numConn = randrange(1, 2)
    procSock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    procSock.connect(
            ('127.0.0.1', 8008,))
    with procSock:
        for _ in range(numConn):
            randomText = GetARandomText(session)
            procSock.sendall(randomText.encode())


def main() -> None:
    maxProcs = randrange(10, 20)
    with ProcessPoolExecutor(max_workers=maxProcs) as executor:
        procs = []
        for _ in range(maxProcs):
            procs.append(
                executor.submit(
                    proc_main,
                    _GetRandomPort()))
    
    as_completed(procs)


if __name__ == '__main__':
    main()

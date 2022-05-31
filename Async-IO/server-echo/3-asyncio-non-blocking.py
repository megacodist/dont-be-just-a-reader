import asyncio
from collections import deque, namedtuple
from dataclasses import dataclass
import os
import signal
import socket
import sys
from types import FrameType


# Defining of required types...
Host = namedtuple(
    'Host',
    'ip, port')

@dataclass
class ConnectionInfo:
    socket: socket.socket
    data: bytes


# Defining global variables...
loop = None
toQuit: bool = False
connections: dict[Host, ConnectionInfo] = {}


def _OnKeyboardInterrupt(
        signum: int,
        frame: FrameType | None = None
        ) -> None:

    global toQuit
    if not toQuit:
        toQuit = True
    else:
        sys.exit(0)


async def ShowStatus() -> None:
    global connections

    os.system('cls')
    if connections:
        print(f'Connections number: {len(connections)}')
        for key in connections:
            print('-' * 50)
            print(f'Host: {key}')
            print(f'Data: {connections[key].data}')
    else:
        print('No connection')


async def ReadData(sock: socket.socket) -> None:
    global connections
    global loop

    sock.setblocking(False)
    sock.settimeout(0.1)
    try:
        q = deque()
        while True:
            try:
                dataPart = await loop.sock_recv(sock, 1024)
                if not dataPart:
                    break
                q.append(dataPart)
            except socket.error:
                break
        connections[sock.getpeername()].data = b''.join(q)
    finally:
        sock.close()


async def CheckConnections() -> None:
    global connections
    global serverSock

    # Creating a shallow copy...
    conns = {**connections}

    for key in conns:
        try:
            serverSock.connect(key)
        except Exception:
            del connections[key]


async def main() -> None:
    global loop
    global serverSock
    global connections

    loop = asyncio.get_running_loop()
    while not toQuit:
        await ShowStatus()
        clientSock, clientHost = await loop.sock_accept(serverSock)
        connections[clientHost] = ConnectionInfo(
            clientSock,
            bytes())
        await ReadData(clientSock)


if __name__ == '__main__':
    # Setting keyboard interrupt handler...
    signal.signal(
        signal.SIGINT,
        _OnKeyboardInterrupt)

    # Configuring the server socket...
    # Setting family address to IPv4 & protocol to TCP...
    serverSock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    # Using non-blocking socket...
    serverSock.setblocking(False)
    serverSock.settimeout(0.1)
    # Binding IP and port to the socket...
    serverSock.bind(('127.0.0.1', 8008,))
    # Accepting up to 200 connections...
    serverSock.listen(200)

    asyncio.run(main())

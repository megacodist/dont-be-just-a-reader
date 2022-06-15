import asyncio
from collections import namedtuple
from dataclasses import dataclass
import os
import socket
import signal
import sys
from threading import Thread
from types import FrameType


# Defining of required types...
Host = namedtuple(
    'Host',
    'ip, port')

@dataclass
class ConnectionInfo:
    socket: socket.socket
    thread: Thread
    data: bytes


# Defining global variables...
SERVER_SOCK: socket.socket
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


def ReadSocket_Thrd(clientIP: Host) -> None:
    global connections
    while True:
        try:
            connections[clientIP].data = connections[
                clientIP].socket.recv(2024)
        except BlockingIOError:
            pass
        except socket.error:
            break


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


async def ListenForConnection() -> None:
    global connections

    try:
        clientSock, host = SERVER_SOCK.accept()
        thread = Thread(
            target=ReadSocket_Thrd,
            args=(host,),
            name=f'Reading {host}')
        connections[host] = ConnectionInfo(
            clientSock,
            thread,
            None)
        thread.start()
    except BlockingIOError:
        await asyncio.sleep(0.1)


async def main() -> None:
    while not toQuit:
        await ShowStatus()
        await ListenForConnection()


if __name__ == '__main__':
    # Setting keyboard interrupt handler...
    signal.signal(
        signal.SIGINT,
        _OnKeyboardInterrupt)

    # Configuring the server socket...
    # Setting family address to IPv4 & protocol to TCP...
    SERVER_SOCK = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    # Using non-blocking socket...
    SERVER_SOCK.setblocking(False)
    # Binding IP and port to the socket...
    SERVER_SOCK.bind(('127.0.0.1', 8008,))
    # Accepting up to 200 connections...
    SERVER_SOCK.listen(200)

    asyncio.run(main())

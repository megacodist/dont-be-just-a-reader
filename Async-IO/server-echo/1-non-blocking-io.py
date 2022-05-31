# This script acts as a server and accepts connections from other
# sockets on the network and read the sent data. It has a bad
# artitechture because it waits in a loop and as a result stresses
# processing resources.
#
# Keywords:
# signal, socket, dataclass, namedtuple, asyncio

import asyncio
from collections import namedtuple
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


async def ListenForConnection() -> None:
    global connections

    try:
        clientSoc, host = serverSoc.accept()
        connections[host] = ConnectionInfo(
            socket=clientSoc,
            data=bytes())
        await ReadSocket(host)
    except BlockingIOError:
        await asyncio.sleep(0.1)


async def ReadSocket(host: Host) -> None:
    global connections

    connections[host].socket.setblocking(False)
    while True:
        dataPart = None
        try:
            dataPart = connections[host].socket.recv(1024)
        except socket.error:
            break
        if not dataPart:
            break
        connections[host].data = connections[host].data + dataPart


async def CheckConnections() -> None:
    global connections

    for key in connections:
        if not connections[key].socket:
            del connections[key]


async def main() -> None:
    while not toQuit:
        await ShowStatus()
        await ListenForConnection()
        await CheckConnections()


if __name__ == '__main__':
    # Setting keyboard interrupt handler...
    signal.signal(
        signal.SIGINT,
        _OnKeyboardInterrupt)

    # Configuring the server socket...
    # Setting family address to IPv4 & protocol to TCP...
    serverSoc = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)
    # Using non-blocking socket...
    serverSoc.setblocking(False)
    # Binding IP and port to the socket...
    serverSoc.bind(('127.0.0.1', 8008,))
    # Accepting up to 200 connections...
    serverSoc.listen(200)

    asyncio.run(main())

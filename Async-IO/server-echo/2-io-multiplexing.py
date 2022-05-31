import asyncio
from collections import namedtuple
from dataclasses import dataclass
from email.headerregistry import Address
from multiprocessing import connection
import os
from selectors import DefaultSelector, EVENT_READ
import signal
import socket
import sys
from threading import Lock
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


def ShowStatus() -> None:
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


def ReadData(sock: socket.socket) -> None:
    global connections
    global selector

    while True:
        try:
            connections[sock.getpeername()].socket.setblocking(False)
            dataPart = connections[sock.getpeername()].socket.recv(1024)
            if dataPart:
                dataPart = connections[sock.getpeername()].data + dataPart
                connections[sock.getpeername()].data = dataPart
            else:
                # No data was received, closing the connection...
                selector.unregister(connections[sock.getpeername()].socket)
                connections[sock.getpeername()].socket.close()
        except socket.error:
            break


def AcceptConnection(serverSock: socket.socket) -> None:
    global selector
    global connections

    conn, host = serverSock.accept()
    connections[host] = ConnectionInfo(
        conn,
        b'')
    selector.register(
        conn,
        EVENT_READ,
        ReadData)


def main() -> None:
    global toQuit
    global selector

    while not toQuit:
        ShowStatus()
        events = selector.select(timeout=0.2)
        for key, mask in events:
            if mask == EVENT_READ:
                callback = key.data
                callback(key.fileobj)


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
    # Binding IP and port to the socket...
    serverSock.bind(('127.0.0.1', 8008,))
    # Accepting up to 200 connections...
    serverSock.listen(200)

    # Configuring I/O multiplexing...
    selector = DefaultSelector()
    selector.register(
        serverSock,
        EVENT_READ,
        AcceptConnection)
    
    # Starting application...
    main()

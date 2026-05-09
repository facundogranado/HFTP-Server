# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
import os
from base64 import b64encode

from constants import (
    BAD_EOL,
    BAD_OFFSET,
    BAD_REQUEST,
    CODE_OK,
    COMMANDS,
    CONTENT_LENGTH_PREFIX,
    FILE_NOT_FOUND,
    INTERNAL_ERROR,
    INVALID_ARGUMENTS,
    INVALID_COMMAND,
    error_messages,
)


class Connection:

    def __init__(self, sock: socket.socket, directory: str) -> None:
        self.sock = sock
        self.directory = directory
        self.alive = True

    def handle(self) -> None:
        buffer = ""

        try:
            while self.alive:
                data = self.sock.recv(1024)
                if not data:
                    break

                chunk = data.decode()
                combined = buffer + chunk

                for i in range(len(combined)):
                    if combined[i] == "\n":
                        if i == 0 or combined[i - 1] != "\r":
                            self.sock.sendall(f"{BAD_EOL} {error_messages[BAD_EOL]}\r\n".encode())
                            self.alive = False
                            return

                buffer = combined

                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    command_line = line.strip()

                    if not command_line:
                        self.sock.sendall(f"{BAD_REQUEST} {error_messages[BAD_REQUEST]}\r\n".encode())
                        self.alive = False
                        break

                    parts = command_line.split()
                    command = parts[0]

                    if not parts:
                        self.sock.sendall(f"{BAD_REQUEST} {error_messages[BAD_REQUEST]}\r\n".encode())
                        self.alive = False
                        break

                    if command == "help":
                        self.handle_help(parts)
                    elif command == "quit":
                        self.handle_quit(parts)
                    elif command == "get_file_listing":
                        self.handle_listing(parts)
                    elif command == "get_metadata":
                        self.handle_metadata(parts)
                    elif command == "get_slice":
                        self.handle_slice(parts)
                    else:
                        self.sock.sendall(f"{INVALID_COMMAND} {error_messages[INVALID_COMMAND]}\r\n".encode())

        except Exception:
            try:
                self.sock.sendall(f"{INTERNAL_ERROR} {error_messages[INTERNAL_ERROR]}\r\n".encode())
            except Exception:
                pass
        finally:
            self.sock.close()

    def handle_help(self, parts):
        if len(parts) != 1:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        res = f"{CODE_OK} {error_messages[CODE_OK]}\r\n"
        for command in COMMANDS:
            res += f"{command}\r\n"
        res += "\r\n"
        self.sock.sendall(res.encode())

    def handle_quit(self, parts):
        if len(parts) != 1:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        self.sock.sendall(f"{CODE_OK} {error_messages[CODE_OK]}\r\n".encode())
        self.alive = False

    def handle_listing(self, parts):
        if len(parts) != 1:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        files = os.listdir(self.directory)
        files.sort()

        response = f"{CODE_OK} {error_messages[CODE_OK]}\r\n"
        for file in files:
            response += file + "\r\n"
        response += "\r\n"

        self.sock.sendall(response.encode())

    def handle_metadata(self, parts):
        if len(parts) != 2:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        filename = parts[1]
        path = os.path.join(self.directory, filename)

        if not os.path.isfile(path):
            self.sock.sendall(f"{FILE_NOT_FOUND} {error_messages[FILE_NOT_FOUND]}\r\n".encode())
            return

        size = os.path.getsize(path)
        response = f"{CODE_OK} {error_messages[CODE_OK]}\r\n{size}\r\n"
        self.sock.sendall(response.encode())

    def handle_slice(self, parts):
        if len(parts) < 4 or len(parts) > 5:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        filename = parts[1]
        path = os.path.join(self.directory, filename)

        if not os.path.isfile(path):
            self.sock.sendall(f"{FILE_NOT_FOUND} {error_messages[FILE_NOT_FOUND]}\r\n".encode())
            return

        try:
            offset = int(parts[2])
            size = int(parts[3])
        except ValueError:
            self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
            return

        is_raw = False
        if len(parts) == 5:
            if parts[4] == "raw":
                is_raw = True
            else:
                self.sock.sendall(f"{INVALID_ARGUMENTS} {error_messages[INVALID_ARGUMENTS]}\r\n".encode())
                return

        file_size = os.path.getsize(path)

        if offset < 0 or size < 0 or offset + size > file_size:
            self.sock.sendall(f"{BAD_OFFSET} {error_messages[BAD_OFFSET]}\r\n".encode())
            return

        with open(path, "rb") as file:
            file.seek(offset)
            data = file.read(size)

        header = f"{CODE_OK} {error_messages[CODE_OK]}\r\n"
        self.sock.sendall(header.encode())

        if is_raw:
            raw_header = f"{CONTENT_LENGTH_PREFIX} {size}\r\n\r\n"
            self.sock.sendall(raw_header.encode())
            self.sock.sendall(data)
        else:
            payload = b64encode(data).decode("ascii")
            self.sock.sendall(f"{payload}\r\n".encode())

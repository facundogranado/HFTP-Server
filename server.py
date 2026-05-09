#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import argparse
import socket
import sys
import connection
import threading
from constants import DEFAULT_ADDR, DEFAULT_DIR, DEFAULT_PORT


class Server:
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(
        self,
        addr: str = DEFAULT_ADDR,
        port: int = DEFAULT_PORT,
        directory: str = DEFAULT_DIR,
    ) -> None:
        print(f"Serving {directory} on {addr}:{port}.")
        self.addr = addr
        self.port = port
        self.directory = directory

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((addr, port))
        self.socket.listen(5)
        # FALTA: Crear socket del servidor, configurarlo, asignarlo
        # a una dirección y puerto, etc.

    def serve(self) -> None:
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        while True:
            client_socket, client_addr = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()
            # FALTA: Aceptar una conexión al server, crear una
            # Connection para la conexión y atenderla hasta que termine.

    def handle_client(self, client_socket: socket.socket) -> None:
        conn = connection.Connection(client_socket, self.directory)
        conn.handle()

def main() -> None:
    """Parsea los argumentos y lanza el server"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar",
        type=int,
        default=DEFAULT_PORT,
    )
    parser.add_argument(
        "-a", "--address",
        help="Dirección donde escuchar",
        default=DEFAULT_ADDR,
    )
    parser.add_argument(
        "-d", "--datadir",
        help="Directorio compartido",
        default=DEFAULT_DIR,
    )
    args = parser.parse_args()
    try:
        server = Server(args.address, args.port, args.datadir)
        server.serve()
    except OSError as e:
        sys.stderr.write(f"Error al iniciar el servidor: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

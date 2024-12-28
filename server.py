import threading
import socket
import argparse
import os
import sys

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        # AF_INET = Address Family, SOCK_STREAM = TCP socket type
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse old socket
        sock.bind((self.host, self.port))
        sock.listen(1)  # TCP uses listening sockets
        print("Listening at ", sock.getsockname())

        # Accept new connections
        while True:
            sc, sockname = sock.accept()
            print(f"Accepted new connection from {sc.getpeername()} to {sc.getsockname()}")

            # Create and start a new thread
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()

            # Add thread to active connections
            self.connections.append(server_socket)

            print("Ready to receive messages from ", sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections[:]:  # Iterate over a copy of the list
            if connection.sockname != source:
                try:
                    connection.send(message)
                except (ConnectionResetError, BrokenPipeError):
                    print(f"Error sending message to {connection.sockname}. Removing connection.")
                    self.remove_connection(connection)

    def remove_connection(self, connection):
        self.connections.remove(connection)

class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc  # Connected socket
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode('ascii')
                if message:

                    print(f"{self.sockname} says {message}")
                    self.server.broadcast(message, self.sockname)
                else:
                    print(f"{self.sockname} has closed the connection")
                    self.server.remove_connection(self)
                    self.sc.close()
                    break
            except (ConnectionResetError, BrokenPipeError):
                print(f"{self.sockname} has forcibly closed the connection")
                self.server.remove_connection(self)
                self.sc.close()
                break

    def send(self, message):
        try:
            self.sc.sendall(message.encode('ascii'))
        except (ConnectionResetError, BrokenPipeError):
            print(f"Failed to send message to {self.sockname}.")
            self.server.remove_connection(self)


def server_exit(server):
    while True:
        try:
            ipt = sys.stdin.read(1)  # Read one character at a time
            if ipt.strip() == 'q':   # Strip any newline or extra spaces
                print("Closing all connections...")
                for connection in server.connections:
                    connection.sc.close()
                print("Shutting down the server...")
                sys.exit(0)
        except Exception as e:
            print(f"Error in server_exit: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', nargs='?', default='localhost', help="Interface the server listens at")
    parser.add_argument('-p', metavar='PORT', type=int, default=5050, help='TCP port (default 5050)')

    args = parser.parse_args()

    # Set host to localhost and IP to 0.0.0.0
    args.host = 'localhost'
    args.p = 5050

    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()

    # Create and start the exit thread
    exit_thread = threading.Thread(target=server_exit, args=(server,))
    exit_thread.start()

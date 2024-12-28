import threading
import socket
import argparse
import os
import sys
import tkinter as tk


class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        # Listen for user input and send to server
        while True:
            try:
                message = input(f"{self.name}: ")
                # Exit chatroom if user types 'QUIT'
                if message.strip() == "QUIT":
                    self.sock.sendall(f"server: {self.name} has left the chat.".encode('ascii'))
                    break
                else:
                    self.sock.sendall(f"{self.name}: {message}".encode('ascii'))
            except (ConnectionAbortedError, ConnectionResetError):
                print("Connection to server lost. Exiting...")
                break
        print("\nQuitting...")
        self.sock.close()
        sys.exit(0)


class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        # Listen for incoming messages from the server
        while True:
            try:
                message = self.sock.recv(1024).decode('ascii')
                if message:
                    if self.messages:
                        self.messages.insert(tk.END, message)
                    else:
                        print(f"\r{message}")
                else:
                    print("\nConnection to server lost. Exiting...")
                    break
            except (ConnectionAbortedError, ConnectionResetError):
                print("\nConnection to server lost. Exiting...")
                break
        self.sock.close()
        sys.exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):
        # Establish connection to server
        try:
            print(f"Trying to connect to {self.host}:{self.port}")
            self.sock.connect((self.host, self.port))
            print(f"Successfully connected to {self.host}:{self.port}\n")
        except (ConnectionRefusedError, OSError):
            print(f"Unable to connect to {self.host}:{self.port}. Exiting...")
            sys.exit(1)

        self.name = input("Your name: ").strip()
        print(f"\nWelcome, {self.name}! Preparing to send and receive messages...\n")

        # Create and start threads for sending and receiving messages
        send = Send(self.sock, self.name)
        receive = Receive(self.sock, self.name)

        send.start()
        receive.start()

        self.sock.sendall(f"server: {self.name} has joined the chat. Say hi!".encode('ascii'))
        print("\rReady! Leave the chatroom anytime by typing 'QUIT'\n")
        return receive

    def send(self, textInput):
        # Send text from GUI input to the server
        message = textInput.get().strip()
        textInput.delete(0, tk.END)

        if self.messages:
            self.messages.insert(tk.END, f"{self.name}: {message}")

        if message == "QUIT":
            self.sock.sendall(f"server: {self.name} has left the chat.".encode('ascii'))
            print("\nQuitting...")
            self.sock.close()
            sys.exit(0)
        else:
            self.sock.sendall(f"{self.name}: {message}".encode('ascii'))


def main(host, port):
    # Initialize and run the GUI application
    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title("Chatroom")

    # Message display frame
    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    client.messages = messages
    receive.messages = messages
    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")

    # Message input frame
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)
    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Write your message here.")

    btnSend = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send(textInput)
    )
    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, pady=10, sticky="ew")

    # Configure window layout
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom Client")
    parser.add_argument('host', help="Server IP or hostname")
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help="Server TCP port (default 1060)")

    args = parser.parse_args()

    main(args.host, args.p)

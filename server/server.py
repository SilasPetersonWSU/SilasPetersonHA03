import socket
import threading
import os

# Server setup
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345
BUFFER_SIZE = 1024

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)
print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

clients = []

# Broadcast messages to all connected clients
def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

# Handle incoming client messages and file uploads
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break

            # Check if it's a file upload request
            if message.startswith("UPLOAD"):
                _, file_name = message.split(" ")
                receive_file(client_socket, file_name)
            else:
                print(f"Client: {message}")
                broadcast(message.encode(), client_socket)
        except:
            clients.remove(client_socket)
            break

# Function to receive file from a client
def receive_file(client_socket, file_name):
    with open(file_name, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if bytes_read == b"DONE":
                break
            f.write(bytes_read)
    print(f"File {file_name} received successfully.")

# Function to send a file to a client
def send_file(client_socket, file_name):
    if os.path.exists(file_name):
        client_socket.send(f"DOWNLOAD {file_name}".encode())
        with open(file_name, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
        client_socket.send(b"DONE")
    else:
        client_socket.send(f"ERROR File {file_name} not found.".encode())

# Allow the server to send messages to all connected clients
def server_send_messages():
    while True:
        message = input("Server: ")
        for client in clients:
            client.send(f"Server: {message}".encode())

# Accept incoming client connections
def start_server():
    while True:
        client_socket, addr = server_socket.accept()
        print(f"[+] {addr} connected.")
        clients.append(client_socket)
        
        # Handle client messages in a new thread
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

# Start the server message input in a new thread
threading.Thread(target=server_send_messages).start()

start_server()

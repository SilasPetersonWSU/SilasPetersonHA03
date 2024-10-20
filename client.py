import socket
import threading
import os

# Server details
SERVER_HOST = '127.0.0.1'  
SERVER_PORT = 12345        
BUFFER_SIZE = 1024         # Size of data chunks for sending/receiving data

# Create a client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

# Function to handle sending messages
def send_message():
    while True:
        message = input()
        if message.startswith("UPLOAD"):  # Upload command
            _, file_name = message.split(" ")
            upload_file(file_name)
        else:  # Send regular chat message
            client_socket.send(message.encode())

# Function to upload files to the server
def upload_file(file_name):
    try:
        with open(file_name, "rb") as f:
            client_socket.send(f"UPLOAD {file_name}".encode())  # Notify the server about the file upload
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)  # Send file data in chunks
        client_socket.send(b"DONE")  # Indicate the end of file transfer
        print(f"File {file_name} uploaded successfully.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")

# Function to receive messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()  # Receive and decode message from server
            if message == "":  # If connection closed
                break
            print(message)  # Print received message
        except:
            print("Error receiving message.")
            break

# Start two threads: one for receiving messages and one for sending messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_message)
send_thread.start()

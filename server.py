import socket
import threading
import json
import os
import base64

SERVER_MEDIA = 'server_media'
os.makedirs(SERVER_MEDIA, exist_ok=True)

HOST = '127.0.0.1'  # Loopback address for localhost
PORT = 12345       # Port to listen on

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the specified address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")

ack_json = {
  "type": "connect_ack",
  "payload": {
    "message": "Connected to the room."
  }
}

def broadcast_to_room(message):
    for client in rooms.get(current_room, []):
        if client != client_socket:
            client.send(json.dumps(message).encode('utf-8'))

# Functions to handle the type of message
def upload_file(client_socket, file_path):
    file_name = os.path.basename(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        with open(os.path.join(SERVER_MEDIA, file_name), 'wb') as server_file:
            server_file.write(file_data)
        response = {
            "type": "message",
            "payload": {
                "sender": "Server",
                "text": f"User {client_socket.getpeername()} uploaded the {file_name} file."
            }
        }
        broadcast_to_room(response)
    else:
        response = {
            "type": "message",
            "payload": {
                "sender": "Server",
                "text": f"File {file_name} doesn't exist."
            }
        }
        client_socket.send(json.dumps(response).encode('utf-8'))

def download_file(client_socket, file_name):
    file_path = os.path.join(SERVER_MEDIA, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        file_encode64 = base64.b64encode(file_data).decode('utf-8')
        response = {
            "type": "file",
            "payload": {
                "file_name": file_name,
                "file_data": file_encode64
            }
        }
        client_socket.send(json.dumps(response).encode('utf-8'))
    else:
        response = {
            "type": "message",
            "payload": {
                "sender": "Server",
                "text": f"The {file_name} doesn't exist."
            }
        }
        client_socket.send(json.dumps(response).encode('utf-8'))

# Function to handle a client's messages
def handle_client(client_socket, client_address, room):
    print(f"Accepted connection from {client_address}")

    while True:
        message = json.loads(client_socket.recv(1024).decode('utf-8'))
        if not message:
            break

        message_type = message['type']
        if message_type == "upload":
            file_path = message['payload']['file_path']
            upload_file(client_socket, file_path)
        elif message_type == "download":
            file_name = message['payload']['file_name']
            download_file(client_socket, file_name)
        elif message_type == "message":
            # Broadcast messages as before
            for client in rooms.get(room, []):
                if client != client_socket:
                    client.send(json.dumps(message).encode('utf-8'))

    # Remove the client from the list associated with the room
    rooms[room].remove(client_socket)
    client_socket.close()

clients = []
rooms = {}

while True:
    client_socket, client_address = server_socket.accept()
    connection = json.loads(client_socket.recv(1024).decode('utf-8'))
    if connection:
        client_socket.send(json.dumps(ack_json).encode('utf-8'))
        current_room = connection['payload']['room']
        clients.append(client_socket)
        # Create the room list if it doesn't exist
        rooms.setdefault(current_room, []).append(client_socket)

        # Start a thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, current_room))
        client_thread.start()
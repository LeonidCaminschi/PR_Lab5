import socket
import threading
import json

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

# Function to handle a client's messages
def handle_client(client_socket, client_address, room):
    print(f"Accepted connection from {client_address}")

    while True:
        message = json.loads(client_socket.recv(1024).decode('utf-8'))
        if not message:
            break  # Exit the loop when the client disconnects
        print(f"Received from {client_address}: {message}")

        # Broadcast the message to all clients in the same room
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
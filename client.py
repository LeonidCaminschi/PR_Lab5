import socket
import threading
import json
import base64

# Server configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345  # Server's port

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

# Function to receive and display messages
def receive_messages():
    while True:
        data = client_socket.recv(1024)
        if not data:
            break  # Exit the loop when the server disconnects

        try:
            message = json.loads(data.decode('utf-8'))

            # Handle JSON messages
            if message['type'] == "message":
                print("\n" + message['payload']['sender'] + ": " + message['payload']['text'])
            if message['type'] == "file":
                file_name = message['payload']['file_name']
                file_data_base64 = message['payload']['file_data']
                file_data = base64.b64decode(file_data_base64.encode('utf-8'))

                # Save the file on the client-side, for example:
                with open(file_name, 'wb') as file:
                    file.write(file_data)
        except json.JSONDecodeError:
            file_name = "image.png"  # Set the desired file name and extension
            with open(file_name, 'wb') as file:
                file.write(data)
            print(f"Downloaded file: {file_name}")


# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True  # Thread will exit when the main program exits
receive_thread.start()

username = input("Enter username to proceed with the chat initialization: ")

while True:
    roomname = input("Enter the room you would like to try to connect or ('exit' to quit): ")

    if roomname.lower() == 'exit':
        break

    connect_json = {
      "type": "connect",
      "payload": {
        "name": f"{username}",
        "room": f"{roomname}"
      }
    }

    client_socket.send(json.dumps(connect_json).encode('utf-8'))
    response = json.loads(client_socket.recv(1024))

    if response: #needs to be worked on
        print(f"Entered room: {roomname}")
        print("Enter a message (or 'disconnect' to leave the room): ")
        while True:
            message = input(f"{username}: ")

            if message.lower() == 'disconnect':
                break

            if message.lower() == 'upload':
                file_path = input("Enter the path to the file you want to upload: ")
                upload_command = {
                    "type": "upload",
                    "payload": {
                        "file_path": file_path
                    }
                }
                client_socket.send(json.dumps(upload_command).encode('utf-8'))
            elif message.lower() == 'download':
                file_name = input("Enter the name of the file you want to download: ")
                download_command = {
                    "type": "download",
                    "payload": {
                        "file_name": file_name
                    }
                }
                client_socket.send(json.dumps(download_command).encode('utf-8'))
            else:
                message_json = {
                    "type": "message",
                    "payload": {
                        "sender": f"{username}",
                        "room": f"{roomname}",
                        "text": f"{message}"
                    }
                }

                # Send the message to the server
                client_socket.send(json.dumps(message_json).encode('utf-8'))

# Close the client socket when done
client_socket.close()
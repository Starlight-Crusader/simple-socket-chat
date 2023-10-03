import socket
import threading
import json


HOST = '127.0.0.1'
PORT = 55555

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the specified address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()
print(f'Server is listening on {HOST}:{PORT}')

rooms = {}

# Function to handle a client's messages
def handle_client(client_socket, client_address):
    print(f'Accepted connection from {client_address}')

    while True:
        message = client_socket.recv(1024)
        
        if not message:
            break # Exit the loop when the client disconnects

        message_data = json.loads(message.decode('utf-8'))

        print(f"Received from {client_address}: {message_data['type']}")

        if message_data['type'] == 'connect':
            if message_data['payload']['room_name'] not in rooms.keys():
                rooms[message_data['payload']['room_name']] = []

            rooms[message_data['payload']['room_name']].append(client_socket)

            response_data = {
                'type': 'connect_ack',
                'payload': {
                    'message': 'Successfully connected to the room!'
                }
            }

            client_socket.send(json.dumps(response_data).encode('utf-8'))
        # elif message_data['type'] == 'disconnect':
        #     rooms[message_data['payload']['room_name']].remove(client_socket)
        elif message_data['type'] == 'message':

            # Broadcast the message to all the clients in the room
            for client in rooms[message_data['payload']['room_name']]:
                if client != client_socket:
                    client.send(message)

    # Remove the client from the list and room
    for room in rooms.keys():
        if client_socket in rooms[room]:
            rooms[room].remove(client_socket)
            break

    clients.remove(client_socket)
    client_socket.close()

clients = []

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)

    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
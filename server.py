import socket, threading, sys, signal, threading, json, time


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
        try:
            message = client_socket.recv(1024)
        except:
            pass
        
        if not message:
            break # Exit the loop when the client disconnects

        message_data = json.loads(message.decode('utf-8'))

        print(f"Received from {client_address}: {message_data['type']}")

        if message_data['type'] == 'connect':
            if message_data['payload']['room_name'] not in rooms.keys():
                print(f"Created a new room {message_data['payload']['room_name']} for user {message_data['payload']['nickname']}")
                rooms[message_data['payload']['room_name']] = []

            rooms[message_data['payload']['room_name']].append(client_socket)

            print(f"Added user {message_data['payload']['nickname']} to the room {message_data['payload']['room_name']}")

            response_data = {
                'type': 'connect_ack',
                'payload': {
                    'message': 'Successfully connected to the room!'
                }
            }

            client_socket.send(json.dumps(response_data).encode('utf-8'))

            notification_data = {
                'type': 'notification',
                'payload': {
                    'message': f"{message_data['payload']['nickname']} has connected..."
                }
            }

            for client in rooms[message_data['payload']['room_name']]:
                if client != client_socket:
                    client.send(json.dumps(notification_data).encode('utf-8'))

        elif message_data['type'] == 'message':
            if message_data['payload']['text'] == 'exit':

                notification_data = {
                    'type': 'notification',
                    'payload': {
                        'message': f"{message_data['payload']['sender']} has disconnected..."
                    }
                }
                
                for client in rooms[message_data['payload']['room_name']]:
                    if client != client_socket:
                        client.send(json.dumps(notification_data).encode('utf-8'))

                time.sleep(1)
                rooms[message_data['payload']['room_name']].remove(client_socket)
                clients.remove(client_socket)
                client_socket.close()

                print(f"User {message_data['payload']['sender']} left the room {message_data['payload']['room_name']}")

                if len(rooms[message_data['payload']['room_name']]) == 0:
                    rooms.pop(message_data['payload']['room_name'])
                    print(f"Removed the empty room {message_data['payload']['room_name']}")
            else:
                # Broadcast the message to all the clients in the room
                for client in rooms[message_data['payload']['room_name']]:
                    if client != client_socket:
                        client.send(message)

clients = []


# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print('\nShutting down the server...')
    server_socket.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)

    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
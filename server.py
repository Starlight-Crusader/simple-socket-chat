import socket, threading, sys, signal, threading, json, os, base64, shutil, math


HOST = '127.0.0.1'
PORT = 55555

SEPARATOR = '<SEPARATOR>'
BUFFER_SIZE = 4096

MEDIA_PATH = './media/server/'
try:
    os.makedirs(MEDIA_PATH)
except:
    pass

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
        message = client_socket.recv(1024).decode('utf-8')
        
        if not message:
            break # Exit the loop when the client disconnects

        try:
            message_data = json.loads(message)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {message_data}")
            continue

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

                rooms[message_data['payload']['room_name']].remove(client_socket)
                print(f"User {message_data['payload']['sender']} left the room {message_data['payload']['room_name']}")

                if len(rooms[message_data['payload']['room_name']]) == 0:
                    rooms.pop(message_data['payload']['room_name'])
                    print(f"Removed the empty room {message_data['payload']['room_name']}")

                print(f"Closed connection for the user {message_data['payload']['sender']}")

                if message_data['payload']['room_name'] in rooms.keys():
                    notification_data = {
                        'type': 'notification',
                        'payload': {
                            'message': f"{message_data['payload']['sender']} has disconnected..."
                        }
                    }
                
                    for client in rooms[message_data['payload']['room_name']]:
                        client.send(json.dumps(notification_data).encode('utf-8'))

            else:

                # Broadcast the message to all the clients in the room
                for client in rooms[message_data['payload']['room_name']]:
                    if client != client_socket:
                        client.send(message.encode('utf-8'))
        
        elif message_data['type'] == 'file-upload':

            filename = message_data['payload']['filename']

            base64_data = message_data['payload']['chunk']
            bytes_data = base64.b64decode(base64_data)

            with open(MEDIA_PATH + filename, 'ab') as f:
                f.write(bytes_data)

            f.close()

            if message_data['payload']['chunk_num'] == message_data['payload']['chunk_total']:
                print(f'{filename} recieved')

                notification_data = {
                'type': 'notification',
                'payload': {
                    'message': f"{message_data['payload']['sender']} uploaded file {filename}. Enter dl~{filename} to start the download ..."
                }
            }
                
            for client in rooms[message_data['payload']['room_name']]:
                if client != client_socket:
                    client.send(json.dumps(notification_data).encode('utf-8'))

        elif message_data['type'] == 'download-req':

            filename = message_data['payload']['filename']
            filesize = os.path.getsize(MEDIA_PATH + filename)

            with open(MEDIA_PATH + filename, 'rb') as f:
                chunk_num = 1
                chunk_total = math.ceil(filesize / BUFFER_SIZE)

                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    base64_data = base64.b64encode(bytes_read).decode('utf-8')

                    if not bytes_read:
                        break

                    message_data = {
                        'type': 'file-download',
                        'payload': {
                            'filename': filename,
                            'chunk_num': chunk_num,
                            'chunk_total': chunk_total,
                            'chunk': base64_data
                        }
                    }

                    client_socket.send(json.dumps(message_data).encode('utf-8'))

                    chunk_num += 1

            f.close()

    clients.remove(client_socket)
    client_socket.close()

clients = []


# Function to handle Ctrl+C and other signals
def signal_handler(sig, frame):
    print('\nShutting down the server...')

    try:
        shutil.rmtree(MEDIA_PATH)
    except OSError as e:
        print(f"Error: {e}")

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
import socket, threading, json, os, base64, math
from time import sleep


HOST = '127.0.0.1'
PORT = 55555

SEPARATOR = '<SEPARATOR>'
BUFFER_SIZE = 4096

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')

# Some client's status variables
nickname = ''
room_name = ''
acknowledged = False
receive_thread_active = True


# Call one time at the very beginning to setup nickname and the name of the room to join
def initial_setup():
    global nickname, room_name

    nickname = input('Pick a nickname visible to others - ')
    room_name = input('Insert the name of the room to join/create - ')

    message_data = {
        'type': 'connect',
        'payload': {
            'nickname': nickname,
            'room_name': room_name
        }
    }

    client_socket.send(json.dumps(message_data).encode('utf-8'))
    sleep(1)


# Thread function to receive and display messages
def receive_messages():
    global acknowledged, receive_thread_active

    while receive_thread_active:
        try:
            message = client_socket.recv(1024)
        
            if not message:
                break

            message_data = json.loads(message.decode('utf-8'))
        
            if message_data['type'] == 'connect_ack':
                acknowledged = True
                print(f"{message_data['payload']['message']}")
            elif message_data['type'] == 'message':
                print(f"~\n{message_data['payload']['sender']}: {message_data['payload']['text']}", "\nEnter a message (or 'exit' to quit): ", end='')
            elif message_data['type'] == 'notification':
                print(f"~\n{message_data['payload']['message']}", "\nEnter a message (or 'exit' to quit): ", end='')
        except ConnectionAbortedError:
            print('Connection to the server was terminated ... :(')
            break

# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()


while True:
    initial_setup()

    while acknowledged:
        message_text = input("Enter a message (or 'exit' to quit): ")

        if not message_text:
            break
        elif message_text.lower() == 'exit':
            acknowledged = False

        if message_text[:3].lower() == "ul-":
            filename = message_text[3:]
            filesize = os.path.getsize(filename)

            receive_thread_active = False

            with open(filename, 'rb') as f:
                chunk_num = 1
                chunk_total = math.ceil(filesize / BUFFER_SIZE)

                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    base64_data = base64.b64encode(bytes_read).decode('utf-8')

                    if not bytes_read:
                        break

                    message_data = {
                        'type': 'file-upload',
                        'payload': {
                            'filename': filename,
                            'sender': nickname,
                            'room_name': room_name,
                            'chunk_num': chunk_num,
                            'chunk_total': chunk_total,
                            'chunk': base64_data
                        }
                    }

                    client_socket.send(json.dumps(message_data).encode('utf-8'))

                    chunk_num += 1

            receive_thread_active = True

            continue

        message_data = {
            'type': 'message',
            'payload': {
                'sender': nickname,
                'room_name': room_name,
                'text': message_text
            }
        }

        client_socket.send(json.dumps(message_data).encode('utf-8'))
        sleep(1)

    print('\nShutting down the client...')
    break


# Close the client socket when done
client_socket.close()

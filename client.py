import socket
import threading
import json
from time import sleep


HOST = '127.0.0.1'
PORT = 55555

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')

# Some client's paramters
nickname = ''
room_name = ''
acknowledged = False


# Call one time at the very beginning to setup nickname and the name of the room to join
def initial_setup():
    nickname = input("Pick a nickname visible to others - ")
    room_name = input("Insert the name of the room to join/create - ")

    message_data = {
        'type': 'connect',
        'payload': {
            'nickname': nickname,
            'room_name': room_name
        }
    }

    client_socket.send(json.dumps(message_data).encode('utf-8'))

# initial_setup()

# Function to receive and display messages
def receive_messages():
    global acknowledged

    while True:
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
        except ConnectionAbortedError:
            print("Connection to the server was terminated ... :(")
            break

# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()


# Function to send messages
def send_chat_messages():
    global acknowledged

    while True:
        if acknowledged == False:
            nickname = input("Pick a nickname visible to others - ")
            room_name = input("Insert the name of the room to join/create - ")

            message_data = {
                'type': 'connect',
                'payload': {
                    'nickname': nickname,
                    'room_name': room_name
                }
            }
        else:
            message_text = input("Enter a message (or 'exit' to quit): ")
    
            if not message_text or message_text.lower() == 'exit':
                break

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

# Start the message serving thread
send_thread = threading.Thread(target=send_chat_messages)
send_thread.daemon = True
send_thread.start()


# Wait for both threads to complete before closing the client socket
send_thread.join()
receive_thread.join()

# Close the client socket when done
client_socket.close()
import socket, threading, json, os, tqdm
from time import sleep


HOST = '127.0.0.1'
PORT = 55555

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')

# Some client's status variables
nickname = ''
room_name = ''
acknowledged = False


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

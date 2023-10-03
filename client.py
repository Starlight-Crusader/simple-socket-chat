import socket
import threading


HOST = '127.0.0.1'
PORT = 55555

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')


# Function to receive and display messages
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
        
            if not message:
                break
        
            # Print the recieved message
            print(f'~\nReceived: {message}', "\nEnter a message (or 'exit' to quit): ", end='')
        except ConnectionAbortedError:
            print("Connection to the server was terminated ... :(")
            break


# Function to send messages
def send_messages():
    while True:
        message = input("Enter a message (or 'exit' to quit): ")
    
        if not message or message.lower() == 'exit':
            break

        # Send the message to the server
        client_socket.send(message.encode('utf-8'))


# Start the message reception thread
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Start the message serving thread
send_thread = threading.Thread(target=send_messages)
send_thread.daemon = True
send_thread.start()

# Wait for both threads to complete before closing the client socket
send_thread.join()
receive_thread.join()

# Close the client socket when done
client_socket.close()
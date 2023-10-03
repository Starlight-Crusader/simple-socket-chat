import socket
import threading


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
        message = client_socket.recv(1024).decode('utf-8')
        
        if not message:
            break # Exit the loop when the client disconnects

        print(f'Received from {client_address}: {message}')
        
        # Broadcast the message to all clients
        for client in clients:
            if client != client_socket: # find alternative to this IF
                client.send(message.encode('utf-8'))

    # Remove the client from the list
    clients.remove(client_socket)
    client_socket.close()

clients = []

while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)

    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
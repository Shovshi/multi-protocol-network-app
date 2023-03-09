import socket

def tcp():
    # create a TCP socket
    help_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # set the server address and port number
    help_server_address = ('localhost', 8000)

    # bind the socket to the server address and port number
    help_server_socket.bind(help_server_address)

    # listen for incoming connections
    help_server_socket.listen()

    # accept a connection from a client
    app_server_socket, app_address = help_server_socket.accept()
    print("TCP connection succeed")

    return app_server_socket , help_server_socket

def receive_data(client_socket):
    # receive data from the client
    data = client_socket.recv(1024)
    integer = int.from_bytes(data, byteorder='big')
    if integer > 0:
        print("Received request")
    return data

def decode_data(packet):
   option = packet.decode()
   return option


def send_tcp(app , option):
    #Split the words in the request message
    words = option.split()
    # Get the second word, which should be the file path ("/dog.jpg")
    file_path = words[1]
    # Remove the initial forward slash
    file_path = file_path[1:]
    with open(file_path, "rb") as picture:
        print("IMAGE:", file_path)
        # Read the image data
        data = picture.read()
        # Send the image data to the client
        app.send(data)

if __name__ == '__main__':

    app_socket , server_socket = tcp()
    receive_packet = receive_data(app_socket)
    selected_option = decode_data(receive_packet)
    send_tcp(app_socket , selected_option)
    app_socket.close()
    server_socket.close()



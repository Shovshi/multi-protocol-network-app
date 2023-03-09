import socket
import struct
import time
from PIL import Image


def rudp_connect():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('localhost', 8000))
    return server

def ack_packet(sequence , client_addr):
    # create an ACK packet with the next expected sequence number
    ack_num = seq_num + 1
    ack = struct.pack('!II', ack_num, 0)
    if server_socket.sendto(ack, client_addr) > 0:
        print("successfully sent ack number")

def get_seq(packet):
    sequence = struct.unpack('!I', packet[:4])[0]
    return sequence

def tcp_connection():
    # create a TCP socket
    app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # set the server address and port number
    help_server_address = ('localhost', 8000)

    # connect to the server
    app_socket.connect(help_server_address)
    return app_socket , help_server_address

def send_tcp(app_socket ,help_server_address, data):

    picture_request = data + '.jpg'
    request = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(picture_request, help_server_address)
    app_socket.send(request.encode())

def receive_tcp(app_socket):
    # We open a file so we can write the picture data into it
    with open("image.jpg", "wb") as image:
        picture_data = b''
        while True:
            response = app_socket.recv(4096)
            if not response:
                break
            picture_data += response

    # Open the file again to write the picture data
    with open("image.jpg", "wb") as image_file:
        image_file.write(picture_data)

    return 'image.jpg'

def send_udp(image , client_add):
     with open(image, 'rb') as img:
        # We read the file in chunks of 1024 bytes
        chunk = img.read(1024)
        while chunk:
            # Send each chunk to the client
            server_socket.sendto(chunk, client_add)
            # Read the next chunk
            chunk = img.read(1024)

if __name__ == '__main__':

    server_socket = rudp_connect()

    #Get the first syn packet to initiate the connection
    receive_packet , client_address = server_socket.recvfrom(1024)
    int_value = int.from_bytes(receive_packet, byteorder='big')
    #Make sure we get the right packet
    if int_value == 0 :
        print("successfully received seq number")
    #Get the seq number from the packet
    seq_num = get_seq(receive_packet)
    #Sending ACK
    ack_packet(seq_num , client_address)

    #Get the request packet
    receive_packet, client_address = server_socket.recvfrom(1024)
    integer = int.from_bytes(receive_packet, byteorder='big')
    #Check if we got it properly
    if integer > 0:
        print("received request")

    # Get the request itself
    request_message = receive_packet[4:].decode()
    print("Request message: ", request_message)
    # Get the sequence number from the packet we received
    get_seq(receive_packet)
    #Sending back an ACK
    ack_packet(seq_num, client_address)

    #Open a tcp connection between the APP server and the help server to get the picture the client wants
    app_server_socket , help_server = tcp_connection()
    send_tcp(app_server_socket ,help_server , request_message)
    picture_file_name = receive_tcp(app_server_socket)
    app_server_socket.close()

    #Sending the picture back to the client
    send_udp(picture_file_name,client_address)
























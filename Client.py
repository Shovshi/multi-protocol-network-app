from scapy.all import*
import time

from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.layers.http import HTTP, HTTPRequest
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send

import socket
import struct
from PIL import Image


src_mac = '08:00:27:80:c2:67'
dst_mac = 'ff:ff:ff:ff:ff:ff'
my_ip = '0.0.0.0'

#DHCP
def discover():
    eth = Ether(dst='ff:ff:ff:ff:ff:ff')
    ip = IP(dst='255.255.255.255')
    udp = UDP(dport=67, sport=68)
    dhcp = DHCP(options=[('message-type', 'discover'), 'end'])
    bootp = BOOTP(chaddr='08:00:27:80:c2:67', xid=0x1337)

    packet = eth / ip / udp / bootp / dhcp
    time.sleep(1)
    sendp(packet)

def handle_offer_packet(packet):
    if DHCP in packet and packet[DHCP].options[0][1] == 2:  # Check for DHCP Offer packet
        print("Received offer packet")


def receive_offer():
    res = sniff(filter="udp and (port 67 or 68)", count=1 , store=1)
    return res

def receive_ack():
    ack_packet = sniff(filter="udp and (port 67 or 68)", count=1 , store=1)
    print("Received ACK packet")

def request(packet):
    eth_frame = Ether(dst=dst_mac)
    ip_packet = IP(src='0.0.0.0', dst='255.255.255.255')
    udp_packet = UDP(sport=68, dport=67)
    dhcp_packet = DHCP(options=[('message-type', 'request'),'end'])
    bootp_packet = BOOTP(chaddr= src_mac , xid=packet[BOOTP].xid , yiaddr=packet[BOOTP].yiaddr)
    packet_request = eth_frame / ip_packet / udp_packet /  bootp_packet / dhcp_packet


    time.sleep(1)
    sendp(packet_request)



#DNS
def dns_request():
    dns_query = DNSQR(qname="google.com" , qtype=1)
    eth_layer = Ether(src=src_mac , dst=src_mac)
    ip_layer = IP(src= '192.168.1.3' ,dst='192.168.1.5')
    udp_layer = UDP(dport=53)
    dns_request_packet =eth_layer / ip_layer / udp_layer / DNS(rd=1, qd=dns_query)

    time.sleep(1)
    sendp(dns_request_packet , verbose=2)

def dns_response():
    sniff(filter="udp and port 53", count=1 , store=1)
    print("Received dns response")

#APP
def rudp_connection(picture_selected):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 8000)
    seq_num = 0
    syn_packet = struct.pack('i', seq_num)
    if client_socket.sendto(syn_packet, server_address) > 0  :
        print("successfully sent syn")

    receive_packet,server_address= client_socket.recvfrom(1024)
    int_value = int.from_bytes(receive_packet, byteorder='big')
    if int_value > 0 :
        print("successfully received ack number")

    ack_num , window_size = struct.unpack('ii', receive_packet)

    if ack_num == seq_num + 1:
        print('RUDP connection success')


    #sending request packet
    request_message = picture_selected.encode()
    seq_num = seq_num+1
    data = struct.pack('!I', seq_num) + request_message
    did_send = False

    client_socket.settimeout(2)
    client_socket.sendto(data, server_address)
    print("sent request packet")

    while not did_send:
        try:
            receive_packet, server_address = client_socket.recvfrom(1024)
            did_send = True
            print("successfully received ACK")
        except socket.timeout:
            print("timeout expired to get ack, retransmission")
            client_socket.sendto(request_message, server_address)
    return client_socket

    received_file = open('picture_file', 'ab')
    try:
        while True:
            chunk, server_address = client.recvfrom(1024)
            if not chunk:
                break
            bytes_written = received_file.write(chunk)
            if bytes_written < len(chunk):
                raise IOError('Failed to write all data to file')
    except socket.timeout:
        print('Timed out waiting for data')
    finally:
        received_file.close()


def select_option():
    print("Please choose an option:")
    print("1. picture of a cat")
    print("2. picture of a dog")
    print("3. picture of a koala")
    print("4. The best picture")

    option = input("Enter your choice (1-4): ")

    if option == "1":
        selected = 'cat'
    elif option == "2":
        selected = 'dog'
    elif option == "3":
        selected = 'koala'
    elif option == "4":
        selected = 'ant'
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")

    return selected

if __name__ == '__main__':

    '''
    #DHCP part
    discover()
    captured_packets = receive_offer()
    my_ip = captured_packets[0][BOOTP].yiaddr
    handle_offer_packet(captured_packets[0])
    request(captured_packets[0])
    receive_ack()

    #DNS part
    dns_request()
    dns_response()
    '''


    #APP part
    picture = select_option()
    client_sock = rudp_connection(picture)









'''
File acts as a Trivial File Transfer Protocol Client using UDP.  Does basic read and write operations and handels errors
'''

import argparse
import socket
import time
from constructpacket import build_rrq
from constructpacket import build_wrq
from constructpacket import build_data
from constructpacket import build_ack
from constructpacket import build_error

from deconstructpacket import unpack_data
from deconstructpacket import unpack_ack
from deconstructpacket import unpack_error

'''
ARGPARSE

FORMAT:
    1.	‘-a’ is for IP Addresses,
    2.	‘-sp’ for server port
    3.	‘-f’ for file name,
    4.	‘-p’ for port numbers
    5.	‘-m’ for mode (r = read from server, w = write to server)

Example: python3 trivialftp.py -a 234.45.345.2 -sp 50001 -p 50000 -f mytext.txt -m w
'''
parser = argparse.ArgumentParser(description='Communicate Via TFTP')
parser.add_argument('-a', '--address', help='IP Address', required=True)
parser.add_argument('-sp', '--serverport', type=int, help='Server Port', required=True)
parser.add_argument('-p', '--clientport', type=int, help='Port Number', required=True)
parser.add_argument('-f', '--filename', type=str, help='File Name', required=True)
parser.add_argument('-m', '--mode', type=str, help='Mode: r = read from server, w = write to server', required=True)
args = parser.parse_args()

if (args.mode != 'r' and args.mode != 'w'):
    print("Invalid mode: Must use 'r' for Read or 'w' for Write")
    exit()
elif (args.serverport < 5000 or args.serverport > 65535 or args.clientport < 5000 or args.clientport > 65535):
    print("Port numbers must be between 5000 and 65,535")
    exit()

def checkTID(message, serverAddress):
    while serverAddress != (args.address, args.serverport):
        print("RECEIVED ADDRESS: ", serverAddress)
        print("EXPECTED ADDRESS: ", (args.address, args.serverport))
        packetERROR = build_error(5, 'Unknown transfer ID')
        print("SENT: ERROR 5, UNKOWN TRANSFER ID")
        clientSocket.sendto(packetERROR, serverAddress)
        message, serverAddress = clientSocket.recvfrom(2048)
    return message


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = ''

if __name__ == '__main__':

    if (args.mode == 'r'):
        # BUILD READ-REQUEST PACKET
        packet = build_rrq(args.filename, 'netascii')
        time.sleep(1)
        # SEND RRQ PACKET
        clientSocket.sendto(packet, (args.address, args.serverport))
        # RECEIVE DATA PACKET
        message, serverAddress = clientSocket.recvfrom(2048)
        message = checkTID(message, serverAddress)
        if (message[1] == 3): # message is a DATA packet
            # UNPACK DATA PACKET
            (opcode, blockNum, data) = unpack_data(args.filename, message)
            #print("Client receiving DATA packet: ", packet, "  Block number: ", blockNum, "  Data Length: ", len(data))
            # BUILD ACK PACKET
            packetACK = build_ack(blockNum)
            # SEND ACK PACKET
            clientSocket.sendto(packetACK, (args.address, args.serverport))
            #print("Client sending ACK packet: ", packet, "  Block number: ", blockNum)
            # WHILE DATA IS MAXED
            while len(data) > 511:
                blockIndex = blockNum
                # RECEIVE DATA PACKET
                message, serverAddress = clientSocket.recvfrom(2048)
                message = checkTID(message, serverAddress)
                # UNPACK DATA PACKET
                (opcode, blockNum, data) = unpack_data(args.filename, message)
                #print("Client receiving DATA packet: ", packet, "  Block number: ", blockNum, "  Data Length: ", len(data))
                # BUILD ACK PACKET
                #print(blockNum)
                packetACK = build_ack(blockNum)
                # SEND ACK PACKET

                clientSocket.sendto(packetACK, (args.address, args.serverport))
                #print("Client sending ACK packet: ", packet, "  Block number: ", blockNum)
#        elif (message[1] == 4):
#            (blockNum) = unpack_ack(args.filename, message)
#        elif (message[1] == 5):
#            (error_code, error_msg) = unpack_error(args.filename, message)


    elif (args.mode == 'w'):
        # BUILD WRITE-REQUEST PACKET
        packet = build_wrq(args.filename, 'netascii')
        #print("Client sending WRQ packet: ", packet)
        time.sleep(1)
        # SEND WRQ PACKET
        clientSocket.sendto(packet, (args.address, args.serverport))
        # RECEIVE ACK PACKET
        message, serverAddress = clientSocket.recvfrom(2048)
        message = checkTID(message, serverAddress)
        if (message[1] == 4): # packet is an ACK packet
            # UNPACK ACK PACKET
            blockNum = unpack_ack(message)
            #print("Client receiving ACK packet, Block number: ", blockNum)
            # INITIALIZE DATA LENGTH = 512
            dataLen = 512

            with open(args.filename, "r") as file_object:
                while dataLen == 512:
                    # INCREASE BLOCK NUMBER BY 1 (STARTING AT 1)
                    blockNum = blockNum + 1
                    # COLLECT UP TO 512 BYTES OF DATA FROM FILE
                    data = file_object.read(512)
                    # RECORD DATA LENGTH
                    dataLen = len(data)
                    # CONVERT TO BYTE ARRAY
                    data = bytearray(data.encode('utf-8'))
                    # CONSTRUCT DATA PACKET
                    packetDATA = build_data(data, blockNum)
                    # SEND DATA PACKET
                    clientSocket.sendto(packetDATA, (args.address, args.serverport))
                    #print("Client sending DATA packet: ", packetDATA, "  Block number: ", blockNum)
                    # RECEIVE ACK PACKET
                    message, serverAddress = clientSocket.recvfrom(2048)
                    message = checkTID(message, serverAddress)
                    # UNPACK ACK PACKET
                    blockNum = unpack_ack(message)
                    #print("Client receiving ACK packet, Block number: ", blockNum)


clientSocket.close()





'''
Deconstructs 5 all 5 kinds of TFTP packet headers:
	opcode 	operation
	--------------------------
	 1		Read request (RRQ)
	 2		Write request (WRQ)
	 3 		Data (DATA)
	 4		Acknowledgment (ACK)
 	 5 		Error (ERROR)
'''

# OPCODE: 3		Deconstructs data packet
def unpack_data(filename, packet):
	opcode = 3
	blockNum = int.from_bytes((packet[2],packet[3]), "big")
	data = bytearray()
	j = 4
	if (len(packet) < 5):
		with open(filename,"ba") as file_object:
			file_object.close()
	else:
		while (j < len(packet)):
			data.append(packet[j])
			j = j + 1

		with open(filename, "ba") as file_object:
			file_object.write(data)

	file_object.close()

	return opcode, blockNum, data

# OPCODE: 4		Deconstructs acknowledge packet
def unpack_ack(packet):
	opcode = 4
	blockNum = int.from_bytes((packet[2], packet[3]), "big")
	return blockNum

# OPCODE: 4		Deconstructs error packet
def unpack_error(packet):
	opcode = 5
	error_code = packet[3]
	error_msg = bytearray()
	j = 4
	while j < len(packet):
		error_msg.append(packet[j])
		j = j + 1

	error_msg = error_msg.decode('utf-8')
	return error_code, error_msg
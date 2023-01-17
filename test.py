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

blockNum = 128
packetACK = build_ack(blockNum)
print(packetACK)
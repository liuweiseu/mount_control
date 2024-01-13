#! /usr/bin/env python3

import serial
import struct

class BaseSerial(base):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def send(self, cmd):
        self.ser.write(cmd)

    def read(self):
        data = b''
        while True:
            line = self.ser.readline()
            if not line:
                break
            data += line
        return data

    def close(self):
        self.ser.close()

    def __del__(self):
        self.close()

class MountSerial(BaseSerial):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5):
        super().__init__(port, baudrate, timeout)
    
d = [1,178,4,0,0,0,2]
cmd = struct.pack('s7B',b'P',*d)
# Open the serial port with a timeout of 1 second
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)

# Send data over UART
print(cmd)
ser.write(cmd)

# Read data from UART
data = b''
while True:
    line = ser.readline()
    if not line:
        break
    data += line

d = struct.unpack('%dBs'%(len(data)-1),data)
print(d)


# Close the serial port
ser.close()

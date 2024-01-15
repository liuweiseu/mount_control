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
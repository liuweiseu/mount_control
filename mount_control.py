import serial

# Open the serial port with a timeout of 1 second
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Send data over UART
ser.write(b'Get AZM-ALT')

# Read data from UART
data = ser.readline()
print(data)

# Close the serial port
ser.close()

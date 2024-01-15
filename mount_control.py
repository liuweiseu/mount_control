#! /usr/bin/env python3

import serial
import struct

CelestronNexStarCmds = {
    "GetRaDec" : "E",
    "GetPreciseRaDec" : "e",
    "GetAltAz" : "Z",
    "GetPreciseAltAz" : "z"
}

class BaseSerial(object):
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
        
# wrapper class for sending commands
class SendCmd_Wrapper(object):
    def __init__(self, ser, cmd):
        self.ser = ser
        self.cmd = cmd

    def sendcmd(self, cmd, data):
        self.sr.send(cmd)
        return self.ser.read()

class MountSerial(BaseSerial):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5, cmds=CelestronNexStarCmds):
        super().__init__(port, baudrate, timeout)
        self.port = port
        self.cmds = cmds
    
    def __InitMethods(self):
        for k in self.cmds():
            cmdobj = SendCmd_Wrapper(self.ser, self.cmds[k])
            setattr(self, k, cmdobj.sendcmd)
    


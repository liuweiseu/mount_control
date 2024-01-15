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
class SendCmd_Wrapper(BaseSerial):
    def __init__(self, port, baudrate, timeout, cmd, data):
        super().__init__(port, baudrate, timeout)
        self.cmd = cmd
        self.data = data

    def sendcmd(self):
        cmd = bytes(self.cmd, 'utf-8')
        data = self.data
        cmdbytes = struct.pack('%ds%dB'%(len(cmd),len(data)), cmd, *data)
        self.send(cmdbytes)
        return self.read()

class MountSerial(object):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5, cmds=CelestronNexStarCmds):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.cmds = cmds
        self.__InitMethods()

    def __InitMethods(self):
        for k in self.cmds:
            cmdobj = SendCmd_Wrapper(self.port, self.baudrate, self.timeout, self.cmds[k], [])
            setattr(self, k, cmdobj.sendcmd)
    


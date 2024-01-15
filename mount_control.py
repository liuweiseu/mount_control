#! /usr/bin/env python3

import serial
import struct

# Get Position Commands Dict
GetRaDecCmd = {
    'cmd'       : 'E',
    'rfmt'      : '4s1s4s1s',
    'roffset'   : [0,2],
    'encode'    : 16
}

GetPreciseRaDecCmd = {
    'cmd'       : 'e',
    'rfmt'      : '8s1s8s1s',
    'roffset'   : [0,2],
    'encode'    : 16
} 

GetAltAzCmd = {
    'cmd'       : 'Z',
    'rfmt'      : '4s1s4s1s',
    'roffset'   : [0,2],
    'encode'    : 16
}

GetPreciseAltAzCmd = {
    'cmd'       : 'z',
    'rfmt'      : '8s1s8s1s',
    'roffset'   : [0,2],
    'encode'    : 16
}

CelestronNexStarCmds = {
    # Get Position Commands
    'GetRaDec'              : GetRaDecCmd,
    'GetPreciseRaDec'       : GetPreciseRaDecCmd,
    'GetAltAz'              : GetAltAzCmd,
    'GetPreciseAltAz'       : GetPreciseAltAzCmd
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
    def __init__(self, port, baudrate, timeout, cmd):
        super().__init__(port, baudrate, timeout)
        self.cmd = cmd

    def sendcmd(self, data=[] , verbose = False):
        '''
        each is a dict, which contains cmd, data, offset, 
        response format, response offset and encode method
        '''
        # cmd is always in the dict
        cmd = bytes(self.cmd['cmd'], 'utf-8')
        # besides cmd, other keys may not be in the dict
        if 'data' in self.cmd: 
            data = self.cmd['data']
        else:
            data = []
        if 'offset' in self.cmd:
            offset = self.cmd['offset']
        else:
            offset = []
        if 'rfmt' in self.cmd:
            rfmt = self.cmd['rfmt']
        else:
            rfmt = 's'
        if 'roffset' in self.cmd:
            roffset = self.cmd['roffset']
        else:
            roffset = -1
        if 'encode' in self.cmd:
            encode = self.cmd['encode']
        else:
            encode = -1
        # pack the data    
        cmdbytes = struct.pack('%ds%dB'%(len(cmd),len(data)), cmd, *data)
        if verbose:
            print('cmd: %s'%cmdbytes)
        self.send(cmdbytes)
        rbytes = self.read()
        r = struct.unpack(rfmt, rbytes)
        rdata = []
        for i in roffset:
            rdata.append(int(r[i], encode))
        return rdata

class MountSerial(object):
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=0.5, cmds=CelestronNexStarCmds):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.cmds = cmds
        self.__initmethods()

    def __initmethods(self):
        for k in self.cmds:
            cmdobj = SendCmd_Wrapper(self.port, self.baudrate, self.timeout, self.cmds[k])
            setattr(self, k, cmdobj.sendcmd)
    


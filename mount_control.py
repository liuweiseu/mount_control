#! /usr/bin/env python3

'''
Each command is implemented in a dict.
The code will get the dict, and then send the cmd and parse the response from the mount.

There are some keys included in each dict:
(1) 'cmd': 
    This is the command sent to the mount.
(2) 'rfmt': 
    This is the response format.
    Example:
        When we send `E`, we will get '34AB,12CE#', which is unpacked as 4 strings:'34AB', ',', '12CE' and '#'.
        So the rfmt is `4s1s4s1s`.
(3) 'roffset'(optional):
    This means which parts are valid in the unpacked strings.
    Example:
        We unpacked the response, and got 4 strings: :'34AB', ',', '12CE' and '#'.
        '34AB' and '12CE' are the valid data, so roffset should be [0,2].
(4) 'parameter':
    This is the input paramater in some commands.
(5) 'poffset':
    This means which data are variable in the parameter.
'''

import serial
import struct

# Get Position Commands Dict
GetRaDecCmd = {
    'cmd'       : 'E',
    'rfmt'      : '4s1s4s1s',
    'rdloc'     : [0,2],
    'rencode'    : 16
}

GetPreciseRaDecCmd = {
    'cmd'       : 'e',
    'rfmt'      : '8s1s8s1s',
    'rdloc'     : [0,2],
    'rencode'    : 16
} 

GetAltAzCmd = {
    'cmd'       : 'Z',
    'rfmt'      : '4s1s4s1s',
    'rdloc'     : [0,2],
    'rencode'    : 16
}

GetPreciseAltAzCmd = {
    'cmd'       : 'z',
    'rfmt'      : '8s1s8s1s',
    'rdloc'     : [0,2],
    'rencode'    : 16
}

# GOTO Commands
GotoRaDecCmd = {
    'cmd'       : 'R',
    'sfmt'      : '1s4s1s4s',
    'sdloc'     : [1,3],
    'rfmt'      : '1s'
}

GotoPreciseRaDecCmd = {
    'cmd'       : 'r',
    'sfmt'      : '1s8s1s8s',
    'sdloc'     : [1,3],
    'rfmt'      : '1s'
}

GotoAltAzCmd = {
    'cmd'       : 'B',
    'sfmt'      : '1s4s1s4s',
    'sdloc'     : [1,3],
    'rfmt'      : '1s'   
}

GotoPreciseAltAzCmd = {
    'cmd'       : 'b',
    'sfmt'      : '1s8s1s8s',
    'sdloc'     : [1,3],
    'rfmt'      : '1s'
}

CelestronNexStarCmds = {
    # Get Position Commands
    'GetRaDec'              : GetRaDecCmd,
    'GetPreciseRaDec'       : GetPreciseRaDecCmd,
    'GetAltAz'              : GetAltAzCmd,
    'GetPreciseAltAz'       : GetPreciseAltAzCmd
    # Goto Commands
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
        if 'rdloc' in self.cmd:
            rdloc = self.cmd['rdloc']
        else:
            roffset = -1
        if 'rencode' in self.cmd:
            rencode = self.cmd['rencode']
        else:
            rencode = -1
        # pack the data    
        cmdbytes = struct.pack('%ds%dB'%(len(cmd),len(data)), cmd, *data)
        if verbose:
            print('cmd: %s'%cmdbytes)
        self.send(cmdbytes)
        rbytes = self.read()
        r = struct.unpack(rfmt, rbytes)
        rdata = []
        for i in rdloc:
            rdata.append(int(r[i], rencode))
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
    


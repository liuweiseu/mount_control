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
    'cmd'       : b'E',
    'sfmt'      : 's',
    'rfmt'      : '4s1s4s1s',
    'rdataloc'  : [0,2],
    'rencode'   : 16
}

GetPreciseRaDecCmd = {
    'cmd'       : b'e',
    'sfmt'      : 's',
    'rfmt'      : '8s1s8s1s',
    'rdataloc'  : [0,2],
    'rencode'   : 16
} 

GetAltAzCmd = {
    'cmd'       : b'Z',
    'sfmt'      : 's',
    'rfmt'      : '4s1s4s1s',
    'rdataloc'  : [0,2],
    'rencode'   : 16
}

GetPreciseAltAzCmd = {
    'cmd'       : b'z',
    'sfmt'      : 's',
    'rfmt'      : '8s1s8s1s',
    'rdataloc'  : [0,2],
    'rencode'   : 16
}

# GOTO Commands
GotoRaDecCmd = {
    'cmd'       : b'R',
    'sdata'     : [b'0000', b',', b'0000'],
    'sfmt'      : '1s4s1s4s',
    'maxsdata'  : 2**16,
    'sdataloc'  : [0,2],
    'rfmt'      : '1s'
}

GotoPreciseRaDecCmd = {
    'cmd'       : b'r',
    'sdata'     : [b'00000000', b',', b'00000000'],
    'sfmt'      : '1s8s1s8s',
    'maxsdata'  : 2**32,
    'sdataloc'  : [1,3],
    'rfmt'      : '1s'
}

GotoAltAzCmd = {
    'cmd'       : b'B',
    'sdata'     : [b'0000', b',', b'0000'],
    'sfmt'      : '1s4s1s4s',
    'maxsdata'  : 2**16,
    'sdataloc'  : [1,3],
    'rfmt'      : '1s'   
}

GotoPreciseAltAzCmd = {
    'cmd'       : b'b',
    'sdata'     : [b'00000000', b',', b'00000000'],
    'sfmt'      : '1s8s1s8s',
    'maxsdata'  : 2**32,
    'sdataloc'  : [1,3],
    'rfmt'      : '1s'
}

# Sync

# Tracking Commands
GetTrackingModeCmd = {
    'cmd'       : b't',
    'sdata'     : [],
    'sfmt'      : 's',
    'rfmt'      : '1B1s',
    'rdataloc'  : [0],
    'rencode'   : 10
}

# TimeLocation Commands

# GPS commands
GPSLinkStatusCmd = {
    'cmd'       : b'P',
    'sfmt'      : 's7B',
    'sdata'     : [1, 176, 55, 0, 0, 0 ,1],
    'rfmt'      : '1B1s',
    'rdataloc'  : [0],
    'rencode'   : 10
}

# RTC Commands
GetDateCmd = {
    'cmd'       : b'P',
    'sfmt'      : 's7B',
    'sdata'     : [1, 178, 3, 0, 0, 0, 2],
    'rfmt'      : '2B1s',
    'rdataloc'  : [0,1],
    'rencode'   : 10
}

GetYearCmd = {
    'cmd'       : b'P',
    'sfmt'      : 's7B',
    'sdata'     : [1, 178, 4, 0, 0, 0, 2],
    'rfmt'      : '2B1s',
    'rdataloc'  : [0,1],
    'rencode'   : 10
}

CelestronNexStarCmds = {
    # Get Position Commands
    'GetRaDec'              : GetRaDecCmd,
    'GetPreciseRaDec'       : GetPreciseRaDecCmd,
    'GetAltAz'              : GetAltAzCmd,
    'GetPreciseAltAz'       : GetPreciseAltAzCmd,
    # Goto Commands
    'GotoRaDec'             : GotoRaDecCmd,
    'GotoPriceseRaDec'      : GotoPreciseRaDecCmd,
    'GotoAltAz'             : GotoAltAzCmd,
    'GotoPreciseAltAz'      : GotoPreciseAltAzCmd,
    # Sync Commands
    # TODO
    # Tracking Commands
    'GetTrackingMode'       : GetTrackingModeCmd,
    # GPS
    'GPSLinkStatus'         : GPSLinkStatusCmd,
    # RTC
    'GetDate'               : GetDateCmd,
    'GetYear'               : GetYearCmd
}

# convert the data type to the template's data type
#
def __convtype(template, d, encode):
    if encode == 10:
        e = 'd'
    elif encode == 16:
        e = 'x'
    if type(template) == bytes:
        tmp = format(d, '0%d%s'%(len(template), e))
        return bytes(tmp, 'utf-8')
    elif type(template) == int:
        return d

# convert the Dict to a object.
# All of the keys-vals are the var member in the obj.
#
class DictVar(object):
    def __init__(self, d):
        self.__dict__.update(d)

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
        each cmd is a dict, which contains cmd, data, offset, 
        response format, response offset and encode method
        '''
        # convert the dict to an obj
        c = DictVar(self.cmd)
        # process send
        # check if sdata is here
        if not hasattr(c, 'sdata'):
            c.sdata = []
        # we need replace some data to be sent
        # if sdataloc is here
        if hasattr(c, 'sdataloc'):
            index = 0
            for i in c.sdataloc:
                c.sdata[i] = data[index]
                index += 1
        # pack the data    
        cmdbytes = struct.pack(c.sfmt, c.cmd, *c.sdata)
        if verbose:
            print('cmd: %s'%cmdbytes)
        self.send(cmdbytes)

        # process recv
        rbytes = self.read()
        if verbose:
            print('rbytes: ', rbytes)
        r = struct.unpack(c.rfmt, rbytes)
        if len(c.rdataloc) > 0  and len(rbytes) > 0:
            rdata = []
            for i in c.rdataloc:
                if type(r[i]) == bytes:
                    rdata.append(int(r[i], c.rencode))
                else:
                    rdata.append(r[i])
        elif len(rbytes) > 0:
            rdata = 0
        else:
            rdata = -1
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
    


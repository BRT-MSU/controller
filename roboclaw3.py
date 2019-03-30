import serial
from PyCRC.CRCCCITT import CRCCCITT


class Roboclaw:
    'Roboclaw Interface Class'

    def __init__(self, comport, rate, timeout=0.01, retries=3):
        self.comport = comport
        self.rate = rate
        self.timeout = timeout
        self._trystimeout = retries
        self._packet = []

        command = [0x80, 0x00, 0x64, 0x17, 0x78]
        # print(self._port.write(b'\x80\x00\x64\x17\x78'))
        # print(self._port.write(bytes(command)))

    # Command Enums
    class Cmd():
        M1FORWARD = 0
        M1BACKWARD = 1
        SETMINMB = 2
        SETMAXMB = 3
        M2FORWARD = 4
        M2BACKWARD = 5
        M17BIT = 6
        M27BIT = 7
        MIXEDFORWARD = 8
        MIXEDBACKWARD = 9
        MIXEDRIGHT = 10
        MIXEDLEFT = 11
        MIXEDFB = 12
        MIXEDLR = 13
        GETM1ENC = 16
        GETM2ENC = 17
        GETM1SPEED = 18
        GETM2SPEED = 19
        RESETENC = 20
        GETVERSION = 21
        SETM1ENCCOUNT = 22
        SETM2ENCCOUNT = 23
        GETMBATT = 24
        GETLBATT = 25
        SETMINLB = 26
        SETMAXLB = 27
        SETM1PID = 28
        SETM2PID = 29
        GETM1ISPEED = 30
        GETM2ISPEED = 31
        M1DUTY = 32
        M2DUTY = 33
        MIXEDDUTY = 34
        M1SPEED = 35
        M2SPEED = 36
        MIXEDSPEED = 37
        M1SPEEDACCEL = 38
        M2SPEEDACCEL = 39
        MIXEDSPEEDACCEL = 40
        M1SPEEDDIST = 41
        M2SPEEDDIST = 42
        MIXEDSPEEDDIST = 43
        M1SPEEDACCELDIST = 44
        M2SPEEDACCELDIST = 45
        MIXEDSPEEDACCELDIST = 46
        GETBUFFERS = 47
        GETPWMS = 48
        GETCURRENTS = 49
        MIXEDSPEED2ACCEL = 50
        MIXEDSPEED2ACCELDIST = 51
        M1DUTYACCEL = 52
        M2DUTYACCEL = 53
        MIXEDDUTYACCEL = 54
        READM1PID = 55
        READM2PID = 56
        SETMAINVOLTAGES = 57
        SETLOGICVOLTAGES = 58
        GETMINMAXMAINVOLTAGES = 59
        GETMINMAXLOGICVOLTAGES = 60
        SETM1POSPID = 61
        SETM2POSPID = 62
        READM1POSPID = 63
        READM2POSPID = 64
        M1SPEEDACCELDECCELPOS = 65
        M2SPEEDACCELDECCELPOS = 66
        MIXEDSPEEDACCELDECCELPOS = 67
        SETM1DEFAULTACCEL = 68
        SETM2DEFAULTACCEL = 69
        SETPINFUNCTIONS = 74
        GETPINFUNCTIONS = 75
        SETDEADBAND = 76
        GETDEADBAND = 77
        RESTOREDEFAULTS = 80
        GETTEMP = 82
        GETTEMP2 = 83
        GETERROR = 90
        GETENCODERMODE = 91
        SETM1ENCODERMODE = 92
        SETM2ENCODERMODE = 93
        WRITENVM = 94
        READNVM = 95
        SETCONFIG = 98
        GETCONFIG = 99
        SETM1MAXCURRENT = 133
        SETM2MAXCURRENT = 134
        GETM1MAXCURRENT = 135
        GETM2MAXCURRENT = 136
        SETPWMMODE = 148
        GETPWMMODE = 149
        FLAGBOOTLOADER = 255

    # Private Functions
    def clear_packet(self):
        self._packet = []
        return

    def append_packet(self, data):
        self._packet.append(data)

        # self._crc = self._crc & 0xFFFF
    def build_command(self, address, command, vals):
        self.clear_packet()
        self.append_packet(address)
        self.append_packet(command)
        for val in vals:
            self.append_packet(val)

    def send_command(self):
        crc = CRCCCITT().calculate(bytes(self._packet))
        crcMSB = (crc >> 8) & 0xFF
        crcLSB = crc & 0xFF
        self._packet.append(crcMSB)
        self._packet.append(crcLSB)
        self._port.write(bytes(self._packet))
        # self._port.write(bytes(crc))

    def Open(self):
        self._port = serial.Serial(self.comport, self.rate, timeout=self.timeout)
        return self._port.isOpen()

    def ForwardM1(self, address, val):
        self.build_command(address, self.Cmd.M1FORWARD, [val])
        self.send_command()

    def BackwardM1(self, address, val):
        self.build_command(address, self.Cmd.M1BACKWARD, [val])
        self.send_command()

    def ForwardM2(self, address, val):
        self.build_command(address, self.Cmd.M2FORWARD, [val])
        self.send_command()

    def BackwardM2(self, address, val):
        self.build_command(address, self.Cmd.M2BACKWARD, [val])
        self.send_command()

rc = Roboclaw("COM16", 115200)
rc.build_command(0x80, 0, [0x0])
rc.send_command()
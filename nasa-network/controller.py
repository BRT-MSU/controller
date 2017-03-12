import connection
import adbLib as ADBLib
#import motorLib
import enum
import re
import atexit
import signal
import sys

def signalHandler(signal, frame):
    sys.exit(0)

class forwardingPrefix(enum.Enum):
    client = '-c',
    tango = '-t',
    motor = '-m',
    debug = '-d',
    status = '-s'

# Commented out for testing purposes only
CLIENT_IP_ADDRESS = '192.168.1.2'
CLIENT_PORT_NUMBER = 1123

CONTROLLER_IP_ADDRESS = '0.0.0.0'
CONTROLLER_TO_CLIENT_PORT_NUMBER = 5813
CONTROLLER_TO_TANGO_PORT_NUMBER = 2134

TANGO_IP_ADDRESS = '192.168.1.4'
TANGO_PORT_NUMBER = 5589

forwardToClientRegex = re.compile('^' + forwardingPrefix.client[0] + '([\s\S]*)$')
forwardToTangoRegex = re.compile('^' + forwardingPrefix.tango[0] + '([\s\S]*)$')
forwardToMotorRegex = re.compile('^' + forwardingPrefix.motor[0] + '([\s\S]*)$')

debugRegex = re.compile('^' + forwardingPrefix.debug[0] + '([\s\S]*)$')
statusRegex = re.compile('^' + forwardingPrefix.status[0] + '([\s\S]*)$')

class Controller():
    def __init__(self):
        atexit.register(self.shutdown)

        #self.motorConnection = motorLib.connection()
        print forwardingPrefix.client

        self.clientConnection = connection.main(serverIPAddress=CONTROLLER_IP_ADDRESS, serverPortNumber=CONTROLLER_TO_CLIENT_PORT_NUMBER,
                                           clientIPAddress=CLIENT_IP_ADDRESS, clientPortNumber=CLIENT_PORT_NUMBER)

        self.tangoConnection = connection.main(serverIPAddress=CONTROLLER_IP_ADDRESS, serverPortNumber=CONTROLLER_TO_TANGO_PORT_NUMBER,
                                          clientIPAddress=TANGO_IP_ADDRESS, clientPortNumber=TANGO_PORT_NUMBER)

        self.run()

    def run(self):
        ADBLib.startADB()
        while True:
            clientMessage = self.clientConnection.getMessage()
            if clientMessage is not None:
                print 'Controller received the following message from the client:', clientMessage
                self.forwardMessage(clientMessage)

            tangoMessage = self.tangoConnection.getMessage()
            if tangoMessage is not None:
                print 'Controller received the following message from the tango:', tangoMessage
                self.forwardMessage(tangoMessage)

    def forwardMessage(self, message):
        print 'Forwarding message:', message
        if re.match(forwardToClientRegex, message):
             self.clientConnection.send(message)
        elif re.match(forwardToTangoRegex, message):
             self.tangoConnection.send(message)
        elif re.match(forwardToMotorRegex, message):
             print 'Motor controller command sent:', re.match(forwardToMotorRegex, message).group(1)
             #self.motorConnection.parseInstruction(message)

    def shutdown(self):
        self.clientConnection.closeServerSocket()
        self.tangoConnection.closeServerSocket()

def main():
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGTSTP, signalHandler)
    Controller()

if __name__ == '__main__':
    main()

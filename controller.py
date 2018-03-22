import connection
import motor_lib

import enum
import re
import atexit
import signal
import sys


def signal_handler(signal, frame):
    sys.exit(0)


class ForwardingPrefix(enum.Enum):
    CLIENT = '-c'
    MOTOR = '-m'
    CONTROLLER = '-p'
    DEBUG = '-d'
    STATUS = '-s'

# Commented out for testing purposes only
CLIENT_IP_ADDRESS = '192.168.1.2'
CLIENT_PORT_NUMBER = 1123

CONTROLLER_IP_ADDRESS = '0.0.0.0'
CONTROLLER_TO_CLIENT_PORT_NUMBER = 5813
CONTROLLER_TO_TANGO_PORT_NUMBER = 2134

AUTONOMY_ACTIVATION_MESSAGE = 'activate'
AUTONOMY_DEACTIVATION_MESSAGE = 'deactivate'

forwardToClientRegex = re.compile('^' + str(ForwardingPrefix.CLIENT) + '([\s\S]*)$')
forwardToControllerRegex = re.compile('^' + str(ForwardingPrefix.CONTROLLER) + '([\s\S]*)$')
forwardToMotorRegex = re.compile('^' + str(ForwardingPrefix.MOTOR) + '([\s\S]*)$')

debugRegex = re.compile('^' + str(ForwardingPrefix.DEBUG) + '([\s\S]*)$')
statusRegex = re.compile('^' + str(ForwardingPrefix.STATUS) + '([\s\S]*)$')


class Controller:
    def __init__(self):
        atexit.register(self.shutdown)

        self.motorConnection = motor_lib.MotorConnection()

        self.clientConnection = connection.main(serverIPAddress=CONTROLLER_IP_ADDRESS,
                                                serverPortNumber=CONTROLLER_TO_CLIENT_PORT_NUMBER,
                                                clientIPAddress=CLIENT_IP_ADDRESS,
                                                clientPortNumber=CLIENT_PORT_NUMBER)

        self.isAutonomyActivated = False

        self.run()

    def run(self):
        while True:
            clientMessage = self.clientConnection.getMessage()
            if clientMessage is not None:
                print 'Controller received the following message from the client:', clientMessage
                self.forward_message(clientMessage)

    def forward_message(self, message):
        print 'Forwarding message:', message
        if re.match(forwardToClientRegex, message):
            self.clientConnection.send(re.match(forwardToClientRegex, message).group(1))
        elif re.match(forwardToControllerRegex, message):
            if re.match(forwardToControllerRegex, message).group(1) is AUTONOMY_ACTIVATION_MESSAGE:
                self.isAutonomyActivated = True
            elif re.match(forwardToControllerRegex, message).group(1) is AUTONOMY_DEACTIVATION_MESSAGE:
                self.isAutonomyActivated = False
        elif re.match(forwardToMotorRegex, message):
            self.motorConnection.parse_message(re.match(forwardToMotorRegex, message).group(1))

    def shutdown(self):
        self.motorConnection.close()
        self.clientConnection.closeServerSocket()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    Controller()

if __name__ == '__main__':
    main()

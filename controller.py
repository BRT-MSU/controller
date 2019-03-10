import enum
import re
import atexit
import signal
import sys

from connection import Connection
import motor_lib


def signal_handler(signal, frame):
    sys.exit(0)


class ForwardingPrefix(enum.Enum):
    CLIENT = '-c'
    MOTOR = '-m'
    CONTROLLER = '-p'
    DEBUG = '-d'
    STATUS = '-s'

# Commented out for testing purposes only
DEFAULT_CLIENT_IP_ADDRESS = '192.168.1.2'
DEFAULT_CLIENT_PORT_NUMBER = 1123

DEFAULT_CONTROLLER_IP_ADDRESS = '0.0.0.0'
DEFAULT_CONTROLLER_PORT_NUMBER = 5813

DEFAULT_BUFFER_SIZE = 1024

AUTONOMY_ACTIVATION_MESSAGE = 'activate'
AUTONOMY_DEACTIVATION_MESSAGE = 'deactivate'

forward_to_client_regex = re.compile('^' + str(ForwardingPrefix.CLIENT) + '([\s\S]*)$')
forward_to_controller_regex = re.compile('^' + str(ForwardingPrefix.CONTROLLER) + '([\s\S]*)$')
forward_to_motor_regex = re.compile('^' + str(ForwardingPrefix.MOTOR) + '([\s\S]*)$')


class Controller:
    def __init__(self):
        atexit.register(self.shutdown)

        self.motorConnection = motor_lib.MotorConnection(left_drive_address=0x80, right_drive_address=0x80)

        self.clientConnection = Connection(DEFAULT_CONTROLLER_IP_ADDRESS,
                                           DEFAULT_CONTROLLER_PORT_NUMBER,
                                           DEFAULT_CLIENT_IP_ADDRESS,
                                           DEFAULT_CLIENT_PORT_NUMBER,
                                           DEFAULT_BUFFER_SIZE)

        self.isAutonomyActivated = False

        self.run()

    def run(self):
        while True:
            client_message = self.clientConnection.get_message()
            if client_message is not None:
                print 'Controller received the following message from the client:', client_message
                self.forward_message(client_message)

    def forward_message(self, message):
        print 'Forwarding message:', message
        if re.match(forward_to_client_regex, message):
            self.clientConnection.send(re.match(forward_to_client_regex, message).group(1))
        elif re.match(forward_to_controller_regex, message):
            if re.match(forward_to_controller_regex, message).group(1) is AUTONOMY_ACTIVATION_MESSAGE:
                self.isAutonomyActivated = True
            elif re.match(forward_to_controller_regex, message).group(1) is AUTONOMY_DEACTIVATION_MESSAGE:
                self.isAutonomyActivated = False
        elif re.match(forward_to_motor_regex, message):
            motor_message = re.match(forward_to_motor_regex, message).group(1)
            self.motorConnection.parse_message(motor_message)

    def shutdown(self):
        self.motorConnection.close()
        self.clientConnection.close_server_socket()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    Controller()

if __name__ == '__main__':
    main()

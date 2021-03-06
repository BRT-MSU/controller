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
    OBJECT = '-o'

# Commented out for testing purposes only
SPEED = -50
DEFAULT_CLIENT_IP_ADDRESS = '10.152.186.73'
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
                client_message = client_message.decode('utf-8')
                print('Controller received the following message from the client:', client_message)
                self.forward_message(client_message)

    def forward_message(self, message):
        global SPEED
        print('Forwarding message:', message)
        if (message[0]=="w"):
            self.motorConnection.left_drive(SPEED)
            self.motorConnection.right_drive(SPEED)
        elif (message[0]=="s"):
            self.motorConnection.left_drive(-1*SPEED)
            self.motorConnection.right_drive(-1*SPEED)
        elif (message[0]=="a"):
            self.motorConnection.left_drive(50)
            self.motorConnection.right_drive(-50)
        elif (message[0]=="d"):
            self.motorConnection.left_drive(-50)
            self.motorConnection.right_drive(50)
        elif (message[0]=="q"):
            self.motorConnection.bucket_rotate(SPEED)
        elif (message[0]=="e"):
            self.motorConnection.bucket_rotate(-1*SPEED)
        elif (message[0]=="x"):
            self.motorConnection.left_drive(0)
            self.motorConnection.right_drive(0)
            self.motorConnection.bucket_rotate(0)
            self.motorConnection.conveyor_rotate(0)

            self.motorConnection.bucket_actuate(0)
        elif (message[0]=="i"):
            self.motorConnection.bucket_actuate(SPEED)

        elif (message[0]=="k"):
            self.motorConnection.bucket_actuate(-SPEED)

        elif (message[0] == "u"):
            SPEED -= 5
        elif (message[0] == "j"):
            SPEED += 5
        elif (message[0] == "p"):
            self.motorConnection.conveyor_rotate(SPEED)
        print(SPEED)

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

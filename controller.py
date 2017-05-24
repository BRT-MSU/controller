import connection
import motorLib
from gyroscope import GyroscopeController
from gyroBuffer import GyroBuffer

import time
import enum
import re
import atexit
import signal
import sys


def signalHandler(signal, frame):
    sys.exit(0)


class forwardingPrefix(enum.Enum):
    CLIENT = '-c'
    TANGO = '-t'
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

TANGO_IP_ADDRESS = '192.168.1.4'
TANGO_PORT_NUMBER = 5589

ARM_GYROSCOPE_ADDRESS = 0x68

BUCKET_GYROSCOPE_ADDRESS = 0x69

GYROSCOPE_TOLERANCE = 1.5
GYROSCOPE_PRECISION = 1
GYROSCOPE_BUFFER_SIZE = 20

DEFAULT_TIME_DELAY = 0.1

MAX_ACTUATOR_ANGLE = 30.0

AUTONOMY_ACTIVATION_MESSAGE = 'activate'
AUTONOMY_DEACTIVATION_MESSAGE = 'deactivate'

forwardToClientRegex = re.compile('^' + forwardingPrefix.CLIENT + '([\s\S]*)$')
forwardToControllerRegex = re.compile('^' + forwardingPrefix.CONTROLLER + '([\s\S]*)$')
forwardToTangoRegex = re.compile('^' + forwardingPrefix.TANGO + '([\s\S]*)$')
forwardToMotorRegex = re.compile('^' + forwardingPrefix.MOTOR + '([\s\S]*)$')

debugRegex = re.compile('^' + forwardingPrefix.DEBUG + '([\s\S]*)$')
statusRegex = re.compile('^' + forwardingPrefix.STATUS + '([\s\S]*)$')


class Controller():
    def __init__(self):
        atexit.register(self.shutdown)

        self.motorConnection = motorLib.MotorConnection(self)

        self.armGyroConnection = GyroscopeController(address=ARM_GYROSCOPE_ADDRESS)
        self.bucketGyroConnection = GyroscopeController(address=BUCKET_GYROSCOPE_ADDRESS)

        self.clientConnection = connection.main(serverIPAddress=CONTROLLER_IP_ADDRESS, serverPortNumber=CONTROLLER_TO_CLIENT_PORT_NUMBER,
                                           clientIPAddress=CLIENT_IP_ADDRESS, clientPortNumber=CLIENT_PORT_NUMBER)

        self.tangoConnection = connection.main(serverIPAddress=CONTROLLER_IP_ADDRESS, serverPortNumber=CONTROLLER_TO_TANGO_PORT_NUMBER,
                                          clientIPAddress=TANGO_IP_ADDRESS, clientPortNumber=TANGO_PORT_NUMBER)

        self.isAutonomyActivated = False

        # Gyroscope variables
        self.armGyroBuffer = GyroBuffer(GYROSCOPE_BUFFER_SIZE)
        self.bucketGyroBuffer = GyroBuffer(GYROSCOPE_BUFFER_SIZE)

        self.armRotation = 0.0
        self.bucketRotation = 0.0

        self.isActuatorMovingUp = False

        self.lastTimeCheck = time.time()

        self.isActuatorMoving = False
        self.isBucketMoving = False

        self.run()

    def run(self):
        while True:
            clientMessage = self.clientConnection.getMessage()
            if clientMessage is not None:
                print 'Controller received the following message from the client:', clientMessage
                self.forwardMessage(clientMessage)

            tangoMessage = self.tangoConnection.getMessage()
            if self.isAutonomyActivated and tangoMessage is not None:
                print 'Controller received the following message from the tango:', tangoMessage
                self.forwardMessage(tangoMessage)


            # Collect gyroscope information and send it to the client.
            try:
                armRotation = -1 * self.armGyroConnection.getXRotation()
                self.armGyroBuffer.add(armRotation)
            except IOError:
                pass

            try:
                bucketRotation = -1 * self.bucketGyroConnection.getYRotation()
                self.bucketGyroBuffer.add(bucketRotation)
            except IOError:
                pass

            averageArmRotation = self.armGyroBuffer.computeAverage()
            averageBucketRotation = self.bucketGyroBuffer.computeAverage()

            timeCheck = time.time()

            # Only send gyroscope information at intervals when the arms or bucket is moving
            if timeCheck - self.lastTimeCheck > DEFAULT_TIME_DELAY and (self.isActuatorMoving or self.isBucketMoving):
                self.clientConnection.send(forwardingPrefix.CLIENT + 'a' + str(round(averageArmRotation, GYROSCOPE_PRECISION)) + \
                                               'b' + str(round(averageBucketRotation, GYROSCOPE_PRECISION)))

                self.lastTimeCheck = timeCheck

            self.armRotation = averageArmRotation
            self.bucketRotation = averageBucketRotation

            if self.armRotation > MAX_ACTUATOR_ANGLE and self.isActuatorMovingUp:
                # if the arm rotation is greater than the maximum actuator angle, we send
                # an emergency stop command
                self.motorConnection.parseMessage('a0|')

    def forwardMessage(self, message):
        print 'Forwarding message:', message
        if re.match(forwardToClientRegex, message):
            self.clientConnection.send(re.match(forwardToClientRegex, message).group(1))
        elif re.match(forwardToControllerRegex, message):
            if re.match(forwardToControllerRegex, message).group(1) is AUTONOMY_ACTIVATION_MESSAGE:
                self.isAutonomyActivated = True
                self.tangoConnection.send(AUTONOMY_ACTIVATION_MESSAGE)
            elif re.match(forwardToControllerRegex, message).group(1) is AUTONOMY_DEACTIVATION_MESSAGE:
                self.isAutonomyActivated = False
        elif re.match(forwardToTangoRegex, message):
            self.tangoConnection.send(re.match(forwardToTangoRegex, message).group(1))
        elif re.match(forwardToMotorRegex, message):
            self.motorConnection.parseMessage(re.match(forwardToMotorRegex, message).group(1))

    def shutdown(self):
        self.motorConnection.close()
        self.clientConnection.closeServerSocket()
        self.tangoConnection.closeServerSocket()


def main():
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    signal.signal(signal.SIGTSTP, signalHandler)
    Controller()


if __name__ == '__main__':
    main()

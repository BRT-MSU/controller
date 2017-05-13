from roboclaw import Roboclaw
import re
import enum
import time

DEFAULT_TIME_TO_DELAY_MOTOR = 0.02  # delay for 20 milliseconds
MAX_MOTOR_SPEED = 100  # max speed from client
MAX_MOTOR_POWER = 120  # max power to motor controllers (Max value for drive methods)

motorMessageRegex = re.compile('([\w])([-]*[\d]+)\|')

class subMessagePrefix(enum.Enum):
    LEFT_MOTOR = 'l'
    RIGHT_MOTOR = 'r'
    ACTUATOR = 'a'
    BUCKET = 'b'
    SERVO = 's'

class roboclawStatus(enum.Enum):
    CONNECTED = 'Roboclaw Connected'
    DISCONNECTED = 'Roboclaw Disconnected'

class MotorConnection():
    def __init__(self, communicationPort = '/dev/roboclaw', baudRate = 115200,
                 driveAddress = 0x80, bucketAddress = 0x81):
        print 'MotorConnnection initialized.'
        self.controller = Roboclaw(communicationPort, baudRate)
        self.status = roboclawStatus.CONNECTED if self.controller.Open() else roboclawStatus.DISCONNECTED
        self.driveAddress = driveAddress

        self.bucketAddress = bucketAddress

        self.leftMotorSpeed = 0
        self.rightMotorSpeed = 0
        self.actuatorMotorSpeed = 0
        self.bucketMotorSpeed = 0

    def directionOfSpeed(self, speed):
        if speed >= 0:
            return 1
        else:
            return -1

    def areSpeedDirectionsEqual(self, speed1, speed2):
        if self.directionOfSpeed(speed1) is self.directionOfSpeed(speed2):
            return True
        else:
            return False

    def convertSpeedToPower(self, speed):
        if abs(speed) > MAX_MOTOR_SPEED:
            return 0
        else:
            powerPercentage = float(speed) / float(MAX_MOTOR_SPEED)
            power = int(powerPercentage * float(MAX_MOTOR_POWER))
            return power

    def leftDrive(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.leftMotorSpeed):
            print 'Left motor speed changed direction.'
            self.controller.ForwardM1(self.driveAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Left motor at speed:', speed, '%'
        self.leftMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Left motor at power:', power
        if power >= 0:
            self.controller.ForwardM1(self.driveAddress, power)
        else:
            self.controller.BackwardM1(self.driveAddress, abs(power))

    def rightDrive(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.rightMotorSpeed):
            print 'Right motor speed changed direction.'
            self.controller.ForwardM2(self.driveAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Right motor at speed:', speed, '%'
        self.rightMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Right motor at power:', power
        if power >= 0:
            self.controller.ForwardM2(self.driveAddress, power)
        else:
            self.controller.BackwardM2(self.driveAddress, abs(power))

    def bucketActuate(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.actuatorMotorSpeed):
            print 'Actuator motor speed changed direction.'
            self.controller.ForwardM1(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Actuator motor at speed:', speed, '%'
        self.actuatorMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Actuator motor at power:', power
        if power >= 0:
            self.controller.ForwardM1(self.bucketAddress, power)
        else:
            self.controller.BackwardM1(self.bucketAddress, abs(power))

    def bucketRotate(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.bucketMotorSpeed):
            print 'Bucket motor speed changed direction.'
            self.controller.ForwardM2(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Bucket motor at speed:', speed, '%'
        self.bucketMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Bucket motor at power:', power
        if power >= 0:
            self.controller.ForwardM2(self.bucketAddress, power)
        else:
            self.controller.BackwardM2(self.bucketAddress, abs(power))

    def parseMessage(self, message):
        subMessages = motorMessageRegex.findall(message)

        for subMessage in subMessages:
            motorPrefix = subMessage[0]
            speed = int(subMessage[1])
            try:
                if motorPrefix == subMessagePrefix.LEFT_MOTOR:
                    self.leftDrive(speed)
                elif motorPrefix == subMessagePrefix.RIGHT_MOTOR:
                    self.rightDrive(speed)
                elif motorPrefix == subMessagePrefix.ACTUATOR:
                    self.bucketActuate(speed)
                elif motorPrefix == subMessagePrefix.BUCKET:
                    self.bucketRotate(speed)
                else:
                    print 'MotorPrefix "', motorPrefix, '" unrecognized.'
            except AttributeError:
                self.status = roboclawStatus.DISCONNECTED
                print 'Roboclaw disconnected...retrying connection'
                if self.controller.Open():
                    print 'Roboclaw connected...retrying command'
                    self.status = roboclawStatus.CONNECTED
                    self.parseMessage(message)

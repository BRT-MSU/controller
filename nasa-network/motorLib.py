#from roboclaw import Roboclaw
#import enum
import re
import enum

class subMessagePrefix(enum.Enum):
    LEFT_MOTOR = 'l'
    RIGHT_MOTOR = 'r'
    ACTUATOR = 'a'
    BUCKET = 'b'
    SERVO = 's'

motorMessageRegex = re.compile('([\w])([-]*[\d]+)\|')

class MotorConnection():
    def __init__(self, communicationPort = '/dev/roboclaw', baudRate = 115200,
                 driveAddress = '0x80', bucketAddress = '0x81'):
        print 'MotorConnnection initialized.'
        #self.controller = Roboclaw(communicationPort, baudRate)
        #self.controller.open()
        #self.driveAddress = driveAddress

        #self.bucketAddress = bucketAddress

    def leftDrive(self, speed):
        print 'Left motor at speed:', speed
        #self.controller.SpeedM1(driveAddress, speed)

    def rightDrive(self, speed):
        print 'Right motor at speed:', speed
        #self.controller.SpeedM2(driveAddress, speed)

    def bucketActuate(self, speed):
        print 'Actuator motor at speed:', speed
        #self.controller.SpeedM1(bucketAddress, value)

    def bucketRotate(self, speed):
        print 'Bucket motor at speed:', speed
        #self.controller.SpeedM2(bucketAddress, value)

    def parseMessage(self, message):
        subMessages = motorMessageRegex.findall(message)

        for subMessage in subMessages:
            motorPrefix = subMessage[0]
            speed = subMessage[1]

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














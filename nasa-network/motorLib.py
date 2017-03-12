from roboclaw import Roboclaw
import enum


class Controller:
    def __init__(self, communicationPort = '/dev/roboclaw', baudRate = 115200,
                 driveAddress = '0x80', bucketAddress = '0x81'):
        self.controller = Roboclaw(communicationPort, baudRate)
        self.controller.open()
        self.driveAddress = driveAddress

        self.bucketAddress = bucketAddress

    def leftDrive(self, speed):
        self.controller.SpeedM1(driveAddress, speed)

    def rightDrive(self, speed):
        self.controller.SpeedM2(driveAddress, speed)

    def bucketActuate(self, value):
        self.controller.SpeedM1(bucketAddress, value)

    def bucketRotate(self, value):
        self.controller.SpeedM2(bucketAddress, value)

    def parseInstruction(self, instruction):
        print 'Maybe one day I will understand %s \n:(' % instruction












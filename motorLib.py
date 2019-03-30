from roboclaw import Roboclaw

class MotorLib:

    def __init__(self):
        self.rc = Roboclaw("/dev/ttyACM2", 115200)
        self.rc.Open()
        self.M1 = 63
        self.M2 = 63


    def move(self, speed):
        self.M1 += speed
        self.M2 += speed
        self.setMotors()

    def left(self, speed):
        self.M1 += speed
        self.setMotors()

    def left(self, speed):
        self.M2 += speed
        self.setMotors()

    def setMotors(self):
        self.rc.ForwardBackwardM1(0x80, self.M1)
        self.rc.ForwardBackwardM2(0x80, self.M2)
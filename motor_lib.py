import re
import enum
import time
from roboclaw import Roboclaw
from drive_motor import DriveMotor

DEFAULT_RIGHT_DRIVE_MOTOR_ADDRESS = '/dev/ttyUSB0'
DEFAULT_LEFT_DRIVE_MOTOR_ADDRESS = '/dev/ttyUSB1'

DEFAULT_TIME_TO_DELAY_MOTOR = 20  # 20 milliseconds

MAX_MOTOR_SPEED = 100  # max speed from client
MAX_MOTOR_POWER = 120  # max power to bucket motor controller
MAX_DRIVE_MOTOR_RPM = 4000  # max rpm for to drive motor controllers


motorMessageRegex = re.compile('([\w])([-]*[\d]+)\|')
servoTTYAddressRegex = re.compile('/dev/ttyACM([\d]+)')   


class SubMessagePrefix(enum.Enum):
    LEFT_MOTOR = 'l'
    RIGHT_MOTOR = 'r'
    ACTUATOR = 'a'
    BUCKET = 'b'
    SERVO = 's'


class RoboclawStatus(enum.Enum):
    CONNECTED = 'Roboclaw Connected'
    DISCONNECTED = 'Roboclaw Disconnected'


class MotorConnection:
    def __init__(self, roboclaw_port='/dev/roboclaw',
                 baud_rate=115200, bucket_address=0x80):
        self.right_motor = DriveMotor(DEFAULT_RIGHT_DRIVE_MOTOR_ADDRESS)
        self.left_motor = DriveMotor(DEFAULT_LEFT_DRIVE_MOTOR_ADDRESS)

        self.roboclaw = Roboclaw(roboclaw_port, baud_rate)
        
        if self.roboclaw.Open():
            self.status = RoboclawStatus.CONNECTED
        else:
            self.status = RoboclawStatus.DISCONNECTED
            
        print self.status
        print 'MotorConnection initialized.'

        self.bucketAddress = bucket_address

        self.left_motor_speed = 0
        self.right_motor_speed = 0
        self.actuator_motor_speed = 0
        self.bucket_motor_speed = 0

    @staticmethod
    def direction_of_speed(speed):
        if speed >= 0:
            return 1
        else:
            return -1

    def are_speed_directions_equal(self, speed1, speed2):
        if self.direction_of_speed(speed1) is self.direction_of_speed(speed2):
            return True
        else:
            return False

    @staticmethod
    def convert_speed_to_power(speed):
        if abs(speed) > MAX_MOTOR_SPEED:
            return 0
        else:
            power_percentage = float(speed) / float(MAX_MOTOR_SPEED)
            power = int(power_percentage * float(MAX_MOTOR_POWER))
            return power

    @staticmethod
    def convert_speed_to_rpm(speed):
        if abs(speed) > MAX_MOTOR_SPEED:
            return 0
        else:
            power_percentage = float(speed) / float(MAX_MOTOR_SPEED)
            power = int(power_percentage * float(MAX_DRIVE_MOTOR_RPM))
            return power

    def left_drive(self, speed):
        print 'Left motor at speed:', speed, '%'
        self.left_motor_speed = speed
        rpm = self.convert_speed_to_rpm(speed)
        print 'Left motor at rpm:', rpm
        self.left_motor.drive(rpm)

    def right_drive(self, speed):
        print 'Right motor at speed:', speed, '%'
        self.right_motor_speed = speed
        rpm = self.convert_speed_to_rpm(speed)
        print 'Right motor at rpm:', rpm
        self.right_motor.drive(rpm)

    def bucket_actuate(self, speed):
        if not self.are_speed_directions_equal(speed, self.actuator_motor_speed):
            print 'Actuator motor speed changed direction.'
            self.roboclaw.ForwardM1(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Actuator motor at speed:', speed, '%'
        self.actuator_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print 'Actuator motor at power:', power
        if power >= 0:
            self.roboclaw.ForwardM1(self.bucketAddress, power)
        else:
            self.roboclaw.BackwardM1(self.bucketAddress, abs(power))

    def bucket_rotate(self, speed):
        if not self.are_speed_directions_equal(speed, self.bucket_motor_speed):
            print 'Bucket motor speed changed direction.'
            self.roboclaw.ForwardM2(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Bucket motor at speed:', speed, '%'
        self.bucket_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print 'Bucket motor at power:', power
        if power >= 0:
            self.roboclaw.ForwardM2(self.bucketAddress, power)
        else:
            self.roboclaw.BackwardM2(self.bucketAddress, abs(power))

    def parse_message(self, message):
        sub_messages = motorMessageRegex.findall(message)

        for sub_message in sub_messages:
            motor_prefix = sub_message[0]
            speed = int(sub_message[1])
            try:
                if motor_prefix == SubMessagePrefix.LEFT_MOTOR:
                    self.left_drive(speed)
                elif motor_prefix == SubMessagePrefix.RIGHT_MOTOR:
                    self.right_drive(speed)
                elif motor_prefix == SubMessagePrefix.ACTUATOR:
                    self.bucket_actuate(speed)
                elif motor_prefix == SubMessagePrefix.BUCKET:
                    self.bucket_rotate(speed)
                else:
                    print 'MotorPrefix "', motor_prefix, '" unrecognized.'
            except AttributeError:
                self.status = RoboclawStatus.DISCONNECTED
                print 'Roboclaw disconnected...retrying connection'
                if self.roboclaw.Open():
                    print 'Roboclaw connected...retrying command'
                    self.status = RoboclawStatus.CONNECTED
                    self.parse_message(message)

    def close(self):
        print 'Closed connection:', self.roboclaw.Close()

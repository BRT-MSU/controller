import re
import enum
import time
from threading import Thread
from roboclaw import Roboclaw
import maestro

DEFAULT_TIME_TO_DELAY_MOTOR = 0.02  # 20 milliseconds

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

"""
    To set /dev/roboclaw using udev rules, follow thise guide:
    https://www.linux.com/learn/build-road-raspberry-pi-robot-part-2
"""
class MotorConnection:
    def __init__(self, roboclaw_port='/dev/roboclaw',
                 baud_rate=115200, 
                 left_drive_address=0x82, right_drive_address=0x83,
                 actuator_address=0x80, dig_address=0x83, conveyorAddress=0x81):

        self.roboclaw = Roboclaw(roboclaw_port, baud_rate)
        
        if self.roboclaw.Open():
            self.status = RoboclawStatus.CONNECTED
        else:
            self.status = RoboclawStatus.DISCONNECTED
            
        print(self.status)
        print('MotorConnection initialized.')

        self.left_drive_address = left_drive_address
        self.right_drive_address = right_drive_address
        self.actuator_address = actuator_address
        self.dig_address = dig_address
        self.conveyorAddress = conveyorAddress
        self.bucketAddress = 0x81

        self.left_motor_speed = 0
        self.right_motor_speed = 0
        self.actuator_motor_speed = 0
        self.bucket_motor_speed = 0


        self.camera_actuator_speed = 0
        self.camera_servo_speed = 0

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
        if not self.are_speed_directions_equal(speed, self.left_motor_speed):
            print('Left motor speed changed direction.')
            self.roboclaw.ForwardM2(self.left_drive_address, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print('Left motor at speed:', speed, '%')
        self.left_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print('Left motor at power:', power)
        if power >= 0:
            self.roboclaw.BackwardM2(self.left_drive_address, power)
            self.roboclaw.BackwardM1(self.left_drive_address, power)
        else:
            self.roboclaw.ForwardM2(self.left_drive_address, abs(power))
            self.roboclaw.ForwardM1(self.left_drive_address, abs(power))

    def right_drive(self, speed):
        if not self.are_speed_directions_equal(speed, self.right_motor_speed):
            print('Left motor speed changed direction.')
            self.roboclaw.ForwardM1(self.right_drive_address, 0)
            self.roboclaw.ForwardM2(self.right_drive_address, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print('Right motor at speed:', speed, '%')
        self.right_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print('Right motor at power:', power)
        if power >= 0:
            self.roboclaw.BackwardM1(self.right_drive_address, power)
            self.roboclaw.BackwardM2(self.right_drive_address, power)
        else:
            self.roboclaw.ForwardM1(self.right_drive_address, abs(power))
            self.roboclaw.ForwardM2(self.right_drive_address, abs(power))


    def camera_actuate(self, speed):
        pass

    def camera_rotate(self, speed):
        pass



    def bucket_actuate(self, speed):
        if not self.are_speed_directions_equal(speed, self.actuator_motor_speed):
            print('Actuator motor speed changed direction.')
            self.roboclaw.ForwardM1(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print('Actuator motor at speed:', speed, '%')
        self.actuator_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print('Actuator motor at power:', power)
        if power >= 0:
            self.roboclaw.BackwardM1(self.bucketAddress, power)
        else:
            self.roboclaw.ForwardM1(self.bucketAddress, abs(power))

    def bucket_rotate(self, speed):
        if not self.are_speed_directions_equal(speed, self.bucket_motor_speed):
            print('Bucket motor speed changed direction.')
            self.roboclaw.ForwardM1(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print('Bucket motor at speed:', speed, '%')
        self.bucket_motor_speed = speed
        power = self.convert_speed_to_power(speed)
        print('Bucket motor at power:', power)
        if power >= 0:
            self.roboclaw.BackwardM1(self.bucketAddress, power)
        else:
            self.roboclaw.ForwardM1(self.bucketAddress, abs(power))
    def conveyor_rotate(self, speed):
        #Change direction code missing
        speed_conveyor=speed
        power=self.convert_speed_to_power(speed)
        self.roboclaw.ForwardM1(self.conveyorAddress, abs(power))
        # motor1=self.roboclaw.ReadEncM1(0x83)
        # print(motor1)
        # self.roboclaw.SpeedM1(0x83, 8)
    def parse_message(self, message):
        sub_messages = motorMessageRegex.findall(message)

        threads = []

        for sub_message in sub_messages:
            motor_prefix = sub_message[0]
            speed = int(sub_message[1])
            try:
                if motor_prefix == SubMessagePrefix.LEFT_MOTOR:
                    left_motor_thread = Thread(name='leftMotorThread',
                                               target=self.left_drive(-speed))
                    threads.append(left_motor_thread)
                    left_motor_thread.start()

                elif motor_prefix == SubMessagePrefix.RIGHT_MOTOR:
                    right_motor_thread = Thread(name='rightMotorThread',
                                                target=self.right_drive(speed))
                    threads.append(right_motor_thread)
                    right_motor_thread.start()

                elif motor_prefix == SubMessagePrefix.ACTUATOR:
                    actuator_thread = Thread(name='actuatorThread',
                                             target=self.bucket_actuate(speed))
                    threads.append(actuator_thread)
                    actuator_thread.start()
                elif motor_prefix == SubMessagePrefix.BUCKET:
                    bucket_thread = Thread(name='bucketThread',
                                           target=self.bucket_rotate(speed))
                    threads.append(bucket_thread)
                    bucket_thread.start()
                else:
                    print('MotorPrefix "', motor_prefix, '" unrecognized.')
            except AttributeError:
                self.status = RoboclawStatus.DISCONNECTED
                print('Roboclaw disconnected...retrying connection')
                if self.roboclaw.Open():
                    print('Roboclaw connected...retrying command')
                    self.status = RoboclawStatus.CONNECTED
                    #self.parse_message(message)

        for thread in threads:
            thread.join()

    def close(self):
        print('Closed connection:', self.roboclaw.Close())

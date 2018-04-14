import argparse
from time import sleep
import serial


class DriveMotor:
    def __init__(self, port_name):
        self.serial_connection = serial.Serial(port=port_name,
                                               baudrate=38400,
                                               timeout=0.5,
                                               xonxoff=True)

    def drive(self, rpm):
        if abs(rpm) > 4000:
            return -1

        if abs(rpm) < 100:
            self.serial_connection.write('@#.\r')
            return 0

        if rpm >= 100:
            self.serial_connection.write('@#+\r')
            sleep(0.05)
        else:
            self.serial_connection.write('@#-\r')
            sleep(0.05)

        self.serial_connection.write('@#M' + str(rpm) + '\r')
        sleep(0.005)

        self.serial_connection.write('@#S\r')

        return 0

    def close_connection(self):
        self.serial_connection.close()


def main(port_name):
    drive_motor = DriveMotor(port_name)

    drive_motor.drive(2000)

    sleep(30)

    drive_motor.drive(-2000)

    sleep(30)

    drive_motor.drive(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--portName',
                        help='port name',
                        required=True)

    args = parser.parse_args()

    main(args.portName)

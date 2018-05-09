import argparse
from time import sleep
import serial


class DriveMotor:
    def __init__(self, port_name, address):
        self.serial_connection = serial.Serial(port=port_name,
                                               baudrate=38400,
                                               timeout=0.5,
                                               xonxoff=True)

        self.address = address

        self.serial_connection.write('@~' + str(self.address) + '\r')
        sleep(0.05)

        self.serial_connection.write('@' + str(self.address) + 'D\r')
        sleep(0.05)

    def drive(self, rpm):
        if abs(rpm) > 4000:
            return -1

        if abs(rpm) < 100:
            self.serial_connection.write('@' + str(self.address) + '.\r')
            sleep(0.05)

            return 0

        if rpm >= 100:
            self.serial_connection.write('@' + str(self.address) + '+\r')
            sleep(0.05)
        else:
            self.serial_connection.write('@' + str(self.address) + '-\r')
            sleep(0.05)

        self.serial_connection.write('@' + str(self.address) + 'M'
                                     + str(abs(rpm)) + '\r')
        sleep(0.05)

        self.serial_connection.write('@' + str(self.address) + 'S\r')
        sleep(0.05)

        return 0

    def close_connection(self):
        self.serial_connection.close()


def main(port_name):
    DriveMotor(port_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--portName',
                        help='port name',
                        required=True)

    args = parser.parse_args()

    main(args.portName)

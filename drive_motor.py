import argparse
from time import sleep
import serial

DEFAULT_SERIAL_DELAY = 0.05


class DriveMotor:
    def __init__(self, port_name, address=0):
        self.serial_connection = serial.Serial(port=port_name,
                                               baudrate=38400,
                                               timeout=0.5,
                                               xonxoff=True)

        self.address = address

        self.serial_connection.write('@~' + str(self.address) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) + 'D\r')
        sleep(DEFAULT_SERIAL_DELAY)

    def drive(self, rpm):
        if abs(rpm) > 4000:
            return -1

        if abs(rpm) < 100:
            self.serial_connection.write('@' + str(self.address) + '.\r')
            sleep(DEFAULT_SERIAL_DELAY)

            return 0

        if rpm >= 100:
            self.serial_connection.write('@' + str(self.address) + '+\r')
            sleep(DEFAULT_SERIAL_DELAY)
        else:
            self.serial_connection.write('@' + str(self.address) + '-\r')
            sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) + 'M'
                                     + str(abs(rpm)) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) + 'S\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) + 'VS\r')
        sleep(DEFAULT_SERIAL_DELAY)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) + ' rpm set to: ' + response

        self.serial_connection.write('@' + str(self.address) + 'VM\r')
        sleep(DEFAULT_SERIAL_DELAY + 10)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) + ' running at: ' + response

        return 0

    def set_gain_constant(self, constant):
        self.serial_connection.write('@' + str(self.address)
                                     + 'KG' + str(constant) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) +
                                     'VKG\r')
        sleep(DEFAULT_SERIAL_DELAY)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) \
              + ' gain constant (kg) set to: ' + response

    def set_integrator_constant(self, constant):
        self.serial_connection.write('@' + str(self.address)
                                     + 'KI' + str(constant) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) +
                                        'VKI\r')
        sleep(DEFAULT_SERIAL_DELAY)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) \
              +  ' integrator constant (ki) set to: ' + response

    def set_proportional_constant(self, constant):
        self.serial_connection.write('@' + str(self.address)
                                     + 'KP' + str(constant) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) +
                                     'VKP\r')
        sleep(DEFAULT_SERIAL_DELAY)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) \
              + ' proportional constant (kp) set to: ' + response

    def set_initial_value_constant(self, constant):
        self.serial_connection.write('@' + str(self.address)
                                     + 'IV' + str(constant) + '\r')
        sleep(DEFAULT_SERIAL_DELAY)

        self.serial_connection.write('@' + str(self.address) +
                                        'VIV\r')
        sleep(DEFAULT_SERIAL_DELAY)
        response = self.serial_connection.read(10)
        print 'motor ' + str(self.address) \
              +  ' initial value constant (iv) set to: ' + response

    def close_connection(self):
        self.serial_connection.close()


def main(port_name, gain_constant,
         integrator_constant,
         proportional_constant,
         initial_value_constant):
    drive_motor = DriveMotor(port_name)

    if gain_constant is not None:
        drive_motor.set_gain_constant(gain_constant)

    if integrator_constant is not None:
        drive_motor.set_integrator_constant(integrator_constant)

    if proportional_constant is not None:
        drive_motor.set_proportional_constant(proportional_constant)

    if initial_value_constant is not None:
        drive_motor.set_initial_value_constant(initial_value_constant)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--portName',
                        help='port name',
                        required=True)
    parser.add_argument('-kg', '--gainConstant',
                        help='gain constant',
                        required=False)
    parser.add_argument('-ki', '--integratorConstant',
                        help='integrator constant',
                        required=False)
    parser.add_argument('-kp', '--proportionalConstant',
                        help='proportional constant',
                        required=False)
    parser.add_argument('-iv', '--initialValueConstant',
                        help='initial value constant',
                        required=False)

    args = parser.parse_args()

    main(args.portName, args.gainConstant,
         args.integratorConstant, args.proportionalConstant,
         args.initialValueConstant)

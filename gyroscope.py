import smbus
import math

class GyroscopeController:
    def __init__(self, bus=1, address=0x68):
        # Power management registers
        power_mgmt_1 = 0x6b

        self.bus = smbus.SMBus(bus)  # or bus = smbus.SMBus(1) for Revision 2 boards
        self.address = address  # This is the address value read via the i2cdetect command

        # Now wake the 6050 up as it starts in sleep mode
        while(True):
            try:
                self.bus.write_byte_data(self.address, power_mgmt_1, 0)
                break
            except IOError:
                pass

    def readByte(self, adr):
        return self.bus.read_byte_data(self.address, adr)

    def readWord(self, adr):
        high = self.bus.read_byte_data(self.address, adr)
        low = self.bus.read_byte_data(self.address, adr + 1)
        val = (high << 8) + low
        return val

    def readWord2c(self, adr):
        val = self.readWord(adr)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def getXRotation(self):
        accel_xout = self.readWord2c(0x3b)
        accel_yout = self.readWord2c(0x3d)
        accel_zout = self.readWord2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x = accel_xout_scaled
        y = accel_yout_scaled
        z = accel_zout_scaled

        radians = math.atan2(y, self.distance(x, z))
        return math.degrees(radians)

    def getYRotation(self):
        accel_xout = self.readWord2c(0x3b)
        accel_yout = self.readWord2c(0x3d)
        accel_zout = self.readWord2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x = accel_xout_scaled
        y = accel_yout_scaled
        z = accel_zout_scaled

        radians = math.atan2(x, self.distance(y, z))
        return -math.degrees(radians)

    def distance(self, a, b):
        return math.sqrt((a * a) + (b * b))

def main():
    gyroscopeController = GyroscopeController()

    print "gyro data"
    print "---------"

    gyro_xout = gyroscopeController.readWord2c(0x43)
    gyro_yout = gyroscopeController.readWord2c(0x45)
    gyro_zout = gyroscopeController.readWord2c(0x47)

    print "gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131)
    print "gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131)
    print "gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131)

    print
    print "accelerometer data"
    print "------------------"

    accel_xout = gyroscopeController.readWord2c(0x3b)
    accel_yout = gyroscopeController.readWord2c(0x3d)
    accel_zout = gyroscopeController.readWord2c(0x3f)

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    print "accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled
    print "accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled
    print "accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled

    print "x rotation: ", gyroscopeController.getXRotation()

    print "y rotation: ", gyroscopeController.getYRotation()


if __name__ == '__main__':
    main()
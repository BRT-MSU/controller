import serial


class Controller:
    """
    When connected via USB, the Maestro creates two virtual serial ports
    /dev/ttyACM0 for commands and /dev/ttyACM1 for communications.
    Be sure the Maestro is configured for "USB Dual Port" serial mode.
    "USB Chained Mode" may work as well, but hasn't been tested.
    Pololu protocol allows for multiple Maestros to be connected to a single
    serial port. Each connected device is then indexed by number.
    This device number defaults to 0x0C (or 12 in decimal), which this module
    assumes.  If two or more controllers are connected to different serial
    ports, or you are using a Windows OS, you can provide the tty port.  For
    example, '/dev/ttyACM2' or for Windows, something like 'COM3'.
    """
    def __init__(self, tty_address='/dev/ttyACM1', device=0x0c):
        # Open the command port
        self.usb = serial.Serial(tty_address)
        # Command lead-in and device number are sent for each Pololu serial command.
        self.pololu_command = chr(0xaa) + chr(device)

    """
    Cleanup by closing USB serial port
    """
    def close(self):
        self.usb.close()

    """
    Send a Pololu command out the serial port
    """
    def send_command(self, command):
        command_string = self.pololu_command + command
        #command_string = command_string.encode()
        self.usb.write(command_string)


class Servo:
    def __init__(self, controller, channel):
        self.controller = controller
        self.channel = channel
        self.min = 3000
        self.max = 9000
        self.target = 6000

    """
    Set channels min and max value range.  Use this as a safety to protect
    from accidentally moving outside known safe parameters. A setting of 0
    allows unrestricted movement.
    ***Note that the Maestro itself is configured to limit the range of servo travel
    which has precedence over these values.  Use the Maestro Control Center to configure
    ranges that are saved to the controller.  Use set_range for software controllable ranges.
    """
    def set_range(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    """
    Return Minimum channel range value
    """
    def get_min(self):
        return self.min

    # Return Maximum channel range value
    def get_max(self):
        return self.max

    """
    Set channel to a specified target value.  Servo will begin moving based
    on Speed and Acceleration parameters previously set.
    Target values will be constrained within min and max range, if set.
    For servos, target represents the pulse width in of quarter-microseconds
    Servo center is at 1500 microseconds, or 6000 quarter-microseconds
    Typcially valid servo range is 3000 to 9000 quarter-microseconds
    If channel is configured for digital output, values < 6000 = Low ouput
    """
    def set_target(self, target):
        # if min is defined and Target is below, force to Min
        if self.min > 0 and target < self.min:
            target = self.min
        # if max is defined and Target is above, force to Max
        if 0 < self.max < target:
            target = self.max
        #
        lsb = target & 0x7f  # 7 bits for least significant byte
        msb = (target >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        command = chr(0x04) + chr(self.channel) + chr(lsb) + chr(msb)
        self.controller.send_command(command)
        # Record Target value
        self.target = target

    """
    Set speed of channel
    Speed is measured as 0.25microseconds/10milliseconds
    For the standard 1ms pulse width change to move a servo between extremes, a speed
    of 1 will take 1 minute, and a speed of 60 would take 1 second.
    Speed of 0 is unrestricted.
    """
    def set_speed(self, speed):
        lsb = speed & 0x7f  # 7 bits for least significant byte
        msb = (speed >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        command = chr(0x07) + chr(self.channel) + chr(lsb) + chr(msb)
        self.controller.send_command(command)

    """
    Set acceleration of channel
    This provide soft starts and finishes when servo moves to target position.
    Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start.
    A value of 1 will take the servo about 3s to move between 1ms to 2ms range.
    """
    def set_acceleration(self, accel):
        lsb = accel & 0x7f  # 7 bits for least significant byte
        msb = (accel >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        command = chr(0x09) + chr(self.channel) + chr(lsb) + chr(msb)
        self.controller.send_command(command)

    """
    Get the current position of the device on the specified channel
    The result is returned in a measure of quarter-microseconds, which mirrors
    the Target parameter of setTarget.
    This is not reading the true servo position, but the last target position sent
    to the servo. If the Speed is set to below the top speed of the servo, then
    the position result will align well with the acutal servo position, assuming
    it is not stalled or slowed.
    """
    def get_position(self):
        command = chr(0x10) + chr(self.channel)
        self.controller.send_command(command)
        lsb = ord(self.controller.usb.read())
        msb = ord(self.controller.usb.read())
        return (msb << 8) + lsb

    """
    Test to see if a servo has reached the set target position.  This only provides
    useful results if the Speed parameter is set slower than the maximum speed of
    the servo.  Servo range must be defined first using set_range. See set_range comment.
    ***Note if target position goes outside of Maestro's allowable range for the
    channel, then the target can never be reached, so it will appear to always be
    moving to the target.  
    """
    def is_moving(self):
        if self.target > 0:
            if self.get_position() != self.target:
                return True
        return False

    """
    Have all servo outputs reached their targets? This is useful only if Speed and/or
    Acceleration have been set on one or more of the channels. Returns True or False.
    Not available with Micro Maestro.
    """
    def get_moving_state(self):
        command = chr(0x13)
        self.controller.send_command(command)
        if self.controller.usb.read() == chr(0):
            return False
        else:
            return True


if __name__ == '__main__':
    exit()

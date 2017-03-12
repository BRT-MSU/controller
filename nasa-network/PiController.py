import connection
import ADBLib
import motorLib
import enum
import re

class prefix(enum.Enum):
    tango = '-t',
    client = '-c',
    debug = '-d',
    motor = '-m',
    status = '-s'

motorConnection = motorLib.connection()
tangoConnection = connection.main(serverIPAddress='0.0.0.0', serverPortNumber=6417,
                                  clientIPAddress='192.168.1.4', clientPortNumber=3217)
clientConnection = connection.main(serverIPAddress='0.0.0.0', serverPortNumber=6416,
                                   clientIPAddress='192.168.1.10', clientPortNumber=3216)

def forwardMessage(message):
    if re.match(prefix.tango, message):
        tangoConnection.send(message)
    elif re.match(prefix.client, message):
        clientConnection.send(message)
    elif re.match(prefix.debug, message):
        clientConnection.send(message)
    elif re.match(prefix.motor, message):
        motorConnection.parseInstruction(message)




def main():
    ADBLib.startADB()
    while True:
        clientMessage = clientConnection.getMessage()
        if clientMessage is not None:
            forwardMessage(clientMessage)

        tangoMessage = tangoConnection.getMessage()
        if tangoMessage is not None:
            forwardMessage(tangoMessage)




if __name__ == '__main__':
    main()

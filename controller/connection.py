import argparse
import socket
import threading
import Queue
import enum

SERVER_IP_ADDRESS = '0.0.0.0'
SERVER_PORT_NUMBER = 8888
CLIENT_IP_ADDRESS = 'localhost'
CLIENT_PORT_NUMBER = 9999
DEFAULT_BUFFER_SIZE = 1024

class ClientStatus(enum.Enum):
    HANDSHAKE_INITIALIZED = 'Handshake initialized.'
    HANDSHAKE_SUCCESSFUL = 'Handshake successful.'

class ServerStatus(enum.Enum):
    SERVER_INITIALIZED = 'Server initialized.'
    SERVER_LISTENING = 'Server listening.'
    SERVER_SHUTDOWN = 'Server shutdown.'

class Connection():
    def __init__(self, serverIPAddress, serverPortNumber, clientIPAddress, \
                 clientPortNumber, bufferSize):
        self.serverIPAddress = serverIPAddress
        self.serverPortNumber = serverPortNumber
        self.clientIPAddress = clientIPAddress
        self.clientPortNumber = clientPortNumber
        self.bufferSize = bufferSize

        self.serverQueue = Queue.Queue()

        self.serverStatus = None
        self.serverThread = threading.Thread(name = 'serverThread', target = self.openServerSocket)
        self.serverThread.daemon = True
        self.serverThread.start()

        self.clientStatus = None
        self.handshakeThread = threading.Thread(name = 'handshakeThread', target = self.initiateHandShake)
        self.handshakeThread.daemon = True
        self.handshakeThread.start()

    def initiateHandShake(self):
        self.clientStatus = ClientStatus.HANDSHAKE_INITIALIZED
        print self.clientStatus
        while True:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                clientSocket.connect((self.clientIPAddress, self.clientPortNumber))
                clientSocket.send('SYN\n')

                if clientSocket.recv(self.bufferSize) == 'ACK\n':
                    clientSocket.send('SYN-ACK\n')
                    clientSocket.shutdown(socket.SHUT_WR)
                    clientSocket.close()
                    self.clientStatus = ClientStatus.HANDSHAKE_SUCCESSFUL
                    print self.clientStatus
                else:
                    pass
                break
            except socket.error:
                continue

    def send(self, message):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            clientSocket.connect((self.clientIPAddress, self.clientPortNumber))
            print 'Client sent:', message
            clientSocket.send(message + '\n')
            clientSocket.shutdown(socket.SHUT_WR)
            clientSocket.close()
        except socket.error:
            pass

    def getMessage(self):
        if not self.serverQueue.empty():
            return self.serverQueue.get()
        else:
            return None

    def openServerSocket(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.serverSocket.bind((self.serverIPAddress, self.serverPortNumber))
        self.serverSocket.listen(1)
        self.serverStatus = ServerStatus.SERVER_LISTENING
        print self.serverStatus
        while True:
            try:
                connection, address = self.serverSocket.accept()
                message = connection.recv(self.bufferSize)
                if message == 'SYN\n':
                    connection.send('ACK\n')
                else:
                    print 'Server received:', message.rstrip()
                    self.serverQueue.put(message)
            except socket.error:
                break

    def closeServerSocket(self):
        try:
            self.serverSocket.shutdown(socket.SHUT_RD)
            self.serverSocket.close()
            self.serverStatus = ServerStatus.SERVER_SHUTDOWN
            print self.serverStatus
        except socket.error:
            pass

        self.serverThread.stop = True
        self.handshakeThread.stop = True

def main(serverIPAddress = SERVER_IP_ADDRESS, serverPortNumber = SERVER_PORT_NUMBER, \
            clientIPAddress = CLIENT_IP_ADDRESS, clientPortNumber = CLIENT_PORT_NUMBER, \
            bufferSize = DEFAULT_BUFFER_SIZE):
    return Connection(serverIPAddress, serverPortNumber, clientIPAddress, clientPortNumber, bufferSize)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-sip', '--serverIPAddress', help='server IP address argument', \
                        required=False, default=SERVER_IP_ADDRESS)
    parser.add_argument('-spn', '--serverPortNumber', help='server port number argument', \
                        required=False, default=str(SERVER_PORT_NUMBER))
    parser.add_argument('-cip', '--clientIPAddress', help = 'client IP address argument', \
                        required = False, default = CLIENT_IP_ADDRESS)
    parser.add_argument('-cpn', '--clientPortNumber', help = 'client port number argument', \
                        required = False, default = str(CLIENT_PORT_NUMBER))
    parser.add_argument('-bs', '--bufferSize', help='buffer size argument', \
                        required=False, default=str(DEFAULT_BUFFER_SIZE))
    args = parser.parse_args()

    serverIPAddress = args.serverIPAddress
    serverPortNumber = int(args.serverPortNumber)
    clientIPAddress = args.clientIPAddress
    clientPortNumber = int(args.clientPortNumber)
    bufferSize = int(args.bufferSize)

    print 'serverIpAddress:', serverIPAddress
    print 'serverPortNumber:', serverPortNumber
    print 'clientIpAddress:', clientIPAddress
    print 'clientPortNumber:', clientPortNumber
    print 'bufferSize:', bufferSize

    main(serverIPAddress, serverPortNumber, clientIPAddress, clientPortNumber, bufferSize)

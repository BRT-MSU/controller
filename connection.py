import argparse
import threading
import socket
import Queue
import enum

DEFAULT_LOCAL_IP_ADDRESS = '0.0.0.0'
DEFAULT_LOCAL_PORT_NUMBER = 8888

DEFAULT_REMOTE_IP_ADDRESS = 'localhost'
DEFAULT_REMOTE_PORT_NUMBER = 9999

DEFAULT_BUFFER_SIZE = 1024


class LocalStatus(enum.Enum):
    SERVER_INITIALIZED = 'Local socket initialized.'
    SERVER_LISTENING = 'Local socket listening.'
    SERVER_SHUTDOWN = 'Local socket shutdown.'


class RemoteStatus(enum.Enum):
    HANDSHAKE_INITIALIZED = 'Handshake initialized.'
    HANDSHAKE_SUCCESSFUL = 'Handshake successful.'


class Connection:
    def __init__(self, local_ip_address, local_port_number, remote_ip_address,
                 remote_port_number, buffer_size):
        self.local_socket = None
        
        self.local_ip_address = local_ip_address
        self.local_port_number = local_port_number
        
        self.remote_ip_address = remote_ip_address
        self.remote_port_number = remote_port_number
        
        self.buffer_size = buffer_size

        self.local_queue = Queue.Queue()

        self.local_status = None
        self.local_thread = threading.Thread(name='localThread',
                                             target=self.open_local_socket)
        self.local_thread.daemon = True
        self.local_thread.start()

        self.remote_status = None
        self.handshake_thread = threading.Thread(name='handshakeThread',
                                                 target=self.initiate_handshake)
        self.handshake_thread.daemon = True
        self.handshake_thread.start()

    def initiate_handshake(self):
        self.remote_status = RemoteStatus.HANDSHAKE_INITIALIZED
        print self.remote_status
        while True:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                remote_socket.connect((self.remote_ip_address, self.remote_port_number))
                remote_socket.send('SYN\n')

                if remote_socket.recv(self.buffer_size) == 'ACK\n':
                    remote_socket.send('SYN-ACK\n')
                    remote_socket.shutdown(socket.SHUT_WR)
                    remote_socket.close()
                    self.remote_status = RemoteStatus.HANDSHAKE_SUCCESSFUL
                    print self.remote_status
                else:
                    pass
                break
            except socket.error:
                continue

    def send(self, message):
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            remote_socket.connect((self.remote_ip_address, self.remote_port_number))
            print 'Remote socket sent:', message
            remote_socket.send(message + '\n')
            remote_socket.shutdown(socket.SHUT_WR)
            remote_socket.close()
        except socket.error:
            pass

    def get_message(self):
        if not self.local_queue.empty():
            return self.local_queue.get()
        else:
            return None

    def open_local_socket(self):
        self.local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.local_socket.bind((self.local_ip_address, self.local_port_number))
        self.local_socket.listen(1)
        self.local_status = LocalStatus.SERVER_LISTENING
        print self.local_status
        while True:
            try:
                connection, address = self.local_socket.accept()
                message = connection.recv(self.buffer_size)
                if message == 'SYN\n':
                    connection.send('ACK\n')
                else:
                    print 'Local socket received:', message.rstrip()
                    self.local_queue.put(message)
            except socket.error:
                break

    def close_server_socket(self):
        try:
            self.local_socket.shutdown(socket.SHUT_RD)
            self.local_socket.close()
            self.local_status = LocalStatus.SERVER_SHUTDOWN
            print self.local_status
        except socket.error:
            pass

        self.local_thread.stop = True
        self.handshake_thread.stop = True


def main(local_ip_address, local_port_number,
         remote_ip_address, remote_port_number,
         buffer_size):
    return Connection(local_ip_address, local_port_number,
                      remote_ip_address, remote_port_number,
                      buffer_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-lip', '--localIPAddress', help='local IP address',
                        required=False, default=DEFAULT_LOCAL_IP_ADDRESS)
    parser.add_argument('-lpn', '--localPortNumber', help='local port number',
                        required=False, type=int, default=str(DEFAULT_LOCAL_PORT_NUMBER))
    parser.add_argument('-rip', '--remoteIPAddress', help='remote IP address',
                        required=False, default=DEFAULT_REMOTE_IP_ADDRESS)
    parser.add_argument('-rpn', '--remotePortNumber', help='remote port number',
                        required=False, type=int, default=str(DEFAULT_REMOTE_PORT_NUMBER))
    parser.add_argument('-bs', '--buffer_size', help='buffer size',
                        required=False, type=int, default=str(DEFAULT_BUFFER_SIZE))
    args = parser.parse_args()

    print 'localIpAddress:', args.localIPAddress
    print 'localPortNumber:', args.localPortNumber
    print 'localIpAddress:', args.remoteIPAddress
    print 'localPortNumber:', args.remotePortNumber
    print 'buffer_size:', args.buffer_size

    main(args.localIPAddress, args.localPortNumber,
         args.remoteIPAddress, args.remotePortNumber,
         args.buffer_size)

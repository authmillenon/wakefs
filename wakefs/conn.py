import os
import struct
import socket

def connection_factory():
    connection_type = {
            'local': LocalConnection,
        }
    args = {'path': './test_path'}
    the_class = connection_type['local']
    return the_class(args)

class Connection(object):
    def __new__(type, *args):
        if not '_the_connection' in type.__dict__:
            type._the_connection = object.__new__(type)
        return type._the_connection

    def __init__(self):
        if not '_connected' in dir(self):
            self._connected = True

    def open(self, filename, mode="r", buffering=None):
        raise NotImplemented

class LocalConnection(Connection):
    def __init__(self, path):
        super(LocalConnection, self).__init__()
        self.path = path

    def open(self, filename, mode="r", buffering=None):
        if buffering:
            return open(os.path.join(self.path, filename, mode, buffering))
        else:
            return open(os.path.join(self.path, filename, mode))

    def update(self, model_object):
        # TODO
        print 'Update:', repr(model_object)

class NetConnection(Connection):
    def __init__(self, host, mac, port, path):
        super(NetConnection, self).__init__()
        if len(mac) == 12 + 5:
            sep = mac[2]
            mac = mac.replace(sep, '')
        if len(mac) == 12:
            self.mac = mac
        else:
            raise ValueError('Incorrect MAC address format')
        self.host = host
        self.mac = mac
        self.port = port
        self.path = path

    def wake_host(self):
        # Source: http://code.activestate.com/recipes/358449-wake-on-lan/
        data = ''.join(['FFFFFFFFFFFF', macaddress * 20]) # pad sync stream
        send_data = ''
        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data = ''.join([send_data,
                                 struct.pack('B', int(data[i: i + 2], 16))])

        # Broadcast it to the LAN.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('<broadcast>', 7))

    def connect(self):
        raise NotImplemented

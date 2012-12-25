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

class LocalConnection(Connection):
    def __init__(self, path):
        super(LocalConnection, self).__init__()
        self.path = path

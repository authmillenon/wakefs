from sqlobject import *
from sqlobject.inheritance import *
from sqlobject.views import *
from wakefs.config import Config

import os

_db_connection = None

def initialise(fs_connection):
    global _db_connection
    if _db_connection == None:
        c = Config()
        _db_connection = connectionForURI(c.database_uri)
        sqlhub.processConnection = _db_connection
        INode.createTable(ifNotExists=True)
        Directory.createTable(ifNotExists=True)
        File.createTable(ifNotExists=True)
    root = Directory.selectBy(name="/")
    if root.count() == 0:
        return Directory(id=1,name="/",directory=None,crc=0)
    else:
        return root[0]

class INode(InheritableSQLObject):
    crc = IntCol(notNone=True)
    directory = ForeignKey('Directory',default=1)
    name = StringCol(notNone=True,unique=True)
    location = StringCol(default=None)
    
    crcIndex = DatabaseIndex('crc')
    nameIndex = DatabaseIndex('name')
    
    def _set_name(self, value):
        if value != '/' and self.directory == None:
            raise IntegrityError('directory may not be %s if INode is not %s.' % (repr(self.directory), repr(value)))
        if self.directory != None:
            if os.path.dirname(value).strip('/') != self.directory.name.strip('/'):
                value = os.path.join(self.directory.name,value)
        else:
            value = os.path.join('/',value)
        self._SO_set_name(value)
    
class Directory(INode):
    content = MultipleJoin('INode')

class File(INode):
    pass

# Copyright (c) 2012 Martin Lenders
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from sqlobject import *
from sqlobject.inheritance import *
from sqlobject.views import *
from wakefs.config import Config
import wakefs.utils

import os

_db_connection = None

def close():
    global _db_connection
    _db_connection.close()
    _db_connection = None

def query(query_str):
    global _db_connection
    return _db_connection.queryAll(query_str)

def initialise(database_uri=None):
    global _db_connection
    if _db_connection == None:
        if database_uri == None:
            with Config() as config:
                database_uri = config.database_uri
        _db_connection = connectionForURI(database_uri)
        sqlhub.processConnection = _db_connection
        File.createTable(ifNotExists=True)
        Directory.createTable(ifNotExists=True)
        File.createTable(ifNotExists=True)
        Link.createTable(ifNotExists=True)
        SymLink.createTable(ifNotExists=True)
    root = Directory.selectBy(name="/")
    if root.count() == 0:
        stats = wakefs.utils.get_stats("/")
        return Directory(id=1, name="/", directory=None, **stats)
    else:
        return root[0]

class IntegrityError(Exception):
    pass

class File(InheritableSQLObject):
    crc = IntCol(default=None)
    directory = ForeignKey('Directory',cascade=True,default=1)
    name = StringCol(notNone=True,unique=True)
    location = StringCol(default=None)
    st_mode = IntCol(default=None)
    st_ino = IntCol(default=None)
    st_dev = IntCol(default=None)
    st_nlink = IntCol(default=None)
    st_uid = IntCol(default=None)
    st_gid = IntCol(default=None)
    st_rdev = IntCol(default=None)
    st_size = IntCol(default=None)
    st_blksize = IntCol(default=None)
    st_blocks = IntCol(default=None)
    st_atime = IntCol(default=None)
    st_mtime = IntCol(default=None)
    st_ctime = IntCol(default=None)
    
    crcIndex = DatabaseIndex('crc')
    nameIndex = DatabaseIndex('name')
    
    def _set_name(self, value):
        if value != '/' and self.directory == None:
            raise IntegrityError(
                    'directory may not be {} if {} is not {}.'.\
                            format(
                                    repr(self.directory),
                                    type(self).__name__,
                                    repr(value)
                                )
                )
        if self.directory != None:
            if os.path.dirname(value).strip('/') != \
                    self.directory.name.strip('/') or value[0] != '/':
                value = os.path.join(self.directory.name,value)
        else:
            value = os.path.join('/',value)
        self._SO_set_name(value)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return unicode(self)

class Directory(File):
    content = MultipleJoin('File')

class Link(File):
    target = StringCol()

class SymLink(Link):
    pass

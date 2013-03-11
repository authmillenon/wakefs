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

def initialise():
    global _db_connection
    if _db_connection == None:
        config = Config()
        _db_connection = connectionForURI(config.database_uri)
        sqlhub.processConnection = _db_connection
        INode.createTable(ifNotExists=True)
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

class INode(InheritableSQLObject):
    crc = IntCol(notNone=True)
    directory = ForeignKey('Directory',cascade=True,default=1)
    name = StringCol(notNone=True,unique=True)
    location = StringCol(default=None)
    st_mode = IntCol(notNone=True)
    st_ino = IntCol(notNone=True)
    st_dev = IntCol(notNone=True)
    st_nlink = IntCol(notNone=True)
    st_uid = IntCol(notNone=True)
    st_gid = IntCol(notNone=True)
    st_rdev = IntCol(notNone=True)
    st_size = IntCol(notNone=True)
    st_blksize = IntCol(notNone=True)
    st_blocks = IntCol(notNone=True)
    st_atime = IntCol(notNone=True)
    st_mtime = IntCol(notNone=True)
    st_ctime = IntCol(notNone=True)
    
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

class Directory(INode):
    content = MultipleJoin('INode')

class File(INode):
    pass

class Link(INode):
    target = ForeignKey('INode',notNone=True)

class SymLink(Link):
    pass

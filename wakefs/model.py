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

import os.path
from sqlobject import SQLObjectNotFound
from sqlobject.dberrors import DuplicateEntryError

import wakefs.db
import wakefs.utils
import wakefs.conn

def get_object(filename, location=None):
    return File(filename, location)

class IsDirectoryError(Exception):
    pass

class IsFileError(Exception):
    pass

class _DBConnectedObject(object):
    def __init__(self):
        self._dbobject = None
        raise NotImplemented

    def _get_db_col(self, colname):
        if self._dbobject:
            return getattr(self._dbobject, colname)
        else:
            raise AttributeError("Object was deleted")

    def _set_db_col(self, colname, value):
        if self._dbobject:
            setattr(self._dbobject, colname, value)
        else:
            raise AttributeError("Object was deleted")

class Stats(_DBConnectedObject):
    _valid_attributes = {
            'st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid',
            'st_gid', 'st_rdev', 'st_size', 'st_blksize', 'st_blocks',
            'st_atime', 'st_mtime', 'st_ctime'
        }

    def __init__(self, dbobject):
        self._dbobject = dbobject

    def __getattribute__(self, name):
        if name in Stats._valid_attributes:
            return self._get_db_col(name)
        else:
            return object.__getattribute__(self,name)

    def __setattr__(self, name, value):
        if name in Stats._valid_attributes:
            self._set_db_col(name, value)
        else:
            return object.__setattr__(self,name,value)

    def __repr__(self):
        repr = "Stats("
        for a in Stats._valid_attributes:
            repr += a + '=' + str(getattr(self,a)) + ','
        return repr[:-1] + ")"

class File(_DBConnectedObject):
    def __new__(cls, name, *args, **kwargs):
        wakefs.db.initialise()
        try:
            db_obj = wakefs.db.File.selectBy(name=name).getOne()
            if type(db_obj).__name__ != cls.__name__:
                return globals()[type(db_obj).__name__](name, db_obj, *args, **kwargs)
        except SQLObjectNotFound:
            pass
        return super(File, cls).__new__(cls, name, *args, **kwargs)

    def __init__(self, name, db_obj=None, location=None, **kwargs):
        DBObjectClass = getattr(wakefs.db,type(self).__name__)
        self._connection = wakefs.conn.connection_factory()

        if db_obj != None:
            self._dbobject = db_obj
        elif name == "/":
            self._dbobject = wakefs.db.Directory.selectBy(name=name).getOne()
        else:
            dirname = os.path.dirname(name) or "/"
            if dirname != "/" and wakefs.db.File.selectBy(name=dirname).count() > 0:
                raise IsFileError("'%s' is a file." % dirname)
            directory = Directory(
                    name=dirname,
                    location=location
                )
            stats = wakefs.utils.get_stats(name, location)
            try:
                kwargs.update(stats)
                self._dbobject = DBObjectClass(
                        directory=directory._dbobject,
                        location=location,
                        name=name,
                        **kwargs
                   )
            except DuplicateEntryError:
                self._dbobject = DBObjectClass.selectBy(name=name).getOne()

    def remove(self):
        wakefs.db.File.deleteBy(name=self.name)



    def __getattribute__(self, name):
        if name == 'stat':
            return Stats(self._dbobject)
        elif name in ['crc','location','name']:
            return self._get_db_col(name)
        else:
            return _DBConnectedObject.__getattribute__(self,name)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return u"<"+unicode(type(self).__name__)+u": "+unicode(self)+u">"

class Link(File):
    def __init__(self, name, db_obj=None, location=None, target=None,
            **kwargs):
        super(Link, self).__init__(
                name,
                db_obj,
                location,
                target=target,
                **kwargs
            )

    def __getattribute__(self, name):
        if name == 'target':
            return self._get_db_col(name)
        else:
            return File.__getattribute__(self,name)

class SymLink(Link):
    pass

class Directory(File):
    class _content(object):
        def __init__(self, directory):
            self.directory = directory

        def __iter__(self):
            for c in self.directory._get_db_col('content'):
                yield globals()[type(c).__name__](c.name,c.location)

        def __len__(self):
            return len(self.directory._get_db_col('content'))

    def content(self):
        return Directory._content(self)

    def get_file_object(self, mode="r", buffering=None):
        raise IsDirectoryError("A directory can not be opened.")

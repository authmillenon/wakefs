import os.path
from sqlobject import SQLObjectNotFound

import wakefs.db
import wakefs.utils
import wakefs.conn

class File(object):
    def __init__(self, name, location=None):
        wakefs.db.initialise()
        DBObjectClass = getattr(wakefs.db,type(self).__name__)
        try:
            self._dbobject = DBObjectClass.selectBy(name=name).getOne()
        except SQLObjectNotFound:
            dirname = os.path.dirname(name) or "/"
            if dirname != "/" and wakefs.db.File.selectBy(name=dirname).count() > 0:
                raise ValueError("'%s' is a file." % dirname)
            directory = Directory(
                    name=dirname,
                    location=location
                )
            stats = wakefs.utils.get_stats(name, location)
            self._dbobject = DBObjectClass(
                    directory = directory._dbobject,
                    location = location,
                    name = name,
                    **stats
                )

    def __get_db_col(self, colname):
        if self._dbobject:
            return getattr(self._dbobject, colname)
        else:
            raise AttributeError("Object was deleted")

    def __set_db_col(self, colname, value):
        if self._dbobject:
            setattr(self._dbobject, colname, value)
        else:
            raise AttributeError("Object was deleted")

    @property
    def crc(self):
        return self.__get_db_col('crc')

    @property
    def location(self):
        return self.__get_db_col('location')

    @property
    def name(self):
        return self.__get_db_col('name')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return unicode(self)
    
class Link(File):
    def __init__(self, name, target, location=None):
        wakefs.db.initialise()
        DBObjectClass = getattr(wakefs.db,type(self).__name__)
        self._connection = wakefs.conn.connection_factory()
        try:
            self._dbobject = DBObjectClass.selectBy(name=name).getOne()
        except SQLObjectNotFound:
            dirname = os.path.dirname(name) or "/"
            if dirname != "/" and wakefs.db.File.selectBy(name=dirname).count() > 0:
                raise ValueError("'%s' is a file." % dirname)
            directory = Directory(
                    name=dirname,
                    location=location
                )
            stats = wakefs.utils.get_stats(name, location)
            self._dbobject = wakefs.db.DBObjectClass(
                    directory = directory._dbobject,
                    location = location,
                    target = target,
                    name = name,
                    **stats
                )

    @property
    def target(self):
        return self.target

class SymLink(Link):
    pass

class Directory(File):
    @property
    def content(self):
        for c in self.__get_db_col('content'):
            yield globals()[type(c).__name__](c.name,c.location)

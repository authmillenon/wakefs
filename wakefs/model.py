import os.path
from sqlobject import SQLObjectNotFound

import wakefs.db
import wakefs.utils
import wakefs.conn

class Stats(object):
    valid_attributes = {
            'st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid',
            'st_gid', 'st_rdev', 'st_size', 'st_blksize', 'st_blocks',
            'st_atime', 'st_mtime', 'st_ctime'
        }

    def __init__(self, **stat):
        if set(stat.keys()) == Stats.valid_attributes:
            self.stat = stat
        else:
            raise ValueError("Parameters %s wrong" %
                    str(tuple(Stats.valid_attributes ^ set(stat.keys()))))

    def __getattribute__(self, name):
        if name in Stats.valid_attributes:
            return self.stat[name]
        else:
            return object.__getattribute__(self,name)

    def __repr__(self):
        repr = "Stats("
        for a in Stats.valid_attributes:
            repr += a + '=' + str(self.stat[a]) + ','
        return repr[:-1] + ")"

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

    @property
    def stat(self):
        return Stats(
                self.__get_db_col('st_mode'),
                self.__get_db_col('st_ino'),
                self.__get_db_col('st_dev'),
                self.__get_db_col('st_nlink'),
                self.__get_db_col('st_uid'),
                self.__get_db_col('st_gid'),
                self.__get_db_col('st_rdev'),
                self.__get_db_col('st_size'),
                self.__get_db_col('st_blksize'),
                self.__get_db_col('st_blocks'),
                self.__get_db_col('st_atime'),
                self.__get_db_col('st_mtime'),
                self.__get_db_col('st_ctime'),
            )

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

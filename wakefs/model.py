import os.path
from sqlobject import SQLObjectNotFound

import wakefs.db
import wakefs.utils

class File(object):
    def __init__(self, connection, name, location=None):
        wakefs.db.initialise(connection)
        DBObjectClass = getattr(wakefs.db,type(self).__name__)
        self._connection = connection
        try:
            self._dbobject = DBObjectClass.selectBy(name=name).getOne()
        except SQLObjectNotFound:
            dirname = os.path.dirname(name) or "/"
            if dirname != "/" and wakefs.db.File.selectBy(name=dirname).count() > 0:
                raise ValueError("'%s' is a file." % dirname)
            directory = Directory(
                    connection=connection, 
                    name=dirname,
                    location=location
                )
            stats = wakefs.utils.get_stats(connection, name, location)
            self._dbobject = DBObjectClass(
                    directory = directory._dbobject,
                    location = location,
                    name = name,
                    **stats
                )

    @property
    def crc(self):
        return self._dbobject.crc

    @property
    def location(self):
        return self._dbobject.location

    @property
    def name(self):
        return self._dbobject.name

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(unicode(self))

    def __repr__(self):
        return unicode(self)
    
class Directory(File):
    @property
    def content(self):
        return self._dbobject.content

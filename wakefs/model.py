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

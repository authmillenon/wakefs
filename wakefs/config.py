import ConfigParser, os.path

class Config(object):
    _configfile = os.path.expanduser('~/.wakefs/config')
    def __new__(type, *args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

    def __init__(self,configfile=None):
        if not '_ready' in dir(self):
            self._ready = True
        if configfile != None:
            Config._configfile = str(configfile)
        configdir = os.path.dirname(Config._configfile)
        self._parser = ConfigParser.SafeConfigParser({
                'database_uri': 'sqlite://'+os.path.expanduser('~/.wakefs/db.sqlite'),
            })
        if not os.path.exists(configdir) and len(configdir) > 0:
            os.mkdir(configdir)
        else:
            if os.path.exists(Config._configfile):
                self._parser.read(configfile)
    
    def __getattribute__(self, name):
        if name == "_parser":
            return object.__getattribute__(self, name)
        try:
            value = self._parser.get("DEFAULT", name)
            return value
        except ConfigParser.NoOptionError:
            return object.__getattribute__(self, name)


    def __setattr__(self, name, value):
        if name == 'database_uri':
            self._parser.set("DEFAULT", "database_uri", value)
        else:
            object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name == 'database_uri':
            self._parser.remove_option("DEFAULT", "database_uri")
        else:
            object.__delattr__(self, name)
    
    def close(self):
        configfile = open(Config._configfile,'wb')
        self._parser.write(configfile)
        configfile.close()
        Config._config = None

    def __del__(self):
        self.close()

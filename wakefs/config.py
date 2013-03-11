# Copyright (c) 2012 Martin Lenders

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.close()

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
        with open(Config._configfile,'w') as configfile:
            self._parser.write(configfile)
        Config._config = None

    def __del__(self):
        self.close()

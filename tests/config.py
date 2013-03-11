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

import wakefs.config
import os
import unittest
import random
import string

def random_str(N):
    ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(N))

class TestConfigFileCreate(unittest.TestCase):
    def test_file_create(self):
        testfile = "test.cfg"
        with wakefs.config.Config(testfile) as config:
            pass
        self.assertTrue(os.path.exists(testfile))
        os.remove(testfile)

class TestConfigAttributes(unittest.TestCase):
    def setUp(self):
        self.testfile = "test.cfg"
        self.config = wakefs.config.Config(self.testfile)
    
    def test_get_attribute(self):
        self.config.database_uri

    def test_get_wrong_attribute(self):
        with self.assertRaises(AttributeError):
            self.config.detabase_uri

    def test_set_attribute(self):
        teststr = random_str(random.randint(5,20))
        self.config.test = teststr
        self.assertTrue(self.config.test == teststr)

    def test_del_attribute(self):
        teststr = random_str(random.randint(5,20))
        self.config.test = teststr
        self.assertTrue(self.config.test == teststr)
        del self.config.test
        with self.assertRaises(AttributeError):
            self.config.test

    def tearDown(self):
        self.config.close()
        os.remove(self.testfile)

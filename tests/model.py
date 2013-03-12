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

import wakefs.model
from wakefs.db import initialise
from tests.utils import rand_len_str
import unittest
import random
import os

class TestModelObjectGet(unittest.TestCase):
    def setUp(self):
        self.testfile = "/tmp/test.db"
        initialise("sqlite://"+self.testfile)

    def test_get_root(self):
        root = wakefs.model.Directory("/")
        self.assertEquals(root.name,"/")
        self.assertEquals(len(root.content()), 0)
        self.assertFalse(wakefs.model.File.exists(rand_len_str()))
        with self.assertRaises(wakefs.model.FileDoesNotExist):
            wakefs.model.File.get(rand_len_str())

    def tearDown(self):
        wakefs.db.close()
        os.remove(self.testfile)

class TestModelObjectInit(unittest.TestCase):
    def setUp(self):
        self.testfile = "/tmp/test.db"
        initialise("sqlite://"+self.testfile)
        self.root = wakefs.model.Directory("/")

    def test_create_file(self):
        testname = rand_len_str()
        file = wakefs.model.File(name=testname)
        self.assertEquals(file.name.find(testname), 1)
        self.assertTrue(wakefs.model.File.exists(file.name))

    def test_remove_file(self):
        testname = rand_len_str()
        file = wakefs.model.File(name=testname)
        file.remove()
        self.assertFalse(wakefs.model.File.exists(file.name))

    def tearDown(self):
        wakefs.db.close()
        os.remove(self.testfile)

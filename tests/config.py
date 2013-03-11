import wakefs.config
from tests.utils import rand_len_str
import os
import random
import unittest

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
        teststr = rand_len_str()
        self.config.test = teststr
        self.assertTrue(self.config.test == teststr)

    def test_del_attribute(self):
        teststr = rand_len_str()
        self.config.test = teststr
        self.assertTrue(self.config.test == teststr)
        del self.config.test
        with self.assertRaises(AttributeError):
            self.config.test

    def tearDown(self):
        self.config.close()
        os.remove(self.testfile)

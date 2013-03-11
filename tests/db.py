import wakefs.db
from tests.utils import rand_len_str
from sqlobject.dberrors import DuplicateEntryError
import unittest
import random
import os

class TestDBInit(unittest.TestCase):
    def test_db_initialize(self):
        testfile = "/tmp/test.db"
        root = wakefs.db.initialise("sqlite://"+testfile)
        self.assertTrue(os.path.exists(testfile))
        wakefs.db.close()
        os.remove(testfile)

class TestDBQuery(unittest.TestCase):
    def setUp(self):
        self.testfile = "/tmp/test.db"
        self.root = wakefs.db.initialise("sqlite://"+self.testfile)

    def test_select_root(self):
        file = wakefs.db.query(
                "SELECT * FROM file WHERE name=\"/\""
            )[0]
        self.assertEquals(
                file[3],
                '/'
            )

    def tearDown(self):
        wakefs.db.close()
        os.remove(self.testfile)

class TestDBObjectInit(unittest.TestCase):
    def setUp(self):
        self.testfile = "/tmp/test.db"
        self.root = wakefs.db.initialise("sqlite://"+self.testfile)
    
    def test_setup_file_no_keyword(self):
        with self.assertRaises(TypeError):
            wakefs.db.File() 
    
    def test_setup_file_none_name(self):
        with self.assertRaises(AttributeError):
            wakefs.db.File(name=None)

    def test_setup_file_no_directory(self):
        name=rand_len_str()
        file=wakefs.db.File(name=name)
        self.assertEquals(file.name.find(name),1)
        self.assertEquals(
                len(list(wakefs.db.File.selectBy(name=file.name))),
                1
            )

    def test_setup_file_double_same_file(self):
        name=rand_len_str()
        file1=wakefs.db.File(name=name)
        with self.assertRaises(DuplicateEntryError):
            file2=wakefs.db.File(name=name)

    def test_setup_file_without_directory_init(self):
        dirname=rand_len_str()
        filename=rand_len_str()
        file=wakefs.db.File(name=os.path.join(dirname,filename))
        self.assertEquals(
                len(list(wakefs.db.File.selectBy(name=file.name))),
                1
            )
        self.assertEquals(
                file.directory.name,
                self.root.name
            )

    def test_setup_file_containing_dirname(self):
        dirname=rand_len_str()
        filename=rand_len_str()
        directory=wakefs.db.Directory(name=dirname)
        file=wakefs.db.File(name=os.path.join(dirname,filename))
        self.assertEquals(
                len(list(wakefs.db.Directory.selectBy(name=directory.name))),
                1
            )
        self.assertEquals(
                len(list(wakefs.db.File.selectBy(name=file.name))),
                1
            )
        self.assertEquals(
                file.directory.name,
                self.root.name
            )

    def test_setup_directory_with_file(self):
        dirname=rand_len_str()
        filename=rand_len_str()
        directory=wakefs.db.Directory(name=dirname)
        file=wakefs.db.File(name=filename,directory=directory)
        self.assertEquals(
                len(list(wakefs.db.Directory.selectBy(name=directory.name))),
                1
            )
        self.assertEquals(
                len(list(wakefs.db.File.selectBy(name=file.name))),
                1
            )
        self.assertEquals(
                file.directory.name,
                directory.name
            )

    def tearDown(self):
        wakefs.db.close()
        os.remove(self.testfile)

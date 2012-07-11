'''
Created on 26.06.2012

@author: pasha
'''
import unittest
from core.engines import stylish
from core.engines.stylish import stylishengine 

class StylishTest(unittest.TestCase):


    def setUp(self):
        self.obj = stylishengine.StylishEngine()


    def tearDown(self):
        pass


    def test_firefoxProfiles(self):
        self.obj.loadFirefoxProfiles()
        self.assertTrue(self.obj.firefoxProfiles, 'firefox profiles not detect')
        self.assertTrue(self.obj.styles(None), 'styles not detect')
        print (self.obj.styles(None))
        



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


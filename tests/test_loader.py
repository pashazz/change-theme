'''
Created on 26.06.2012

@author: pasha
'''
import unittest, os
from core import loader, config
import time


class TestLoader(unittest.TestCase):


    def setUp(self):
        self.callbacks = 0


    def tearDown(self):
        pass
    
    def callback_func(self, engine, status, error):
        '''tests callbacks'''
        print ("Notification From Engine! {}: status  '{}', error '{}'".format(
                            engine, status, error))
        self.callbacks += 1

    def test_loader(self):
        '''test loader's work almostly'''
        l = loader.AppLoader(self.callback_func)
        self.assertTrue(l.loadedEngines)
        l.startDaemon()
        time.sleep(10)
        self.assertIsNotNone(l.running)
        l.stopDaemon()
        l.stopAll()
        
    #def test_callbacks(self):
    #    self.test_loader()
    #    self.assertGreater(self.callbacks, 0, 'callbacks not work')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

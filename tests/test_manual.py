'''
Created on 08.07.2012

@author: pasha
'''
import unittest
from core.timesets.manual import ManualTimeset
import time
from datetime import datetime, timedelta
import os

class TestManual(unittest.TestCase):
    def callback(self, profileid):
        print ('Callback from ManualTimeset, text= {}'.format(profileid))
        
        #jajaja ich kann!!!!

    def setUp(self):
        self.mts = ManualTimeset(self.callback)
        now = (datetime.now() + timedelta(minutes=1)).strftime('%H:%M')
        print ('now is {}'.format(now))
        self.mts.setSettings({'day':('10:00', now), 'night':(now, '10:00')})
        
    def tearDown(self):
        os.remove(self.mts.conffile)
        
        
    def test_currper(self):
        '''check if we know about current period'''
        print (self.mts.currentPeriod())
        self.assertIn(self.mts.currentPeriod(), ('day', 'night'), 'runs incorrectly?')
        self.assertEqual('day', self.mts.currentPeriod(), 'must be day because of setUp')
        
    def test_startstop(self):
        '''starts server and stops after 10s'''
        print ('status of object: {}; last error: {};'.format(self.mts.status,
                                                    self.mts.lastError()))
        self.assertEqual(self.mts.status, 'ready', 'ERROR! BAD STATUS')
        self.mts.start()
        time.sleep(60)
        self.assertEqual('running', self.mts.status, 'Not running???')
        self.mts.stop()
        print (self.mts.status)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

'''
Created on 25.06.2012

@author: pasha
'''
import unittest, time
import core.timesets.yandex.yatimeset as yatset

class Test_Yatimeset(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_success_creation_of_yatimeset(self):
        '''check if yatimeset returns correct dict'''
        callback = lambda msg: print (msg)
        set = yatset.YandexTimeset(callback)
        if set.status == 'configure':
            set.cityid = 27616
        set.night_delta = 5
        set.day_delta = 5
        if set.status == 'ready':
            set.start()
            time.sleep(10)
            print('stoooopp')
            set.stop()
        else:
            self.assertTrue(False, 'Test error')
       
   
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    

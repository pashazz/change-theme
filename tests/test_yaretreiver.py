#-------------------------------------------------------------------------------
# Copyright (c) 2012 Pavel Borisov
# All rights reserved. ChangeTheme and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# Contributors:
#     pasha - initial API and implementation
#-------------------------------------------------------------------------------
'''
Created on 23.06.2012

@author: pasha
'''
import unittest
import core.timesets.yandex.retreiver as yandex
import datetime

class TestYandex(unittest.TestCase):


    def setUp(self):
        self.obj = yandex.YandexRetreiver()
        

    def tearDown(self):
        pass


    def test_countriesList(self):
        '''Check first and last country in list: Абхазия и Япония'''
        lst = self.obj.countriesList()
        self.assertEqual('Абхазия', lst[0], 'countr. fail?')
        self.assertEqual('Япония', lst[-1], 'countr. fail?')
        
    def test_Posad(self):
        lst = self.obj.countriesList()
        self.assertIn('Россия', lst, 'Where is SUPERBEAR?')
        cit_list = self.obj.citiesList('Россия')
        found = False
        for (myid, city) in cit_list.items():
            if myid == 27616 and city == 'Сергиев Посад': #glory Posad!
                found = True
        
        self.assertTrue(found, 'Wassup wheres posad?')


    def test_today(self):
        sunrise, sunset = self.obj.sunrise(27616, datetime.date.today())
        self.assertIsInstance(sunset, datetime.time, 'null sunset')
        self.assertIsInstance(sunrise, datetime.time, 'null sunrise')
        
    def test_batchdate(self):
        times = self.obj.sunrise(27616)
        self.assertTrue(times, 'batchdate dont work')
        
    def test_getname(self):
        self.assertEqual(self.obj.name(27616), 'Сергиев Посад', 'no posad???')
    
    def test_getid(self):
        self.assertEqual(self.obj.id('Сергиев Посад'), 27616, 'no posad???')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

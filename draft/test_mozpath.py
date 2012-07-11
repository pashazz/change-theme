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
Created on 22.06.2012

@author: pasha
'''
import unittest, os
import mozpath

class Test(unittest.TestCase):


    def setUp(self):
        '''create empty mozilla profile'''
        self.profiles = mozpath.getProfilePath()

    def tearDown(self):
        pass
        
    def test_isList(self):
        self.assertIsInstance(self.profiles, dict, "forgot return?")


    def test_mozPath(self):
        '''Check that mozpath return valid profile'''
        self.assertEqual(self.profiles['firefox'][0], '/home/pasha/.mozilla/firefox/utqps47j.default')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

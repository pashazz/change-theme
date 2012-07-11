'''
Created on 06.07.2012

@author: pasha
'''
import unittest
from core.engines.kde import *

class KdeToolsTest(unittest.TestCase):
    
    def test_emoticon(self):
        self.assertTrue(emoticons.listIconThemes(), 'listIconThemes dont work?')
#        emoticons.applyIconTheme('KMess-Blue')
#        
    def test_plasmapkgs(self):
        self.assertTrue(plasmathemes.listThemes(), 'cant detect desktoptheme')
        #print(plasmathemes.listThemes())
        
    def test_styles(self):
        self.assertTrue(styles.listStyles(), 'cant detect styles')
        print (tuple(styles.listStyles()))

if __name__ == '__main__':
    unittest.main()

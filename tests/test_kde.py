'''
Created on 29.06.2012

@author: pasha
'''
import unittest
from core.engines.kde import KdeEngine, kdecolors, icons, styles, emoticons, \
    plasmathemes

class Test(unittest.TestCase):

    def tearDown(self):
        pass


#    def test_applyRandomColor(self):
#        choices = kdecolors.listColorSchemes()
#        kdecolors.applyColorScheme(random.choice(tuple(choices.values())))
#        
#    def test_icon(self):
#        icons.applyTheme('iceglass')
#        

        
        
    def test_pkg(self):
        '''test if all KDE Engine works correctly'''
        eng = KdeEngine()
        #eng.proposeSetting('test', 'color-scheme', 'Norway')
        #eng.proposeSetting('test', 'plasma-theme', 'Androbit')
        #eng.proposeSetting('test', 'icons', 'Euforie 2')
        #eng.proposeSetting('test', 'style', 'Bespin')
        eng.setUp('test')
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    

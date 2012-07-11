'''
Created on 30.06.2012

@author: pasha
@summary: manipulate Plasma Themes (not color schemes)
@copyright: (c) Pavel Borisov 2011
@license: GPLv3
This module's methods are very similar to kdecolors.py

'''

from PyKDE4.kdecore import KConfig, KDesktopFile
from .kdepath import kdepath, readDesktop
import os, glob

def applyTheme(themeName):
    ''' @summary: apply themefile to plasmarc
        @param themeName: theme name - use os.path.basename of any of listThemes()
        @attention: we don't check if theme is correct
    '''
    if not isinstance(themeName, str):
        raise ValueError ('themeName must be str object')
    assert (themeName in (os.path.basename(p) for p in listThemes()))
    plasma = KConfig('plasmarc', KConfig.NoGlobals)
    themegr = plasma.group('Theme')
    themegr.writeEntry('name', themeName)
    
def listThemes():
    '''
    @summary: list all Plasma themes
    @rtype: tuple
    @return: typle {theme_name:theme_path}
    '''
    dirs = kdepath('data')
    themes = []
    for d in dirs:
        os.chdir(d)
        if not os.path.exists('desktoptheme'):
            continue
        os.chdir('desktoptheme')
        themes.extend((os.path.dirname(os.path.abspath(p))
                     for p in glob.glob('*/metadata.desktop')))
        
    return {os.path.basename(k):k for k in themes}

def metadata (themePath):
    '''
    @summary: return metadata from .desktop using KDesktopFile
    @rtype: tuple
    @return: tuple (name,comment) according to KDE locale settings
    @param themePath: - full path to theme excluding metadata file
    '''
    if not os.path.exists(os.path.join(themePath, 'metadata.desktop')): return None
    
    file = os.path.join(themePath, 'metadata.desktop')
    return readDesktop(file)

    
       
        

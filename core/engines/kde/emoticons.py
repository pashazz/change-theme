'''
Created on 04.07.2012

@author: Pavel Borisov
@summary: Manipulate KDE emoticons

'''
from .kdepath import kdepath
from PyKDE4.kdecore import KConfig
from PyKDE4.kdeui import KGlobalSettings
import os, glob

def listIconThemes():
    '''
    @summary: list all emoticons available'''
    dirs = kdepath('emoticons')
    themes = []
    for d in dirs:
        os.chdir(d)
        dirnames = [os.path.dirname(f) for f in glob.glob('*/emoticons.xml')]
        themes.extend(dirnames)
    
    return themes

def applyIconTheme(themeName):
    '''
    @summary: apply emoticon theme themeName
    @raise AssertionError: if not themeName is vaild 
    '''
    assert themeName in listIconThemes()
    config = KConfig('kdeglobals')
    gr = config.group('Emoticons')
    gr.writeEntry('emoticonsTheme', themeName)
    config.sync()
    KGlobalSettings.emitChange(KGlobalSettings.IconChanged)
    
        

'''
Created on 04.07.2012

@author: Pavel Borisov
@summary:apply KDE icon themes
@note: for manipulating icon themes use PyKDE4.kdeui.KIconTheme
'''
from PyKDE4.kdecore import KConfig
from PyKDE4.kdeui import KIconTheme, KGlobalSettings

def applyTheme(theme):
    '''
    @summary: check if theme is valid and apply it into kdeglobals
    '''
    assert theme in KIconTheme.list()
    config = KConfig('kdeglobals')
    gr = config.group('Icons')
    gr.writeEntry('Theme', theme)
    config.sync()
    KGlobalSettings.emitChange(KGlobalSettings.IconChanged)
    

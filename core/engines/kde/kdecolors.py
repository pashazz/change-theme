'''
Created on 29.06.2012

@author: pasha
@summary: functions for find & apply KDE color schemes
@requires: PyKDE4 KDEUi and KDECore
'''

from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kdecore import KConfig
from .kdepath import kdepath
import os, glob


def applyColorScheme(schemeFile):
    '''Applies the color scheme to KDE globals'''
    scheme = KConfig(schemeFile, KConfig.NoGlobals)
    kdeglobals = KConfig('kdeglobals')
    for groupName in scheme.groupList():
        group = scheme.group(groupName)
        global_group = kdeglobals.group(groupName)
        for (k, v) in group.entryMap().items():
            if groupName == 'General' and k == 'Name': k = 'ColorScheme'
            global_group.writeEntry(k, v)
            
    kdeglobals.sync()
    KGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
        

def listColorSchemes():
    '''
    @author: Pavel Borisov
    @summary: List all KDE color schemes
    @rtype: dict
    @return: {scheme_name:scheme_filename}
    @todo: use KDE things instead of calling kde4-config
    @attention: problem: http://forum.kde.org/viewtopic.php?f=43&t=106601&p=244986#p244986
    '''
    def getColorName(file):
        config = KConfig(os.path.abspath(file))
        general = config.group('General')
        return general.readEntry('Name') if general.hasKey('Name') else None
       
    
    dirs = kdepath('data')
    schemes = {}
    for directory in dirs:
        os.chdir(directory)
        if not os.path.exists('color-schemes'): continue
        os.chdir('color-schemes')
        schm = {getColorName(f):os.path.abspath(f) for f in glob.glob('*.colors')}
        schemes.update(schm)
    
    return schemes

                          
    



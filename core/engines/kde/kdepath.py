'''
Created on 30.06.2012

@author: Pavel Borisov
'''
from subprocess import check_output
from locale import getpreferredencoding
from PyKDE4.kdecore import KDesktopFile

def kdepath(kdetype):
    '''
    @summary: Return KDE path from kde4-config
    @raise: OSError if kde4-config not found
    @param type: one of KDE resource types
    @requires: kde4-config
    @attention: list of KDE4 types: kde4-config --types
    @rtype: list or None
    '''
    callargs = ['kde4-config', '--path', kdetype]
    ret = check_output(callargs)
    dirstr = ret.decode(getpreferredencoding()).rstrip('\n')
    return dirstr.split(':') if dirstr else None
    
    
def readDesktop(file):
    '''
    @summary: return metadata from .desktop using KDesktopFile
    @rtype: tuple
    @return: tuple (name,comment) according to KDE locale settings
    @param themePath: - full path to metadata file
    '''
    
    file = KDesktopFile(file)
    if not file.isDesktopFile(): return None
    return file.readName(), file.readComment()

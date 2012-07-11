'''
Created on 30.06.2012

@author: Pavel Borisov
@summary: Manipulate KDE Styles
'''
from PyKDE4.kdecore import KConfig
from PyKDE4.kdeui import KGlobalSettings
import configparser #for themerc
from .kdepath import kdepath, readDesktop
import os, glob, logging



def applyStyle(styleName):
    '''
    Apply style to KDE globals
    @param styleName:  Qt style name
    '''
    config = KConfig('kdeglobals')
    #assert
    gr = config.group('General')
    gr.writeEntry('widgetStyle', styleName.lower())
    config.sync()
    KGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
    
def listStyles():
    '''
    list of KDE styles
    '''
    def styleName(file):
        conf = configparser.ConfigParser()
        conf.read(file)
        if 'KDE' in conf and 'WidgetStyle' in conf['KDE']:
            return conf['KDE']['WidgetStyle']
        else:
            return None
    dirs = kdepath('data')
    styles = {}
    for d in dirs:
        os.chdir(d)
        if not os.path.exists('kstyle/themes'): continue
        os.chdir('kstyle/themes')
        styles.update({styleName(file):os.path.abspath(file) for file in glob.glob('*.themerc') if styleName(file) is not None})
    return styles


        
        
        
        
    


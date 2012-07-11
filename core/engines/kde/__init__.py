
import os, logging, json
from ...interface.baseengine import BaseEngine
from ... import config
from . import kdecolors, styles, emoticons, icons, plasmathemes
from PyKDE4.kdeui import KIconTheme

log = logging.getLogger('kde-engine')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='kde-engine: {asctime}: {message}')

hdlr.setFormatter(frm)
log.addHandler(hdlr)

class KdeEngine(BaseEngine):
    '''engine for changing KDE themes, icons & colorschemes'''
    print('loading KDE engine')

    checkerBase = {'color-scheme':kdecolors.listColorSchemes,
                           'style':styles.listStyles,
                           'icons':KIconTheme.list,
                           'emoticons':emoticons.listIconThemes,
                           'plasma-theme':plasmathemes.listThemes
                           }
    
    @staticmethod
    def name():
        return "KDE theme engine"
    
    @classmethod
    def id(cls):
        return 'kde'
    
    @property
    def status(self):
        return self.__status
    
    def lastError(self):
        return self.__lasterr
    
    def writeSettings(self, obj):
        '''check settings dict and if it is good, write to __sett'''
        if not isinstance(obj, dict):
            self.__status = 'configure'
            return
        
        for (k, v) in obj.items():
            if not isinstance (v, dict):
                self.__status = 'configure'
                return
        log.debug('settings looks correctly from here')
        self.__sett = obj
    
    def readSettings(self):
        '''read JSON settings from our conf. dir'''
        self.confpath = os.path.join(config.getConfigPath(self.id()), 'settings')
        self.__sett = {}
        if not os.path.exists(self.confpath):
            self.__status = 'configure'
            return
        try:
            f = open(self.confpath)
            stg = json.load(f)
        except ValueError:
            log.warning('failed to read conf. file, clearing dicts')
            self.__status = 'configure'
            return
        except IOError as e:
            log.error('I/O error: {}'.format(e))
            self.__lasterr = 'Input/Output error: {}'.format(e)
            self.status = 'error'
        finally:
            f.close()
        self.writeSettings(stg)
        
    def checkProfiles(self, *profiles):
        '''check our profiles
        @return: tuple of booleans with results for each profile listed
        '''
        def checker(p):
            if not (p in self.__sett.items()) and isinstance(self.__sett[p], dict):
                return False
            prdict = self.__sett[p]
            
     
            for (k, func) in self.checkerBase.items():
                if k in prdict and prdict[k] not in func():
                    return False
            return True
            
        return map(checker, profiles)
    
    def dumpSettings(self):
        try:
            f = open(self.confpath, 'w')
            json.dump(self.__sett, f)
        except IOError as e:
            log.error('I/O error: {}'.format(e))
            self.__lasterr = 'Input/Output error: {}'.format(e)
            self.status = 'error'
        finally:
            f.close()
        
    def setUp(self, profileid):
        '''set up folowed profile'''
        if not self.checkProfiles(profileid):
            log.debug('Configuration is bad. Exiting')
            self.__status = 'configure'
        prdict = self.__sett[profileid]
        log.debug('preparing to set up... {}'.format(prdict))
        if 'color-scheme' in prdict:
            log.debug('setting color scheme...')
            kdecolors.applyColorScheme(kdecolors.
                        listColorSchemes()[prdict['color-scheme']])
            
        if 'style' in prdict:
            log.debug('setting widget style...')
            styles.applyStyle(prdict['style'])
        
        if 'plasma-theme' in prdict:
            log.debug('setting Plasma theme...')
            plasmathemes.applyTheme(prdict['plasma-theme'])
        
        if 'icons' in prdict:
            log.debug('setting KDE icon theme...')
            icons.applyTheme(prdict['icons'])
            
        if 'emoticons' in prdict:
            log.debug('setting Kopete emoticon theme...')
            emoticons.applyIconTheme(prdict['emoticons'])
            
    def __init__(self):
        self.__status = 'ready'
        self.readSettings()
    
    def proposeSetting(self, profile, t, value):
        '''
        @summary: write setting to config of KDE engine. Useful by front-ends
        @param profile: profile id
        @param t: one of 'color-scheme', 'style', 'plasma-theme', 'icons', 'emoticons'
        @param value: correct setting (theme name)
        @return: true if setting is correct
        '''
        log.debug('called proposeSetting: {},{},{}'.format(profile, t, value))
        if not t in self.checkerBase:
            log.error('{} is not correct type'.format(t))
            return False
        
        if not value in self.checkerBase[t]():
            log.error('{} is not correct value for type {}'.format(value, t))
            return False
        
        if profile not in self.__sett.keys() or type(self.__sett[profile]) is not dict:
            self.__sett[profile] = {t:value}
        else:
            self.__sett[profile][t] = value
        
        log.debug('dumping settings: {}, {}, {}'.format(profile, t, value))
        self.dumpSettings()
        return True

        


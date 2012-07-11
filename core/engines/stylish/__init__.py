'''
detect Stylish profiles for current user
'''

import os, configparser, re
import logging


log = logging.getLogger('stylish-engine')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='stylish-engine: {asctime}: {message}')

hdlr.setFormatter(frm)
log.addHandler(hdlr)

import sqlite3
from core.interface.baseengine import BaseEngine
from ... import config
from itertools import chain

class StylishEngine(BaseEngine):
    '''
    Change stylish theme
    '''
    @staticmethod
    def name():
        return 'Change Stylish themes'
    
    @classmethod
    def id(cls):
        return 'stylish'
    
    def lastError(self):
        return self.__lasterr
        
    @staticmethod
    def firefoxProfileHaveStylish(profile):
        '''return True if profile (firefox) have stylish'''
        if not (isinstance(profile, str)):
            return False
        if os.path.exists(profile):
            os.chdir(profile)
            return os.path.exists('stylish.sqlite')
        else:
            return False
    
    @classmethod
    def settingsDB(cls):
        '''path to sqlite db stores the settings'''
        return os.path.join(config.getConfigPath(cls.id()),
                                                 'settings')
        
       
    @classmethod
    def loadFirefoxProfiles(cls):
        '''
        load firefox profiles from user's home to firefoxProfiles
        call it if you need to(also it calls when you import stylish
        '''
        home = os.path.expanduser('~')
        #now mozilla
        mozpath = os.path.join(home, '.mozilla/firefox')
        if os.path.exists(mozpath):
            os.chdir(mozpath)
            mozparser = configparser.ConfigParser()
            read = mozparser.read('profiles.ini')
            if read:
                profiletempl = re.compile("^Profile\d$")
                profiles = filter(profiletempl.search, mozparser.sections())
                keyname = 'Path' #key for path profile
                prpaths = [os.path.abspath(mozparser[p][keyname]) for p in profiles \
                            if os.path.exists(mozparser[p][keyname])]
                log.debug('Firefox profiles: {}'.format(prpaths)) 
                           
                correct_profiles = tuple(filter(StylishEngine.firefoxProfileHaveStylish, prpaths))
                cls.firefoxProfiles = correct_profiles
                log.debug('Firefox profiles have stylish: {}'.format(cls.firefoxProfiles))



    def needConfigure(self, browprofile=None):
        '''if select count(*) from settings where browprofile=browprofile returns
        zero, then this returns false. Otherwise, true. On error - None
        If browprofile is none, returns just boolean from count of settings
        '''
        try:
            connection = sqlite3.connect(StylishEngine.settingsDB())
        except sqlite3.DatabaseError as err:
            self.__lasterr = 'SQL Error: {}'.format(err)
            self.__status = 'error'
            return None
        
        cur = connection.cursor()
        if browprofile is None:
            sql = 'select count(*) from settings'
            try:
                cur.execute(sql)
            except sqlite3.DatabaseError as err:
                self.__lasterr = 'SQL Error: {}'.format(err)
                self.__status = 'error'
                return None      
    
        elif isinstance(browprofile, str):
            sql = 'select count(*) from settings where browprofile=?'
            try:
                cur.execute(sql, (browprofile))
            except sqlite3.DatabaseError as err:
                self.__lasterr = 'SQL Error: {}'.format(err)
                self.__status = 'error'
                return None
        else:
            raise ValueError('browprofile must be str or None')
        
        res = cur.fetchone()
        if res: res = res[0]
        else: return True
        
        return not bool(res)       
            
            
    @staticmethod
    def execSql(query, connection, *args, **kwargs):
        '''execute sql query  profiles'''
        try:
            connection.cursor().execute(query, args, kwargs)
            connection.commit()
            return True
        except sqlite3.DatabaseError:
            return False
                

    def connect(self):
        '''connect to all profiles' databases'''
        self.connects = dict()
        for pr in StylishEngine.firefoxProfiles:
            try:
                self.connects[os.path.split(pr)[-1]] = (sqlite3.connect(os.path.join(pr, 'stylish.sqlite')))
            except sqlite3.DatabaseError as err:
                log.warning('cant connect to {0}:{1}'.format('stylish.sqlite', err))
                self.__lasterr = 'Can not connect to SQLite'
                self.__status = 'error'
            else:
                log.debug('opened connection to profiles sqlite db: {}'.format(pr))

        #chrome support stub                        
        
    def __init__(self):
        '''
        init stylish engine
        '''
        self.loadSettings()
        StylishEngine.loadFirefoxProfiles()
        self.__lasterr = ''        
        log.debug('try to load profiles: {}'.format(StylishEngine.firefoxProfiles))
        
        if not StylishEngine.firefoxProfiles:
            self.__lasterr = 'No firefox profiles available'
            self.__status = 'error'
        
        self.connect()
        if not self.connects:
            self.__lasterr = 'Can not connect to any of avaliable databases'
            self.__status = 'error'
        else:
            self.__status = 'ready'
            
        if self.needConfigure():
            self.status = 'configure'
    
  
    def loadSettings(self):
        '''loads settings from sqlite3 database'''
        create_table = '''
        create table if not exists settings
        (id integer primary key autoincrement,
        profile text not null,
        browprofile text not null,
        enablelist text,
        disablelist text);
        create index if not exists br_index
        on settings(browprofile);
        create index if not exists pr_index
        on settings (profile);
        '''
        try:
            sett = sqlite3.connect(StylishEngine.settingsDB())
            sett.cursor().executemany(create_table)
            sett.close()
        except sqlite3.DatabaseError as err: 
            self.__status = 'error'
            self.__lasterr = 'SQL query error: {}'.format(err)
        
        
    def getConfigIds(self, profile, browprofile, enable=True):
        '''get IDs of styles from our config db'''
        if enable: action = 'enablelist'
        else: action = 'disablelist'
        
        assert browprofile in self.connects.keys()
        
        conn = sqlite3.connect(StylishEngine.settingsDB())
        try:
            conn.cursor().execute('''select {} from settings where profile=?
            and browprofile=?'''.format(action), (profile, browprofile))
        except sqlite3.DatabaseError as err:
            self.__lasterr = 'SQL query error: {}'.format(err)
            self.__status = 'error'
            
        
        res = conn.cursor().fetchone()
        if res: res = res[0]
        conn.close()
        
        if res:
            lst = res.split(';')
            try:
                result = [int(k) for k in lst]
            except ValueError: #string value
                self.__lasterr = 'Configuration error: string literal in style IDs field'
                self.__status = 'error'
                return []
            else:
                return result
        else:
            return []
    
    def setConfigIds(self, idlist, profile, browprofile, enable=True):
        '''set IDs in our config, to profile profile and browprofile browprofile'''
        assert browprofile in self.connects.keys()
        if enable: action = 'enablelist'
        else: action = 'disablelist'
        if not isinstance(idlist, (list, tuple, set)):
            raise ValueError('idlist should be a sequense')
        
        bad = map(not int, idlist)
        if any(bad): #have non-int values
            log.debug('setIds list has non-integers, raising exception...')
            raise ValueError('idlist should have only ints')
        log('checking if styles exist....')
        set1 = set(idlist)
        set2 = set(self.styles(browprofile).keys())
        if not set1 <= set2:
            raise ValueError ('idlist should have only valid profile IDs')
        idlist = {str(k) for k in idlist}
                
        conn = sqlite3.connect(StylishEngine.settingsDB())
        try:
            conn.cursor().execute('update settings set {}=? where profile=?'.format(
                            action), (';'.join(idlist), profile))
        except sqlite3.DatabaseError as err:
            self.__lasterr = 'SQL query error: {}'.format(err)
            self.__status = 'error'
        finally:
            conn.close()
            
    
    def enable(self, idlist, connection):
        '''enable styles from idlist'''
        for styleid in idlist:
            sqlquery = '''
            update styles set enabled=1 where id=?'''
            if not self.execSql(sqlquery, connection, styleid):
                self.__lasterr = 'SQL query error'
                self.__status = 'error'      
    
    def disable(self, idlist, connection):
        '''disable styles from idlist'''
        for styleid in idlist:
            sqlquery = '''
            update styles set enabled=0 where id=?'''
            if not self.execSql(sqlquery, connection, styleid):
                self.__lasterr = 'SQL query error'
                self.__status = 'error'

        
    def setUp(self, profileid):
        
        #args passed in to getConfigIds
        d = {True: self.enable, False: self.disable}
        
        for (browprofile, conn) in self.connects.items():
            log.debug('using connection {}'.format(conn))          
            for key in d:
                #get ids from config
                ids = self.getConfigIds(profileid, browprofile, key)
                if ids:
                    d[key](ids, conn) #python is so powerful ;)
                else:
                    self.status = 'configure'
                
                            
    def styles(self, browser_profile):
        '''return a dict: {style_id:style_name} for given profile'''
        if browser_profile is None and len(self.connects) == 1:
            cursor = self.connects[tuple(self.connects.keys())[0]].cursor()
        else:
            cursor = self.connects[browser_profile].cursor()
        cursor.row_factory = sqlite3.Row
        try:
            cursor.execute('select id, name from styles')
        except sqlite3.DatabaseError as err:
            self.__lasterr = 'SQL query error: {}'.format(err)
            self.__status = 'error'
            log.debug('SQL error {}'.format(err))

        
        d = {row['id']:row['name'] for row in cursor.fetchall()}
        return d
    
    def checkProfiles(self, *profiles):
        res = []
        for p in profiles:
            resk = []
            for k in self.connects:
                en_set = set(self.getConfigIds(p, k))
                dis_set = set(self.getConfigIds(p, k))
                if not (en_set or dis_set):
                    res.append(False)
                else: #enable set and disable set must be different at all
                    res.append(en_set.isdisjoint(dis_set))
                   
            res.append(bool(resk))
        
        return res
                
                
            
            

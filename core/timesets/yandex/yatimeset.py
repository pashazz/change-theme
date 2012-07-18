#-------------------------------------------------------------------------------
# Copyright (c) 2012 Pavel Borisov
# All rights reserved. ChangeTheme and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
# 
# Contributors:
#     pasha - initial API and implementation
#-------------------------------------------------------------------------------
'''
Created on 24.06.2012

@author: pasha
'''
from . import retreiver
from ...interface import timeset
import sqlite3, logging
from datetime import  date, time, timedelta, datetime
import json
from ... import config
import os
import threading


log = logging.getLogger('yatimeset')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='yatimeset: {asctime}: {message}')

hdlr.setFormatter(frm)
log.addHandler(hdlr)


class YandexTimeset(timeset.TimeSet):
    '''Set time periods using Yandex.Weather service data [sunset/sunrise]
    Many thanks to Yandex.
    '''
    @staticmethod
    def name():
        return "Яндекс.Погода"
    
    @classmethod
    def id(cls):
        return 'yandex'
    
    def lastError(self):
        return self.__lasterr
    
    def __del__(self):
        '''closes connection'''
        
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        self.__status = status
        
    def __init__(self, callback_func):
        '''init'''
        self.callback = callback_func
        self.config = os.path.join(config.getConfigPath(self.id()), 'config')
        self.status = 'init'
        self.__lasterr = ''
        self.__lock = threading.BoundedSemaphore()
        self.readConfig()
    
    def readConfig(self):
        if not os.path.exists(self.config):
            self.confdict = {}
            self.status = 'configure'
        else:
            try:
                self.confdict = json.load(open(self.config, 'r'))
                if retreiver.YandexRetreiver().name(self.confdict.get('id', 0)) is None:
                    self.status = 'configure'

                else: self.status = 'ready'; self.__cityid = self.confdict['id']
            except (IOError, KeyError) as err:
                log.warning('cant read config')
                self.confdict = {}
                self.__lasterr = 'Configuration read failed: {}'.format(err)
                self.status = 'error'
            except ValueError:
                self.status = 'configure'
                self.confdict = {}
    
    def writeConfig(self):
        json.dump(self.confdict, open(self.config, 'w'))    
        
    @property
    def cityid(self):
        return self.__cityid
    
    @cityid.setter
    def cityid(self, cid):
        self.confdict['id'] = cid
        self.writeConfig()
        self.readConfig() 
          
    def nextTime(self):
        '''return a next time for bell (sunset or sunrise) plus deltas from config'''
        now = datetime.now()
        try:
            retr = retreiver.YandexRetreiver()
        except retreiver.InternetConnectionError:
            log.error('please connect to internet')
            
            self.status = 'error'
            return None
        try:
            sunrise, sunset = retr.sunrise(self.__cityid, now.date())
        except retreiver.NoDataError:
            log.info('getting data from tomorrow, today sunset came')
            sunset, sunrise = retr.sunrise(self.__cityid, (now + timedelta(days=1)).date())
        
        daydelta = timedelta(minutes=self.confdict.get('day-begins-after-sunrise-mins', 0))
        nightdelta = timedelta(minutes= -self.confdict.get('night-begins-befort-sunset-mins', 0))
                
        sunrise = (datetime.combine(date.today(), sunrise) + daydelta).time()
        sunset = (datetime.combine(date.today(), sunset) + nightdelta).time()
        
        nowtime = datetime.now().time()
        for t in sunrise, sunset:
            if nowtime < t:
                return t
        #we are after todays sunset (smth like 23-00)
        log.debug(' today sunset came...')
        sunrise = retr.sunrise(self.__cityid, (now + timedelta(days=1)).date())[0]
        sunrise = (datetime.combine(date.today() + timedelta(days=1), sunrise)
                    + daydelta).time()
        return sunrise
    
    def currentPeriod(self):
        '''return current periods id'''
        now = datetime.now()
        try:
            retr = retreiver.YandexRetreiver()
        except retreiver.InternetConnectionError:
            log.error('please connect to internet')
            self.__lasterr = 'Error when retreiving from Yandex. Is internet connection available?'
            self.status = 'error'
            return None
        try:
            sunrise, sunset = retr.sunrise(self.__cityid, now.date())
        except retreiver.NoDataError:
            log.info('getting data from tomorrow, today sunset came')
            sunset, sunrise = retr.sunrise(self.__cityid, (now + timedelta(days=1)).date())
        
        daydelta = timedelta(minutes=self.confdict.get('day-begins-after-sunrise-mins', 0))
        nightdelta = timedelta(minutes= -self.confdict.get('night-begins-befort-sunset-mins', 0))
        nowtime = datetime.now().time()
        sunrise = (datetime.combine(date.today(), sunrise) + daydelta).time()
        sunset = (datetime.combine(date.today(), sunset) + nightdelta).time()
        if sunrise <= nowtime < sunset:
            return 'yandex-day'
        else:
            return 'yandex-night'

    
    def __start(self):
        '''
        First check system time. Then gen next sunrise or sunset
        Then go to loop until this time comes, and when time comes, start from scratch.
        '''
        
        nextTime = self.nextTime()
        self.callback(self.currentPeriod())
        while True:
            now = datetime.now().time()
            if now.hour == nextTime.hour and now.minute == nextTime.minute and now.second == nextTime.second: 
                log.info('Time reached: {}'.format(nextTime))
                nextTime = self.nextTime()
                period = self.period()
                log.info('New nextTime: {}, period {}'.format(nextTime, period))
                self.callback(period)
            self.__lock.acquire()
            if self.status == 'waitstop':
                self.status = 'ready'
                log.info('Stopping called')
                self.__lock.release()
                break
            self.__lock.release()
            
        
    def start(self):
        '''call real start'''
        if self.status == 'ready':
            threading.Thread(target=self.__start).start()
            return True
        else: return False
    
    def stop(self):
        '''stop the loop'''
        self.__lock.acquire()
        self.status = 'waitstop'
        self.__lock.release()
        
    @property
    def day_delta(self):
        return self.confdict.get('day-begins-after-sunrise-mins')
        
    @day_delta.setter
    def day_delta(self, mins):
        if not isinstance(mins, int):
            raise ValueError()
        self.confdict['day-begins-after-sunrise-mins'] = mins
        self.writeConfig()
        self.readConfig()
        
    @property       
    def night_delta(self):
        return self.confdict.get('day-begins-before-sunset-mins')
    
    @night_delta.setter
    def night_delta(self, mins):
        if not isinstance(mins, int):
            raise ValueError()
        self.confdict['day-begins-before-sunset-mins'] = mins
        self.writeConfig()
        self.readConfig()     
        
        
    
 

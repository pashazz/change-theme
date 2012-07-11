from ...interface import timeset
from ... import config
import os, json, logging, threading
from time import sleep
import time as tm
from datetime import datetime, timedelta, time, date
from collections import OrderedDict

log = logging.getLogger('timing')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='TimeSettings-manual: {asctime}: {message}')

hdlr.setFormatter(frm)
log.addHandler(hdlr)

timeformat = '%H:%M' #hour:minute
class ManualTimeset(timeset.TimeSet):
    '''
    set up all times manually
    '''
    conffile = os.path.join(config.getConfigPath('timing'), 'times')
    
    def writeSettings(self):
        '''do time->str conversion and write to JSON'''
            
        with open(self.conffile, 'wt') as file:
            json.dump(self.__stg, file)

    def name(self):
        return 'Set time periods manually'
    
    def id(self):
        return 'manual'
    
    def defaultConfig(self):
        '''@summary:  set up __default__ configuration'''
        log.warning("can't find configuration at {}, creating defaults".format(self.conffile))
        s = {'day':('10:00', '20:00'), 'night':('20:00', '10:00')}
        self.setSettings(s)
        
        
    def loadSettings(self):
        '''loads settings from JSON and give to readSettings'''
        if not os.path.exists(self.conffile):
            self.defaultConfig()
            return
            
        try:
            file = open(self.conffile, 'rt') 
            settings = OrderedDict(json.load(file))    
        except (IOError, ValueError, TypeError) as e:
            self.__lasterr = 'File error when loading config: {}'.format(e)
            self.__status = 'error'
        else:
            self.readSettings(settings)    
        finally:
            file.close()
        
    
    def readSettings(self, settings):
        '''reads settings and check if it is right
        @note: does str->struct_time conversion
        '''
        if not isinstance(settings, dict):
            self.__status = 'configure'
        
        
        def checker(v): return isinstance(v, (list, tuple)) and len(v) == 2
        

                 
            
        log.info('reading settings in format:JSON')
        
        if False in map(checker, tuple(settings.values())):
            self.__lasterr = 'Incorrect configuration. Double-check it'
            self.__status = 'error'
            return
        
        for (i, v) in enumerate(tuple(settings.values())):
            if not(v[0] == tuple(settings.values())[i - 1][1]):
                self.__lasterr = "Misconfiguration: Stop of {} is not start of {}".format(
                                                    i - 1, i)
                log.error('{} != {}'.format(tuple(settings.values())[i - 1][1],
                                        v[0]))
                self.__status = 'error'
                return
        
        self.__stg = OrderedDict()

        log.debug('Sorting....')#use first time to sort
        self.__stg = OrderedDict(sorted(settings.items(), key=lambda v:v[1][0]))
                
        log.debug('settings loaded into self.__stg: {}'.format(self.__stg))
        self.__status = 'ready'
        
    def profiles(self):
        '''in manual, ids of profiles == names of profiles since they set up manually
        by user's hands'''
        return {i:i for i in self.__stg}
            
    def checkProfiles(self, *profiles):
        '''check if these profiles exists'''
        return set(profiles).issubset(set(self.__stg.keys())) if profiles else False
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, st):
        self.__status = st  
    
    def clear(self):
        self.__stg.clear()
        self.status = 'configure'
        
    def setSettings(self, value):
        '''Set folowing settings. Useful for front-ends'''
        self.readSettings(value)
        if not self.status == 'ready':
            log.error('Exception, status={}'.format(self.status))
            return
        log.debug('Writing settings into {}'.format(self.conffile))
        self.writeSettings()
        
    
    def __init__(self, callback_func):
        self.callback = callback_func
        self.status = 'ready'
        self.__lasterr = ''
        log.debug('Loading manual settings')
        self.loadSettings()
        self.__lock = threading.Lock()

    def lastError(self):
        return self.__lasterr
    
    def currentPeriod(self):
        '''@summary: return period of current time'''
        #http://stackoverflow.com/questions/79797/how-do-i-convert-local-time-to-utc-in-python
        def convertTimetoTuple(localDate, localTime):
            if isinstance (localTime, str): #convert to time
                localTime = datetime.strptime(localTime, timeformat).time()
            elif not isinstance (localTime, time):
                raise ValueError
            
            return datetime.combine(localDate, localTime
                                        ).timetuple()
            
        # case I: regular cycle
        for (i, t) in self.__stg.items():
            start = convertTimetoTuple(date.today(), t[0])
            stop = convertTimetoTuple(date.today(), t[1])
            now = tm.gmtime()
            if start <= now < stop:
                
                log.info('Period is {}'.format(i))
                return i
        # case II: we are smth near midnight and period ends in tomorrow
        lastStart = convertTimetoTuple(date.today(), tuple(self.__stg.values())[-1][0])
        lastStop = convertTimetoTuple(date.today() + timedelta(days=1), tuple(self.__stg.values())[-1][1])
        now = tm.gmtime()
        if lastStart <= now < lastStop:
            log.info('period is last')
            return tuple(self.__stg.keys())[-1]
        
        # case III: we are after midnigth and start of period is yesterday                                           
        lastStart = convertTimetoTuple(date.today() - timedelta(days=1), tuple(self.__stg.values())[-1][0])
        lastStop = convertTimetoTuple(date.today(), tuple(self.__stg.values())[-1][1])
        if lastStart <= now < lastStop:
            log.info('period is last')
            return tuple(self.__stg.keys())[-1]
        
        log.error("FATAL ERROR: WE SHOULD NOT BE THERE!!!")
        self.__lasterr = 'Runtime Error'
        self.status = 'error'
        
    
    def start(self):
        '''@summary: start different tread with self.start()'''
        threading.Thread(target=self._start, name='serverloop').start()
        
    def stop(self):
        '''@summary: stops the loop'''
        self.__lock.acquire()
        self.status = 'waitstop'
        self.__lock.release()
        
    def _start(self):
        '''Starts the loop'''
        self.status = 'running'
        
        def do_callback():
            '''call back to engines'''
            log.debug('The current period is...')
            period = self.currentPeriod()
            log.debug(period)
            self.callback(period)               
            return self.__stg[period]
        
        pList = do_callback()
        while True:
            now = tm.localtime()
            dest = tm.strptime(pList[1], timeformat)
            if now.tm_hour == dest.tm_hour and now.tm_min == dest.tm_min and  now.tm_sec == dest.tm_sec:
                pList = do_callback()  #почти никогда не выполняется
                sleep(1)                   
            else:
                print ('{} != {}'.format(now, dest))

            
            if self.status == 'waitstop':
                self.__lock.acquire()
                self.status = 'ready'
                self.__lock.release()
                log.info('Stopping called')
                break
            sleep(.1)

                     

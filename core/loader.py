'''
Created on 26.06.2012

@author: pasha

To be used as context manager!
'''
from . import config
import os, logging
from .timesets.yandex import yatimeset
from .engines.stylish import StylishEngine
from .interface import baseengine, timeset
import threading

log = logging.getLogger('loader')
hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
frm = logging.Formatter(style="{", fmt='AppLoader: {asctime}: {message}')

from yaml import load, dump

class TimesetError(Exception):pass#for timesets errors
class TimesetConfigure(Exception): pass  #for timesets CONFIGURE statuses
class AppLoader:
    '''load configs from yaml file and initialize loops'''
    def __enter__(self):
        '''don't know what here must be'''
        
    def stopDaemon(self):
        '''stops timeset loop'''
        if self.running:
            self.running.stop()
        else:
            log.debug('no loop running!')
    
    def write(self):
        '''write YAML config'''
        with open(config.appConfYaml, 'wt') as conf:
            dump(self.__stg_dict, conf)
    
    def read(self):
        '''read YAML config'''
        with open (config.appConfYaml, 'rt') as conf:
            self.__stg_dict = load(conf)
        if not (self.__stg_dict and isinstance(self.__stg_dict, dict)):
            log.warning('empty/unsafe configuration, writing new')
            self.__stg_dict = {'General':
                        {'time-source':'yandex',
                         'enabled-engines':'stylish'
                         }
                        }
            self.write()
            
    def runStatusLoop(self):
        '''status loop code. Raises callback every time status had changed
        of any engine. To stop, set self.stopSLoop to true'''
        statuses = [e.status for e in self.__loadedEngines]
        while True:
            if hasattr(self, 'stopSLoop') and getattr(self, 'stopSLoop', False):
                log.debug('stopping called to engines status loop')
                del self.stopSLoop
                break
            
            for (i, e) in enumerate(self.__loadedEngines):
                if not e.status == statuses[i]:
                    self.callback(e, e.status, e.lastError())
                if e.status == 'error':
                    log.error('error in engine {} - unloading')
                    del self.__loadedEngines[i]
            
            if self.running:
                if self.running.status == 'error':
                    raise TimesetError()
                elif self.running.status == 'configure':
                    raise TimesetConfigure()

    def activateEngines(self, profileid):
        '''callback function to call setUp in all available engines'''
        log.debug('activateEngines: activating profile {}'.format(profileid))
        for e in self.__loadedEngines:
            if not e.status == 'ready':
                log.warning('skipping engine {0}, because it has status "{0.status}"'.format(e))
                continue
            
            e.setUp(profileid) 
    
            
    def loadEngines(self, engines):
        '''loads engines (dict), writes dict with keys from first dict and vars of engines into
        self.__loadedEngines
        '''
        if not isinstance(engines, dict):
            log.warning("Warning: no engines loaded")
            return
            
        self.__loadedEngines = []
        
        for (k, v) in engines.items():
            engine = v()
            if not engine.status == 'error':
                self.__loadedEngines.append(engine)
            self.callback(engine, engine.status, engine.lastError())
        
        log.debug('starting 2nd thread with status loop')
        threading.Thread(target=self.runStatusLoop, name='statusloop').start()
    
    def stopAll(self):
        '''stops both status loop and timeset loop'''
        self.stopDaemon()
        self.stopSLoop = True
    
  
    
    def __del__(self):
        '''stops all'''
        self.stopAll()
        
    @property
    def loadedEngines(self):
        return self.__loadedEngines        
                
    def __init__(self, status_callback, eng_list=None):
        '''init with:
        status_callback - function called when status changes
        signature: status_call(engineobj, statustext, lasterror)
        eng_list - specified list of enabled engines. If None, then
        all engines is enabled
        '''
        
        log.debug('read YAML file {}'.format(config.appConfYaml))
        self.read()      
        
        self.__engines = {StylishEngine.id():StylishEngine}
        self.__timesets = {yatimeset.YandexTimeset.id():yatimeset.YandexTimeset}
        if eng_list is not None:
            for i in self.__engines:
                if not i in eng_list:
                    del self.__engines[i]
        else:      
            log.info ('checking desktop environment and loading engines')
            #STUB
        #now only stylish
        self.callback = status_callback
        #set to current timeset if running, see startDaemon
        self.running = None
   
        #for locking for status loop
        self.loadEngines(self.__engines)
        
                        
        log.info('{0} loaded successfully. \n Available timesets: {1}\n Loaded Engines:{2}'.format
                 (config.appFullName, self.__timesets, self.__loadedEngines))
        
        
    def startDaemon(self, daemonString=None):
        '''starts the loop of selected daemon
        if daemonString is None, then selects it from YAML:General/time-source
        '''
        if daemonString:
            tsetkey = daemonString
        else:
            tsetkey = self.__stg_dict['General']['time-source']
        log.debug('selected timeset: {}'.format(tsetkey))
        log.debug('check if timeset exists')
        try:
            tset = self.__timesets[tsetkey]
        except KeyError:
            log.error('Incorrect configuration, No such timeset!')
            raise ValueError('Can not find timeset')
        
        timeset = tset(self.activateEngines)
        log.debug('loading timeset  {}...'.format(timeset.name()))

        if timeset.status == 'error':
            log.debug('fail')
            raise TimesetError('In timeset {0}: Error:{1}'.format(
                                    timeset.id(), timeset.lastError()))
        if timeset.status == 'configure':
            log.warning('needs configuring.\nError:{}'.format(timeset.lastError()))
            raise TimesetConfigure(
            'Timeset {0} should be configured properly. See console for details').format(timeset.id())
        
        log.debug('ok')
        
        log.info('starting TimeSet {}'.format(timeset))
        self.running = timeset
        timeset.start()

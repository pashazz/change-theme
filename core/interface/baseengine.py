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

class EngineError(RuntimeError): pass
class EngineConfigurationError(ValueError): pass

class BaseEngine(object):
    '''Base engine for changing themes'''
    
    def __init__(self):
        raise NotImplementedError()
    
    @staticmethod
    def name():
        '''Name of timeset'''
        raise NotImplementedError()
    
    @classmethod
    def id(cls):
        '''id of timeset,used in configs'''
        raise NotImplementedError()
    
    def lastError(self):
        '''our last error in string format'''
        return "Not implemented"
    
    def status(self):
        '''one of error,configure,ready'''
        raise NotImplementedError()
                
    def setUp(self, profileid):
        '''Sets up profile profile id. All code that changes themes should be here'''
        raise NotImplementedError()
    
    def __str__(self):
        return "Theme Engine: {}".format(self.name())
    
    def checkProfiles(self, *profiles):
        '''check if we have correct configuration for working
        with these profiles. Return iterable, with bool values, len=len(profiles)'''
        return NotImplementedError()
    
        

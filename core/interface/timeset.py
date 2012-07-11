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
class TimesetError(ValueError): pass
class InternetConnectionError(ValueError): pass

class TimeSet(object):
    '''
    Base class for all the timesets
    '''
    def __init__(self, callback_func):
        '''init timeset with callback_func (call when need to activate profile.
        callback func has 1 arg:
        profile id
        '''
        raise NotImplementedError()
    
    @staticmethod
    def name():
        '''Name of timeset'''
        raise NotImplementedError()
    
    @classmethod
    def id(cls):
        '''id of timeset'''
        raise NotImplementedError()
    
    def lastError(self):
        '''our last error in string format'''
        return "Not implemented"
    
    def start(self):
        '''starts the loop'''
        raise NotImplementedError()
    
    def stop(self):
        '''stops the loop'''
        raise NotImplementedError()
        
    def status(self):
        '''one of folowing:
        started
        ready
        error
        configure
        '''
        raise NotImplementedError()
           
    def profiles(self):
        '''return tuple of tuples(id,human_readable_name) of profiles'''
        raise NotImplementedError()
        
    
    def __repr__(self):
        return "Timeset: {}".format(self.name())
    


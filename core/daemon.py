'''
Created on 26.06.2012

@author: pasha
'''

from .interface import baseengine, timeset

class Daemon:
    '''
    "while true" loop which controls all the logic. But first, let's get data from respective timeset
    '''
    def __init__(self, timeset, engines_list):
        
    

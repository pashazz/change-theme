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
#!/usr/bin/env python3
'''
Created on 22.06.2012

@author: pasha
'''
import os, re 
import configparser
def getProfilePath(home=None):
    '''Gets mozilla/chrome profiles aval. for current user and returns a list with results'''
    res = dict()
    if home is None:
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
            res['firefox'] = prpaths
    #now chrome
     
    
    return res

import os, logging

appName = "change-theme"
appFullName = 'ChangeTheme'
appAuthor = 'Pavel Borisov, 2012'
qtEngine = 'PyQt4'
appConfDir = os.path.join (os.path.expanduser('~'), '.config', appName)
appConfYaml = os.path.join (os.path.expanduser('~'), '.config', '{appname}.yaml'.format(appname=appName))

if not os.path.exists(appConfDir):
    os.mkdir(appConfDir)
    
hdlr = logging.StreamHandler
#future

def getConfigPath(id):
    '''cls - class, id- possible pathname, create if need to'''
    os.chdir(appConfDir)
    if not os.path.exists(id):
        os.mkdir(id)
    return os.path.abspath(id)
        
        

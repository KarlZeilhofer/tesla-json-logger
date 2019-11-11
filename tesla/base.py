import os
import time
import logging

# Some global constants
site = 'owner-api.teslamotors.com'
appname = 'tesla-json-logger'
appDataPath = os.path.expanduser('~/.config/'+appname)
rcFile = os.path.join(appDataPath, 'teslarc')
logHome = os.path.join(appDataPath, 'logs')
dataLogHome = os.path.join(appDataPath, 'data')
logger = logging.getLogger(appname)

def createPaths():
    if not os.path.exists(appDataPath):
        os.mkdir(appDataPath)

    if not os.path.exists(logHome):
        os.mkdir(logHome)
        
    if not os.path.exists(dataLogHome):
        os.mkdir(dataLogHome)


def setLogPrefix(prefix):
    logfile = '{}/{}-{}.log'.format(logHome, prefix, time.strftime('%Y%m%d', time.localtime(time.time())))
    fileHandler = logging.FileHandler(logfile, 'a')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
    logger.addHandler(fileHandler)
    return logfile


def getLogfile():
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            return h.baseFilename


def showMessageLevel(level):
    if len(logger.handlers) == 1:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)
    for h in logger.handlers:
        if not isinstance(h, logging.FileHandler):
            h.setLevel(level)
    if level < logging.INFO:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)


def showWarningMessages():
    showMessageLevel(logging.WARNING)


def showDebugMessages():
    showMessageLevel(logging.DEBUG)


def showInfoMessages():
    showMessageLevel(logging.INFO)

# ----------------------------

# Logger
if os.path.exists(logHome):
    setLogPrefix('tesla')
showWarningMessages()

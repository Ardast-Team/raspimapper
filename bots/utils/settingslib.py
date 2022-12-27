import sys
import os
import posixpath
import datetime as python_datetime
import codecs
import traceback
import socket
import platform
import collections
import pickle
import importlib
import django
#import configparser
import unicodedata
#bots-modules (no code)
from bots.utils import botsglobal
from bots.utils.botsconfig import *
'''
Base library for bots. Botslib should not import code from other Bots-modules.
'''
MAXINT = (2**31) -1
#**********************************************************/**
#**************getters/setters for some globals***********************/**
#**********************************************************/**
def setrouteid(routeid):
    botsglobal.routeid = routeid

def getrouteid():
    return botsglobal.routeid

#**********************************************************/**
#*************************Logging, Error handling********************/**
#**********************************************************/**
def sendbotserrorreport(subject,reporttext):
    ''' Send an email in case of errors or problems with bots-engine.
        Email is send to MANAGERS in config/settings.py.
        Email parameters are in config/settings.py (EMAIL_HOST, etc).
    '''
    if botsglobal.ini.getboolean('settings','sendreportiferror',False) and not botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
        from django.core.mail import mail_managers
        try:
            mail_managers(subject, reporttext)
        except Exception as msg:
            botsglobal.logger.warning('Error in sending error report: %(msg)s',{'msg':msg})

def txtexc():
    ''' Process last exception, get an errortext.
        Errortext should be valid unicode.
    '''
    if botsglobal.ini and botsglobal.ini.getboolean('settings','debug',False):
        return traceback.format_exc(limit=None)
    else:
        terug = traceback.format_exc(limit=0)
        terug = terug.replace('Traceback (most recent call last):\n','')
        terug = terug.replace('bots.botslib.','')
        return terug

#**********************************************************/**
#*************************import ***********************/**
#**********************************************************/**
def botsbaseimport(modulename):
    ''' Do a dynamic import.
        Errors/exceptions are handled in calling functions.
    '''
    a = modulename.encode(sys.getfilesystemencoding())
    return importlib.import_module(modulename,'bots')

def botsimport(*args):
    ''' import modules from usersys.
        return: imported module, filename imported module;
        if not found or error in module: raise
    '''
    modulepath = '.'.join((botsglobal.usersysimportpath,) + args)             #assemble import string
    modulefile = join(botsglobal.ini.get('directories','usersysabs'),*args)   #assemble abs filename for errortexts; note that 'join' is function in this script-file.
    if modulepath in botsglobal.not_import:     #check if previous import failed (no need to try again).This eliminates eg lots of partner specific imports.
        botsglobal.logger.debug('No import of module "%(modulefile)s".',{'modulefile':modulefile})
        raise BotsImportError('No import of module "%(modulefile)s".',{'modulefile':modulefile})
    try:
        module = botsbaseimport(modulepath)
    except ImportError as msg:
        botsglobal.not_import.add(modulepath)
        botsglobal.logger.debug('No import of module "%(modulefile)s": %(txt)s.',{'modulefile':modulefile,'txt':msg})
        raise BotsImportError('No import of module "%(modulefile)s": %(txt)s',{'modulefile':modulefile,'txt':msg})
    except Exception as msg:
        botsglobal.logger.debug('Error in import of module "%(modulefile)s": %(txt)s.',{'modulefile':modulefile,'txt':msg})
        raise ScriptImportError('Error in import of module "%(modulefile)s":\n%(txt)s',{'modulefile':modulefile,'txt':msg})
    else:
        botsglobal.logger.debug('Imported "%(modulefile)s".',{'modulefile':modulefile})
        return module,modulefile
#**********************************************************/**
#*************************File handling os.path etc***********************/**
#**********************************************************/**
def join(*paths):
    '''Does does more as join.....
        - join the paths (compare os.path.join)
        - if path is not absolute, interpretate this as relative from bots directory.
        - normalize'''
    return os.path.normpath(os.path.join(botsglobal.ini.get('directories','botspath'),*paths))

def dirshouldbethere(path):
    if path and not os.path.exists(path):
        os.makedirs(path)
        return True
    return False

def abspath(soort,filename):
    ''' get absolute path for internal files; path is a section in bots.ini '''
    directory = botsglobal.ini.get('directories',soort)
    return join(directory,filename)

def abspathdata(filename):
    ''' abspathdata if filename incl dir: return absolute path; else (only filename): return absolute path (datadir)'''
    if '/' in filename: #if filename already contains path
        return join(filename)
    else:
        directory = botsglobal.ini.get('directories','data')
        datasubdir = filename[:-3]
        if not datasubdir:
            datasubdir = '0'
        return join(directory,datasubdir,filename)

def deldata(filename):
    ''' delete internal data file.'''
    filename = abspathdata(filename)
    try:
        os.remove(filename)
    except:
        pass

def opendata(filename,mode,charset,errors='strict'):
    ''' open internal data file as unicode.'''
    filename = abspathdata(filename)
    if 'w' in mode:
        dirshouldbethere(os.path.dirname(filename))
    return codecs.open(filename,mode,charset,errors)

def readdata(filename,charset,errors='strict'):
    ''' read internal data file in memory as unicode.'''
    filehandler = opendata(filename,'r',charset,errors)
    content = filehandler.read()
    filehandler.close()
    return content

def opendata_bin(filename,mode):
    ''' open internal data file as binary.'''
    filename = abspathdata(filename)
    if 'w' in mode:
        dirshouldbethere(os.path.dirname(filename))
    return open(filename,mode)

def readdata_bin(filename):
    ''' read internal data file in memory as binary.'''
    filehandler = opendata_bin(filename,mode='rb')
    content = filehandler.read()
    filehandler.close()
    return content

def readdata_pickled(filename):
    filehandler = opendata_bin(filename,mode='rb') #pickle is a binary/byte stream
    content = pickle.load(filehandler)
    filehandler.close()
    return content

def writedata_pickled(filename,content):
    filehandler = opendata_bin(filename,mode='wb') #pickle is a binary/byte stream
    pickle.dump(content,filehandler)
    filehandler.close()

#**********************************************************/**
#*************************calling modules, programs***********************/**
#**********************************************************/**
def runscript(module,modulefile,functioninscript,**argv):
    ''' Execute userscript. Functioninscript is supposed to be there; if not AttributeError is raised.
        Often is checked in advance if Functioninscript does exist.
    '''
    botsglobal.logger.debug('Run userscript "%(functioninscript)s" in "%(modulefile)s".',
                            {'functioninscript':functioninscript,'modulefile':modulefile})
    functiontorun = getattr(module, functioninscript)
    try:
        return functiontorun(**argv)
    except (ParsePassthroughException,KillWholeFileException):  #special cases; these exceptions are handled later in specific ways.
        raise
    except:
        txt = txtexc()
        raise ScriptError('Userscript "%(modulefile)s": "%(txt)s".',{'modulefile':modulefile,'txt':txt})

def tryrunscript(module,modulefile,functioninscript,**argv):
    if module and hasattr(module,functioninscript):
        runscript(module,modulefile,functioninscript,**argv)
        return True
    return False

def runscriptyield(module,modulefile,functioninscript,**argv):
    botsglobal.logger.debug('Run userscript "%(functioninscript)s" in "%(modulefile)s".',
                            {'functioninscript':functioninscript,'modulefile':modulefile})
    functiontorun = getattr(module, functioninscript)
    try:
        for result in functiontorun(**argv):
            yield result
    except:
        txt = txtexc()
        raise ScriptError('Script file "%(modulefile)s": "%(txt)s".',{'modulefile':modulefile,'txt':txt})

def botsinfo():
    return [
            ('served at port',botsglobal.ini.getint('webserver','port',8080)),
            ('platform',platform.platform()),
            ('machine',platform.machine()),
            ('python version',platform.python_version()),
            ('django version',django.VERSION),
            ('bots version',botsglobal.version),
            ('bots installation path',botsglobal.ini.get('directories','botspath')),
            ('config path',botsglobal.ini.get('directories','config')),
            ('botssys path',botsglobal.ini.get('directories','botssys')),
            ('usersys path',botsglobal.ini.get('directories','usersysabs')),
            ('local date/time',python_datetime.datetime.today().isoformat()),
            ('DATABASE_ENGINE',botsglobal.settings.DATABASES['default']['ENGINE']),
            ('DATABASE_NAME',botsglobal.settings.DATABASES['default']['NAME']),
            ('DATABASE_USER',botsglobal.settings.DATABASES['default']['USER']),
            ('DATABASE_HOST',botsglobal.settings.DATABASES['default']['HOST']),
            ('DATABASE_PORT',botsglobal.settings.DATABASES['default']['PORT']),
            ('DATABASE_OPTIONS',botsglobal.settings.DATABASES['default']['OPTIONS']),
            ]

def datetime():
    ''' for use in acceptance testing: returns pythons usual datetime - but frozen value for acceptance testing.
    '''
    if botsglobal.ini.getboolean('acceptance','runacceptancetest',False):
        return python_datetime.datetime(2013,1,23,1,23,45)
    else:
        return python_datetime.datetime.today()

def strftime(timeformat):
    ''' for use in acceptance testing: returns pythons usual string with date/time - but frozen value for acceptance testing.
    '''
    return datetime().strftime(timeformat)

def settimeout(milliseconds):
    socket.setdefaulttimeout(milliseconds)    #set a time-out for TCP-IP connections

def updateunlessset(updatedict,fromdict):
    updatedict.update((key,value) for key, value in fromdict.items() if key not in updatedict or not updatedict[key]) #!!TODO when is this valid? Note: prevents setting charset from grammar

def rreplace(org,old,new='',count=1):
    ''' string handling:
        replace old with new in org, max count times.
        with default values: remove last occurence of old in org.
    '''
    lijst = org.rsplit(old,count)
    return new.join(lijst)

def get_relevant_text_for_UnicodeError(msg):
    ''' see python doc for details of UnicodeError'''
    start = msg.start - 10 if msg.start >= 10 else 0
    return msg.object[start:msg.end+35]

def indent_xml(node, level=0,indentstring='    '):
    text2indent = '\n' + level*indentstring
    if len(node):
        if not node.text or not node.text.strip():
            node.text = text2indent + indentstring
        for subnode in node:
            indent_xml(subnode, level+1)
            if not subnode.tail or not subnode.tail.strip():
                subnode.tail = text2indent + indentstring
        if not subnode.tail or not subnode.tail.strip():
            subnode.tail = text2indent
    else:
        if level and (not node.tail or not node.tail.strip()):
            node.tail = text2indent


class Uri(object):
    ''' generate uri from parts/components
        - different forms of uri (eg with/without password)
        - general layout like 'scheme://user:pass@hostname:80/path/filename?query=argument#fragment'
        - checks: 1. what is required; 2. all parameters need to be valid
        Notes:
        - no filename: path ends with '/'
        Usage: uri = Uri(scheme='http',username='hje',password='password',hostname='test.com',port='80', path='')
        Usage: uri = Uri(scheme='http',hostname='test.com',port='80', path='test')
    '''
    def __init__(self, **kw):
        self._uri = dict(scheme='',username='',password='',hostname='',port='', path='', filename='',query={},fragment='')
        self.update(**kw)
    def update( self, **kw):
        self._uri.update(**kw)
    def uri(self, **kw):
        self.update(**kw)
        return self.__str__()
    def __str__(self):
        scheme   = self._uri['scheme'] + ':' if self._uri['scheme'] else ''
        password = ':' + self._uri['password'] if self._uri['password'] else ''
        userinfo = self._uri['username'] + password + '@' if self._uri['username'] else ''
        port     = ':' + unicodedata(self._uri['port']) if self._uri['port'] else ''
        fullhost = self._uri['hostname'] + port if self._uri['hostname'] else ''
        authority = '//' + userinfo + fullhost if fullhost else ''
        if self._uri['path'] or self._uri['filename']:
            terug = posixpath.join(authority,self._uri['path'],self._uri['filename'])
        else:
            terug = authority
        return scheme + terug
#**********************************************************/**
#**************  Exception classes ***************************
#**********************************************************/**
class BotsError(Exception):
    ''' formats the error messages. Under all circumstances: give (reasonable) output, no errors.
        input (msg,*args,**kwargs) can be anything: strings (any charset), unicode, objects. Note that these are errors, so input can be 'not valid'!
        to avoid the risk of 'errors during errors' catch-all solutions are used.
        2 ways to raise Exceptions:
        - BotsError('tekst %(var1)s %(var2)s',{'var1':'value1','var2':'value2'})  ###this one is preferred!!
        - BotsError('tekst %(var1)s %(var2)s',var1='value1',var2='value2')
    '''
    def __init__(self, msg,*args,**kwargs):
        self.msg = msg
        if args:    #expect args[0] to be a dict
            if isinstance(args[0],dict):
                xxx = args[0]
            else:
                xxx = {}
        else:
            xxx = kwargs
        self.xxx = collections.defaultdict()
        for key,value in xxx.items():
            self.xxx[key] = value
    def __unicode__(self):
        try:
            return self.msg%(self.xxx)    #this is already unicode
        except:
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX12')
            return self.msg             #errors in self.msg; non supported format codes. Don't think this happen...
    def __str__(self):
        try:
            return self.msg%(self.xxx)
        except:
            print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX13')
            return self.msg.encode('utf-8','ignore')            #errors in self.msg; non supported format codes. Don't think this happen...

class CodeConversionError(BotsError):
    pass
class CommunicationError(BotsError):
    pass
class CommunicationInError(BotsError):
    pass
class CommunicationOutError(BotsError):
    pass
class EanError(BotsError):
    pass
class GrammarError(BotsError):
    pass
class GrammarPartMissing(BotsError):
    pass
class InMessageError(BotsError):
    pass
class LockedFileError(BotsError):
    pass
class MessageError(BotsError):
    pass
class MessageRootError(BotsError):
    pass
class MappingRootError(BotsError):
    pass
class MappingFormatError(BotsError):
    pass
class OutMessageError(BotsError):
    pass
class PanicError(BotsError):
    pass
class PersistError(BotsError):
    pass
class PluginError(BotsError):
    pass
class BotsImportError(BotsError):    #import script or recursivly imported scripts not there
    pass
class ScriptImportError(BotsError):    #import errors in userscript; userscript is there
    pass
class ScriptError(BotsError):          #runtime errors in a userscript
    pass
class TraceError(BotsError):
    pass
class TranslationNotFoundError(BotsError):
    pass
class ParsePassthroughException(BotsError):     #to handle Parse and passthrough. Can be via translationrule or in mapping.
    pass
class DummyException(BotsError):     #sometimes it is simplest to raise an error, and catch it rightaway. Like a goto ;-)
    pass
class KillWholeFileException(BotsError):     #used to error whole edi-file out (instead of only a message)
    pass
class FileTooLargeError(BotsError):
    pass

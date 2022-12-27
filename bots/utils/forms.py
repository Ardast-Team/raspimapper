from django import forms
#***********
from bots import models
#from bots.utils import viewlib
from bots.utils import botsglobal
import datetime

HIDDENINPUT = forms.widgets.HiddenInput

def datetimefrom():
    terug = datetime.datetime.today() - datetime.timedelta(days=botsglobal.ini.getint('settings','maxdays',30))
    return terug.strftime('%Y-%m-%d 00:00:00')

def datetimeuntil():
    terug = datetime.datetime.today()
    return terug.strftime('%Y-%m-%d 23:59:59')

class Select(forms.Form):
    datefrom = forms.DateTimeField(initial=datetimefrom)
    dateuntil = forms.DateTimeField(initial=datetimeuntil)
    page = forms.IntegerField(required=False,initial=1,widget=HIDDENINPUT())
    sortedby = forms.CharField(initial='ts',widget=HIDDENINPUT())
    sortedasc = forms.BooleanField(initial=False,required=False,widget=HIDDENINPUT())

class View(forms.Form):
    datefrom = forms.DateTimeField(required=False,initial=datetimefrom,widget=HIDDENINPUT())
    dateuntil = forms.DateTimeField(required=False,initial=datetimeuntil,widget=HIDDENINPUT())
    page = forms.IntegerField(required=False,initial=1,widget=HIDDENINPUT())
    sortedby = forms.CharField(required=False,initial='ts',widget=HIDDENINPUT())
    sortedasc = forms.BooleanField(required=False,initial=False,widget=HIDDENINPUT())

class SelectReports(Select):
    template = 'bots/selectform.html'
    action = '/reports/'
    status = forms.ChoiceField(choices=[models.DEFAULT_ENTRY,('1','Error'),('0','Done')],required=False,initial='')

class ViewReports(View):
    template = 'bots/reports.html'
    action = '/reports/'
    status = forms.IntegerField(required=False,initial='',widget=HIDDENINPUT())

class SelectIncoming(Select):
    template = 'bots/selectform.html'
    action = '/incoming/'
    statust = forms.ChoiceField(choices=[models.DEFAULT_ENTRY,('1','Error'),('3','Done')],required=False,initial='')
    idroute = forms.ChoiceField(choices=[],required=False,initial='')
    fromchannel = forms.ChoiceField(choices=[],required=False)
    frompartner = forms.ChoiceField(choices=[],required=False)
    topartner = forms.ChoiceField(choices=[],required=False)
    ineditype = forms.ChoiceField(choices=models.EDITYPESLIST,required=False)
    inmessagetype = forms.ChoiceField(choices=[],required=False)
    outeditype = forms.ChoiceField(choices=models.EDITYPESLIST,required=False)
    outmessagetype = forms.ChoiceField(choices=[],required=False)
    infilename = forms.CharField(required=False,label='Filename',max_length=70)
    lastrun = forms.BooleanField(required=False,initial=False)
    def __init__(self, *args, **kwargs):
        super(SelectIncoming, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['inmessagetype'].choices = models.getinmessagetypes()
        self.fields['outmessagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()

class ViewIncoming(View):
    template = 'bots/incoming.html'
    action = '/incoming/'
    statust = forms.IntegerField(required=False,initial='',widget=HIDDENINPUT())
    idroute = forms.CharField(required=False,widget=HIDDENINPUT())
    fromchannel = forms.CharField(required=False,widget=HIDDENINPUT())
    frompartner = forms.CharField(required=False,widget=HIDDENINPUT())
    topartner = forms.CharField(required=False,widget=HIDDENINPUT())
    ineditype = forms.CharField(required=False,widget=HIDDENINPUT())
    inmessagetype = forms.CharField(required=False,widget=HIDDENINPUT())
    outeditype = forms.CharField(required=False,widget=HIDDENINPUT())
    outmessagetype = forms.CharField(required=False,widget=HIDDENINPUT())
    infilename = forms.CharField(required=False,widget=HIDDENINPUT(),max_length=256)
    lastrun = forms.BooleanField(required=False,initial=False,widget=HIDDENINPUT())

class SelectDocument(Select):
    template = 'bots/selectform.html'
    action = '/document/'
    status = forms.TypedChoiceField(choices=[(0,'---------'),(320,'Document-in'),(330,'Document-out')],required=False,initial=0,coerce=int)
    idroute = forms.ChoiceField(choices=[],required=False,initial='')
    frompartner = forms.ChoiceField(choices=[],required=False)
    topartner = forms.ChoiceField(choices=[],required=False)
    editype = forms.ChoiceField(choices=models.EDITYPESLIST,required=False)
    messagetype = forms.ChoiceField(required=False)
    lastrun = forms.BooleanField(required=False,initial=False)
    reference = forms.CharField(required=False,label='Reference',max_length=70)
    def __init__(self, *args, **kwargs):
        super(SelectDocument, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()

class ViewDocument(View):
    template = 'bots/document.html'
    action = '/document/'
    status = forms.IntegerField(required=False,initial=0,widget=HIDDENINPUT())
    idroute = forms.CharField(required=False,widget=HIDDENINPUT())
    frompartner = forms.CharField(required=False,widget=HIDDENINPUT())
    topartner = forms.CharField(required=False,widget=HIDDENINPUT())
    editype = forms.CharField(required=False,widget=HIDDENINPUT())
    messagetype = forms.CharField(required=False,widget=HIDDENINPUT())
    lastrun = forms.BooleanField(required=False,initial=False,widget=HIDDENINPUT())
    reference = forms.CharField(required=False,widget=HIDDENINPUT())

class SelectOutgoing(Select):
    template = 'bots/selectform.html'
    action = '/outgoing/'
    statust = forms.ChoiceField(choices=[models.DEFAULT_ENTRY,('1','Error'),('3','Done'),('4','Resend')],required=False,initial='')
    idroute = forms.ChoiceField(choices=[],required=False,initial='')
    tochannel = forms.ChoiceField(choices=[],required=False)
    frompartner = forms.ChoiceField(choices=[],required=False)
    topartner = forms.ChoiceField(choices=[],required=False)
    editype = forms.ChoiceField(choices=models.EDITYPESLIST,required=False)
    messagetype = forms.ChoiceField(required=False)
    filename = forms.CharField(required=False,label='Filename',max_length=256)
    lastrun = forms.BooleanField(required=False,initial=False)
    def __init__(self, *args, **kwargs):
        super(SelectOutgoing, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getoutmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['tochannel'].choices = models.gettochannels()

class ViewOutgoing(View):
    template = 'bots/outgoing.html'
    action = '/outgoing/'
    statust = forms.IntegerField(required=False,initial='',widget=HIDDENINPUT())
    idroute = forms.CharField(required=False,widget=HIDDENINPUT())
    tochannel = forms.CharField(required=False,widget=HIDDENINPUT())
    frompartner = forms.CharField(required=False,widget=HIDDENINPUT())
    topartner = forms.CharField(required=False,widget=HIDDENINPUT())
    editype = forms.CharField(required=False,widget=HIDDENINPUT())
    messagetype = forms.CharField(required=False,widget=HIDDENINPUT())
    filename = forms.CharField(required=False,widget=HIDDENINPUT())
    lastrun = forms.BooleanField(required=False,initial=False,widget=HIDDENINPUT())

class SelectProcess(Select):
    template = 'bots/selectform.html'
    action = '/process/'
    idroute = forms.ChoiceField(choices=[],required=False,initial='')
    lastrun = forms.BooleanField(required=False,initial=False)
    def __init__(self, *args, **kwargs):
        super(SelectProcess, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()

class ViewProcess(View):
    template = 'bots/process.html'
    action = '/process/'
    idroute = forms.CharField(required=False,widget=HIDDENINPUT())
    lastrun = forms.BooleanField(required=False,initial=False,widget=HIDDENINPUT())

class SelectConfirm(Select):
    template = 'bots/selectform.html'
    action = '/confirm/'
    confirmtype = forms.ChoiceField(choices=models.CONFIRMTYPELIST,required=False,initial='0')
    confirmed = forms.ChoiceField(choices=[('0','All runs'),('1','Current run'),('2','Last run')],required=False,initial='0')
    idroute = forms.ChoiceField(choices=[],required=False,initial='')
    editype = forms.ChoiceField(choices=models.EDITYPESLIST,required=False)
    messagetype = forms.ChoiceField(choices=[],required=False)
    frompartner = forms.ChoiceField(choices=[],required=False)
    topartner = forms.ChoiceField(choices=[],required=False)
    fromchannel = forms.ChoiceField(choices=[],required=False)
    tochannel = forms.ChoiceField(choices=[],required=False)
    def __init__(self, *args, **kwargs):
        super(SelectConfirm, self).__init__(*args, **kwargs)
        self.fields['idroute'].choices = models.getroutelist()
        self.fields['messagetype'].choices = models.getallmessagetypes()
        self.fields['frompartner'].choices = models.getpartners()
        self.fields['topartner'].choices = models.getpartners()
        self.fields['fromchannel'].choices = models.getfromchannels()
        self.fields['tochannel'].choices = models.gettochannels()

class ViewConfirm(View):
    template = 'bots/confirm.html'
    action = '/confirm/'
    confirmtype = forms.CharField(required=False,widget=HIDDENINPUT())
    confirmed = forms.CharField(required=False,widget=HIDDENINPUT())
    idroute = forms.CharField(required=False,widget=HIDDENINPUT())
    editype = forms.CharField(required=False,widget=HIDDENINPUT())
    messagetype = forms.CharField(required=False,widget=HIDDENINPUT())
    frompartner = forms.CharField(required=False,widget=HIDDENINPUT())
    topartner = forms.CharField(required=False,widget=HIDDENINPUT())
    fromchannel = forms.CharField(required=False,widget=HIDDENINPUT())
    tochannel = forms.CharField(required=False,widget=HIDDENINPUT())

class UploadFileForm(forms.Form):
    file  = forms.FileField(label='Plugin to read',required=True,widget=forms.widgets.FileInput(attrs={'size':'100'}))

class PlugoutForm(forms.Form):
    databaseconfiguration = forms.BooleanField(required=False,initial=True,label='Database configuration',help_text='Routes, channels, translations, partners, etc. from the database.')
    umlists = forms.BooleanField(required=False,initial=True,label='User code lists',help_text='Your user code data from the database.')
    fileconfiguration = forms.BooleanField(required=False,initial=True,label='Script files',help_text='[bots/usersys] Grammars, mapping scrips, routes scripts, etc.')
    infiles = forms.BooleanField(required=False,initial=True,label='Input files',help_text='[bots/botssys/infile] Example/test edi files.')
    charset = forms.BooleanField(required=False,initial=False,label='Edifact character sets',help_text='[bots/usersys/charsets] Seldom needed, only if changed.')
    databasetransactions = forms.BooleanField(required=False,initial=False,label='Database transactions',help_text='Transaction details of all bots runs from the database. Only for support purposes, on request. May generate a very large plugin!')
    data = forms.BooleanField(required=False,initial=False,label='All transaction files',help_text='[bots/botssys/data] Copies of all incoming, intermediate and outgoing files. Only for support purposes, on request. May generate a very large plugin!')
    logfiles = forms.BooleanField(required=False,initial=False,label='Log files',help_text='[bots/botssys/logging] Log files from engine, webserver etc. Only for support purposes, on request.')
    config = forms.BooleanField(required=False,initial=False,label='Configuration files',help_text='[bots/config] Your customised configuration files. Only for support purposes, on request.')
    database = forms.BooleanField(required=False,initial=False,label='SQLite database',help_text='[bots/botssys/sqlitedb] Entire database file. Only for support purposes, on request.')

class DeleteForm(forms.Form):
    delacceptance = forms.BooleanField(required=False,label='Delete transactions in acceptance testing',initial=True,help_text='Delete runs, reports, incoming, outgoing, data files from acceptance testing.')
    deltransactions = forms.BooleanField(required=False,label='Delete transactions',initial=True,help_text='Delete runs, reports, incoming, outgoing, data files.')
    deloutfile = forms.BooleanField(required=False,label='Delete botssys/outfiles',initial=False,help_text='Delete files in botssys/outfile.')
    delcodelists = forms.BooleanField(required=False,label='Delete user code lists',initial=False,help_text='Delete user code lists.')
    deluserscripts = forms.BooleanField(required=False,label='Delete all user scripts',initial=False,help_text='Delete all scripts in usersys (grammars, mappings etc) except charsets.')
    delinfile = forms.BooleanField(required=False,label='Delete botssys/infiles',initial=False,help_text='Delete files in botssys/infile.')
    delconfiguration = forms.BooleanField(required=False,label='Delete configuration',initial=False,help_text='Delete routes, channels, translations, partners etc.')
    delpersist = forms.BooleanField(required=False,label='Delete persist',initial=False,help_text='Delete the persist information.')

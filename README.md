This is a django mapper using the default Django recommendations
IMPORTANT: This version is Functioning! 10/09/2024

```
python3 -m venv venv
source venv/bin/activate

pip install pip --upgrade
or
python.exe -m pip install --user --upgrade pip

pip install django

cd ..
django-admin startproject mapper
cd mapper
```

# TO START:
```
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```



# OLD:

# DJSUPERVISOR
```
pip install supervisor
pip install watchdog
copy djsupervisor folder
copy supervisor.conf
include djsupervisor in settings.py INSTALLED_APPS
```

# BOTS

```
pip install django-q
pip install django-debug-toolbar
copy bots
copy bots.ini
in urls.py-> import debug_toolbar
in urls.py-> path('__debug__/', include(debug_toolbar.urls)),
in urls.py-> path('bots/', include('bots.urls')),
in settings.py-> 'bots', 'django_q' and 'debug_toolbar' in INSTALLED_APPS
in manage.py -> add bots requireents

in settings.py:
add CUSTOM SETTING
python manage.py createcachetable -> required for CACHE setting

python manage.py makemigrations
python manage.py migrate
```
# import PLUGIN

Import

change:
bots.botsconfig -> bots.utils.botsconfig
bots.botslib -> bots.utils.botslib 
bots.botsglobal -> bots.utils.botsglobal

```
Message(object) Class:
	add2errorlist(self,errortxt)
	checkforerrorlist(self)
	try_to_retrieve_info(self)
	display(lex_records)
	mpathformat(mpath)
	checkmessage(self,node_instance,defmessage,subtranslation=False)
	_checkonemessage(self,node_instance,defmessage,subtranslation)
	_checkifrecordsingrammar(self,node_instance,structure,grammarname)
	_checkiffieldsingrammar(self,node_instance,record_definition)
	_canonicaltree(self,node_instance,structure)
	_canonicalfields(self,node_instance,record_definition)
	_logmessagecontent(self,node_instance)
	_logfieldcontent(noderecord)

	getrecord(self,*mpaths)
	change(self,where,change)
	delete(self,*mpaths)
	get(self,*mpaths)
	getnozero(self,*mpaths)
	getdecimal(self,*mpaths)
	getcount(self)
	getcountoccurrences(self,*mpaths)
	getcountsum(self,*mpaths)
	getloop(self,*mpaths)
	getloop_including_mpath(self,*mpaths)
	put(self,*mpaths,**kwargs)
	putloop(self,*mpaths)
	sort(self,*mpaths)

	Inmessage(message.Message) Class:
		__init__(self,ta_info)
		messagegrammarread(self,typeofgrammarfile)
		initfromfile(self)
		set_syntax_used(self)
		handleconfirm(self,ta_fromfile,routedict,error)
		_formatfield(self,value,field_definition,structure_record,node_instance)
		_parse(self,structure_level,inode)
		_manipulatemessagetype(messagetype,inode)
		_readcontent_edifile(self)
		_sniff(self)
		checkenvelope(self)
		nextmessage(self)
		_canonicaltree(self,node_instance,structure)
		_initmessagefromnode(cls,inode,ta_info,syntax,envelope_content=None)

		fixed(Inmessage) Class:
			_readcontent_edifile(self)
			_lex(self)
			_parsefields(self,lex_record,record_definition)
			_formatfield(self,value,field_definition,structure_record,node_instance)

			idoc(fixed) Class:

		var(Inmessage) Class:
			_lex(self)
			_parsefields(self,lex_record,record_definition)
			separatorcheck(separatorstring)

			csv(var) Class:
				_lex(self)
				set_syntax_used(self)

				excel(csv) Class:
					initfromfile(self)
					read_xls(self,infilename)
					format_excelval(self,book,datatype,value,wanttupledate)
					tupledate_to_isodate(self,tupledate)
					utf8ize(self,l)

			edifact(var) Class:
				_manipulatemessagetype(messagetype,inode)
				_readcontent_edifile(self)
				_sniff(self)
				checkenvelope(self)
				handleconfirm(self,ta_fromfile,routedict,error)
				try_to_retrieve_info(self)
				set_syntax_used(self)

			x12(var) Class:
				_manipulatemessagetype(messagetype,inode)
				_sniff(self)
				checkenvelope(self)
				try_to_retrieve_info(self)
				handleconfirm(self,ta_fromfile,routedict,error)
				set_syntax_used(self)

			tradacoms(var) Class:
				def checkenvelope(self)

		xml(Inmessage) Class:
			initfromfile(self)
			_handle_empty(self,xmlnode)
			_etree2botstree(self,xmlnode)
			_etreenode2botstreenode(self,xmlnode)
			_entitytype(self,xmlchildnode)
			stackinit(self)

			xmlnocheck(xml) Class:
				checkmessage(self,node_instance,defmessage,subtranslation=False)
				_entitytype(self,xmlchildnode)
				stackinit(self)

		json(Inmessage) Class:
			initfromfile(self)
			_getrootid(self)
			_dojsonlist(self,jsonobject,name)
			_dojsonobject(self,jsonobject,name)

			jsonnocheck(json) Class:
				checkmessage(self,node_instance,defmessage,subtranslation=False)
				_getrootid(self)

		db(Inmessage) Class:
			initfromfile(self)
			nextmessage(self)

		raw(Inmessage) Class:
			initfromfile(self)
			nextmessage(self)

	class Outmessage(message.Message):
		def __init__(self,ta_info):
		def messagegrammarread(self,typeofgrammarfile):
		def writeall(self):
		def _initwrite(self):
		def _closewrite(self):
		def _write(self,node_instance):
		def tree2records(self,node_instance):
		def _tree2recordscore(self,node_instance,structure):
		def _tree2recordfields(self,noderecord,structure_record):
		def _formatfield(self,value, field_definition,structure_record,node_instance):
		def _initfield(self,field_definition):
		def record2string(self,lex_records):
		def _getescapechars(self):

		class fixed(Outmessage):
			def _initfield(self,field_definition):

			class idoc(fixed):
				def __init__(self,ta_info):
				def _canonicaltree(self,node_instance,structure):
				def _canonicalfields(self,node_instance,record_definition):

		class var(Outmessage):

			class csv(var):
				def _getescapechars(self):

			class edifact(var):
				def _getescapechars(self):

			class tradacoms(var):
				def _getescapechars(self):
				def writeall(self):

			class x12(var):
				def _getescapechars(self):

		class xml(Outmessage):
			def _write(self,node_instance):
			def envelopewrite(self,node_instance):
			def _xmlcorewrite(self,xmltree,root):
			def _node2xml(self,node_instance):
			def _node2xmlfields(self,noderecord):
			def _initwrite(self):

			class xmlnocheck(xml):
				def _node2xmlfields(self,noderecord):

		class json(Outmessage):
			def _initwrite(self):
			def _write(self,node_instance):
			def _closewrite(self):
			def _node2json(self,node_instance):
			def _canonicaltree(self,node_instance,structure):
			def correct_max_one_occurence(self,node_instance,structure):
			def _canonicalfields(self,node_instance,record_definition):

			class jsonnocheck(json):
				def _initwrite(self):
				def _node2json(self,node_instance):

		class templatehtml(Outmessage):
			class TemplateData(object):
			def __init__(self,ta_info):
			def _write(self,node_instance):
			def writeall(self):

		class db(Outmessage):
			def __init__(self,ta_info):
			def writeall(self):
			
		class raw(Outmessage):
			def __init__(self,ta_info):
			def writeall(self):
```
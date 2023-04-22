from django.shortcuts import render

# Create your views here.
import sys
import os
import time
import shutil
import subprocess
import traceback
import socket
import django
from django.contrib import messages
from bots.utils import forms
from bots import models
from bots.utils import viewlib
from bots.utils import botslib
from bots.utils import pluglib
from bots.utils import botsglobal
from bots.utils import py2html
from bots.utils.botsconfig import *
#from django_q.tasks import async_task, result
import asyncio
from asgiref.sync import sync_to_async

def grammarfiler(request,*kw,**kwargs):

	''' handles bots log file viewer. display/download any file in logging directory.
	'''
	if request.method == 'GET':
		grammarpath = botslib.join('..',botsglobal.ini.get('directories','usersys'),'grammars')
		grammar = 'grammar.py'
		grammardata =  'No file selected'
		for root, dirs, files in os.walk(grammarpath, topdown=False):
			pass
			# for name in files:
			# 	print(os.path.join(root, name))
			# for name in dirs:
			# 	print(os.path.join(root, name))
		if 'grammar' in request.GET:
			grammar = request.GET['grammar']
			grammarpath = request.GET['grammarpath']
			for root, dirs2, files in os.walk(grammarpath, topdown=False):
				if root == grammarpath: 
					for file in files:
						if file == grammar:
							try:
								filename = botslib.join(root, file)
								with open(filename) as f:
										grammardata = f.read()
							except:
								grammardata =  'No such file'
			return django.shortcuts.render(request,'bots/grammarfiler.html',{'grammar':grammar, 'grammardata':grammardata, 'grammardirs':dirs, 'grammarfiles':files,'grammarpath':grammarpath})
		

		if 'action' in request.GET and request.GET['action'] == 'download':
			response = django.http.HttpResponse(content_type='text/log')
			response['Content-Disposition'] = 'attachment; filename=' + grammar
			response.write(grammardata)
			return response
		
		if 'dir' in request.GET:
			directory = request.GET['dir']
			grammarpath = botslib.join(grammarpath, directory)
			grammarfiles = sorted(os.listdir(grammarpath), key=lambda s: s.lower())
			return django.shortcuts.render(request,'bots/grammarfiler.html',{'grammar':grammar, 'grammardata':grammardata, 'grammardirs':dirs, 'grammarfiles':grammarfiles, 'grammarpath':grammarpath})
		else:
			return django.shortcuts.render(request,'bots/grammarfiler.html',{'grammar':grammar, 'grammardata':grammardata, 'grammardirs':dirs, 'grammarfiles':files})

def readgrammar(request,*kw,**kwargs):

	#normal report-query with parameters
	notification = 'Grammar read successfully'
	botsglobal.logger.info(notification)
	messages.add_message(request, messages.INFO, notification)

	return django.shortcuts.redirect('/bots/home/')
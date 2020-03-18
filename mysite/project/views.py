from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth

import pyrebase
import requests
import json

from . import db_specs
#from . import fb_settings

# Create your views here.

def default(request):
	return HttpResponse("Hello, world. You're at the project default.")

def db_test(request, database, searchterm):
	#return HttpResponse("You're looking at db: %s, and searchterm: %s" % (database, searchterm))

	def get_url(db, db_specs):
	    url = db_specs.db_specs[db]['firebaseurl']
	    return url

	def get_tables(db, db_specs):
	    tables = list(db_specs.db_specs[db]['tables'].keys())
	    return tables

	def get_pkeys(db, tables, specs):
	    p_keys = []
	    for table in tables:
	        p_keys.append(db_specs.db_specs[db]['tables'][table]['primarykeys'][0])
	    return p_keys

	#Initialize db metadata
	url = get_url(database, db_specs)
	tables = get_tables(database, db_specs)
	pkeys = get_pkeys(database, tables, db_specs)
	# return HttpResponse("Test url: %s" % (url)) #Working

	keywords = searchterm.lower().split() 
	firebase_output=list() 
	match_rows = dict()  
	for word in keywords:
		try:
			# retrieve search results from the index (multiple observations for each keyword)
			index_matches=requests.get(url+'/index/'+word+'.json').json() 
			for match in index_matches:
				match_table=match['table']
				match_key = db_specs.db_specs[database]['tables'][match_table]['primarykeys'][0]
				match_id=match[match_key]

				path = f'{url}/{match_table}.json?orderBy="{match_key}"&equalTo="{match_id}"'

				response = requests.get(path)
				res = json.loads(response.content)

				if match_table not in match_rows:
					match_rows[match_table] = []

				for val in res.values():
					match_rows[match_table].append(val)

		except TypeError:
			print(f'Keyword "{word}" does not exist in database')
			continue #go to the next keyword

	#return HttpResponse("Test: %s %s %s" % (match_table, match_key, match_id)) #Working 
	return HttpResponse("Test: %s" % (match_rows))
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth

import pyrebase
import requests
import json
from collections import Counter

from . import db_specs
from . import fb_settings

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
				tableindex=tables.index(match['table'])
				obs_prim_key=pkeys[tableindex]

				if match_table not in match_rows:
					match_rows[match_table] = []

				match_id=match[obs_prim_key]
				firebase_queries = fb_settings.db.child(match_table).order_by_child(obs_prim_key).equal_to(match_id).get()
				for firebase_query in firebase_queries:
					firebase_query_key=firebase_query.key()
					path = url+'/'+match_table+'/'+firebase_query_key+'.json'
					#firebase_output.append(requests.get(path).json())
					response = requests.get(path).json()
					match_rows[match_table].append(response)

		except TypeError:
			print(f'Keyword "{word}" does not exist in database')
			continue #go to the next keyword

	return HttpResponse("Test: %s" % (match_rows)) #Working 


# def db_test(request, database, searchterm):
# 	#return HttpResponse("You're looking at db: %s, and searchterm: %s" % (database, searchterm)) #Working
# 	#return HttpResponse("test_json: %s" % firebase_output_json) #Not working
# 	#return HttpResponse("You're looking at db: %s, and searchword: %s" % (db_test, searchword))
# 	#return HttpResponse("You're looking at firebaseurl: %s" % firebaseurl) #Not working
# 	#return render(request, "project/test.html", {'test_json': test_json}) #Not working

# 	# test_dict = {'countrycode': 'aus', 'district': 'new south wales'}
# 	# test_json = json.dumps(test_dict)
# 	# return HttpResponse("test_json: %s" % test_json)

# 	# try:
# 	# 	question = Question.objects.get(pk=question_id)
# 	# except Question.DoesNotExist:
# 	# 	raise Http404("Question does not exist")
# 	# return render(request, 'polls/detail.html', {'question': question})

# 	# question = get_object_or_404(Question, pk=question_id)
# 	# return render(request, 'polls/detail.html', {'question': question})

# 	with open('project/db_specs.json') as json_file:
# 		db_specs = json.load(json_file)

# 	# retrieve the correct url for the user input
# 	firebaseurl=db_specs[database]['firebaseurl']
# 	# Parse multiple words in searchterm into separate keywords
# 	keywords = searchterm.lower().split()

# 	firebase = pyrebase.initialize_app(config)
# 	db=firebase.database()

# 	# use user input to retrieve the correct database/table characteristics
# 	# first, initialize empty lists
# 	tables=list()
# 	columns=list()
# 	prim_keys=list()
# 	frgn_keys=list()
# 	# then fill with the correct specs from the db_specs file
# 	for tbl in db_specs[database]['tables']:
# 	    # retrieve the table names:
# 	    tables.append(tbl)
# 	    # retrieve the column names:
# 	    columns.append(db_specs[database]['tables'][tbl]['columns'])
# 	    # retrieve the primary and foreign keys:
# 	    prim_keys.append(db_specs[database]['tables'][tbl]['primarykeys'])
# 	    frgn_keys.append(db_specs[database]['tables'][tbl]['foreignkeys'])

# 	# REPLACE WITH TABLE IN ALL CAPS ONCE WORLD DATABASE IS RE-UPLOADED FROM MYSQL
# 	if database in ['alumni','kickstarter', 'world']:
# 		#temp_table='TABLE'
# 		temp_table='table'

# 	firebase_output=list()

# 	for word in keywords:
# 		try:
# 			# retrieve search results from the index (multiple observations for each keyword)
# 			responses=requests.get(firebaseurl+'/index/'+word+'.json').json()	
# 			# parse the search results
# 			for response in responses:
# 				response = {k.lower(): v for k, v in response.items()}
# 				#return HttpResponse("response: %s" % response) #Working

# 				# assign the "child" for the firebase query
# 				child=response[temp_table]
# 				# in order to know which primary key to search on, need to know the table
# 				tableindex=tables.index(response[temp_table])
# 				# based on the table, the primary key(s) is(are) assigned
# 				obs_prim_keys=prim_keys[tableindex]
# 				# if there is one primary key: 
# 				if len(obs_prim_keys)==1:
# 					obs_prim_key=obs_prim_keys[0] 
# 					# assign the value of the primary key from the response for the firebase query
# 					#return HttpResponse("obs_prim_key: %s --- response %s" % (obs_prim_key, response)) #Returns 'code'
# 					#return HttpResponse("test: %s" % response) #Returns index tuple with 'Code'

# 					query_val=response[obs_prim_key] #Returns 'swe'
# 					#return HttpResponse("test: %s :: obs_prim_key: %s :: child: %s"% (query_val, obs_prim_key, child))

# 					# search firebase for the entry that contains that query value at the right location
# 					#firebase_queries = db.child(child).order_by_child(obs_prim_key).equal_to(query_val).get() #Fix this
# 					#test = db.child("country").get()
# 					test = requests.get(firebaseurl+'/'+child+'/'+'200'+'.json').json()
# 					return HttpResponse("test: %s" % test)

# 		# if there's no node in the firebase index, catch the error
# 		except TypeError:
# 			#print(f'Keyword "{word}" does not exist in database')
# 			#break #go to the next keyword
# 			continue
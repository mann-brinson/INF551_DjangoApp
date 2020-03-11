from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth

import pyrebase
import requests
import json
from collections import Counter

#from . import db_specs

config = {

'apiKey': "AIzaSyAle83H9wpH_bVHcDHLX2Hhw1ak_8PYhXg",
    'authDomain': "inf551-world-project.firebaseapp.com",
    'databaseURL': "https://inf551-world-project.firebaseio.com",
    'projectId': "inf551-world-project",
    'storageBucket': "inf551-world-project.appspot.com",
    'messagingSenderId': "717516863005",
    'appId': "1:717516863005:web:7d58f28fbdf2f9d93ab8f4"
  }

# Create your views here.

def default(request):
	return HttpResponse("Hello, world. You're at the project default.")

def db_test(request, database, searchterm):
	#return HttpResponse("You're looking at db: %s, and searchterm: %s" % (database, searchterm)) #Working
	#return HttpResponse("test_json: %s" % firebase_output_json) #Not working
	#return HttpResponse("You're looking at db: %s, and searchword: %s" % (db_test, searchword))
	#return HttpResponse("You're looking at firebaseurl: %s" % firebaseurl) #Not working
	#return render(request, "project/test.html", {'test_json': test_json}) #Not working

	# test_dict = {'countrycode': 'aus', 'district': 'new south wales'}
	# test_json = json.dumps(test_dict)
	# return HttpResponse("test_json: %s" % test_json)

	# try:
	# 	question = Question.objects.get(pk=question_id)
	# except Question.DoesNotExist:
	# 	raise Http404("Question does not exist")
	# return render(request, 'polls/detail.html', {'question': question})

	# question = get_object_or_404(Question, pk=question_id)
	# return render(request, 'polls/detail.html', {'question': question})

	with open('project/db_specs.json') as json_file:
		db_specs = json.load(json_file)

	# retrieve the correct url for the user input
	firebaseurl=db_specs[database]['firebaseurl']
	# Parse multiple words in searchterm into separate keywords
	keywords = searchterm.lower().split()

	firebase = pyrebase.initialize_app(config)
	db=firebase.database()

	# use user input to retrieve the correct database/table characteristics
	# first, initialize empty lists
	tables=list()
	columns=list()
	prim_keys=list()
	frgn_keys=list()
	# then fill with the correct specs from the db_specs file
	for tbl in db_specs[database]['tables']:
	    # retrieve the table names:
	    tables.append(tbl)
	    # retrieve the column names:
	    columns.append(db_specs[database]['tables'][tbl]['columns'])
	    # retrieve the primary and foreign keys:
	    prim_keys.append(db_specs[database]['tables'][tbl]['primarykeys'])
	    frgn_keys.append(db_specs[database]['tables'][tbl]['foreignkeys'])

	# REPLACE WITH TABLE IN ALL CAPS ONCE WORLD DATABASE IS RE-UPLOADED FROM MYSQL
	if database in ['alumni','kickstarter', 'world']:
		#temp_table='TABLE'
		temp_table='table'

	firebase_output=list()

	for word in keywords:
		try:
			# retrieve search results from the index (multiple observations for each keyword)
			responses=requests.get(firebaseurl+'/index/'+word+'.json').json()	
			# parse the search results
			for response in responses:
				response = {k.lower(): v for k, v in response.items()}
				#return HttpResponse("response: %s" % response) #Working

				# assign the "child" for the firebase query
				child=response[temp_table]
				# in order to know which primary key to search on, need to know the table
				tableindex=tables.index(response[temp_table])
				# based on the table, the primary key(s) is(are) assigned
				obs_prim_keys=prim_keys[tableindex]
				# if there is one primary key: 
				if len(obs_prim_keys)==1:
					obs_prim_key=obs_prim_keys[0] 
					# assign the value of the primary key from the response for the firebase query
					return HttpResponse("obs_prim_key: %s --- response %s" % (obs_prim_key, response)) #Returns 'code'
					#return HttpResponse("test: %s" % response) #Returns index tuple with 'Code'

					# query_val=response[obs_prim_key] #Returns 'swe'
					# #return HttpResponse("test: %s" % query_val)

					# # search firebase for the entry that contains that query value at the right location
					# firebase_queries = db.child(child).order_by_child(obs_prim_key).equal_to(query_val).get()
					# #return HttpResponse("test: %s" % firebase_queries)
					# # the queries are returned as pyrebase objects for which you can retrieve keys
					# for firebase_query in firebase_queries:
					# 	# the key then functions as a node in the final retrieval of the original entry in firebase
					# 	firebase_query_id=firebase_query.key()
					# 	return HttpResponse("test: %s" % firebase_query_id) #Test
						#firebase_output.append(requests.get(firebaseurl+'/'+child+'/'+firebase_query_id+'.json').json())
					#return HttpResponse("test: %s" % firebase_output[0]) #Test

				# # if there are two primary keys for a given table
				# if len(obs_prim_keys)==2:
				# 	# assign the first primary key and value
				# 	obs_prim_key1=obs_prim_keys[0] 
				# 	query_val1=response[obs_prim_key1]
				# 	# assign the second primary key and value
				# 	obs_prim_key2=obs_prim_keys[1] 
				# 	query_val2=response[obs_prim_key2]	
				# 	# search firebase for the entries that contains that query value at the right location
				# 	# there could be multiple at this time.
				# 	firebase_queries = db.child(child).order_by_child(obs_prim_key1).equal_to(query_val1).get()		 
				# 	for firebase_query in firebase_queries:
				# 		firebase_query_id=firebase_query.key()
				# 		# NEED TO ADD SECTION TO PULL OUT THE RIGHT OBSERVATIONS THAT ALSO MATCH 
				# 		# ON THE SECOND PRIMARY KEY FOR THE WORLD (COUNTRYLANGUAGE) DATABASE. 
				# 		# FIRST THIS NEED TO BE ADDED TO FIREBASE IN ORDER TO TEST 
				# 		firebase_output.append(requests.get(firebaseurl+'/'+child+'/'+firebase_query_id+'.json').json())

		# if there's no node in the firebase index, catch the error
		except TypeError:
			#print(f'Keyword "{word}" does not exist in database')
			#break #go to the next keyword
			continue

	#return HttpResponse("test_json: %s" % db_specs)


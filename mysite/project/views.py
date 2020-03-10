from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth

import pyrebase
import requests
import json
from collections import Counter

config = {

'apiKey': "AIzaSyAle83H9wpH_bVHcDHLX2Hhw1ak_8PYhXg",
    'authDomain': "inf551-world-project.firebaseapp.com",
    'databaseURL': "https://inf551-world-project.firebaseio.com",
    'projectId': "inf551-world-project",
    'storageBucket': "inf551-world-project.appspot.com",
    'messagingSenderId': "717516863005",
    'appId': "1:717516863005:web:7d58f28fbdf2f9d93ab8f4"
  }

firebase = pyrebase.initialize_app(config)

authe = firebase.auth()
database=firebase.database()

# Create your views here.

def default(request):
	return HttpResponse("Hello, world. You're at the project default.")

def db_test(request, db_test, searchword):
	return HttpResponse("You're looking at db: %s, and searchword: %s" % (db_test, searchword))

	# try:
	# 	question = Question.objects.get(pk=question_id)
	# except Question.DoesNotExist:
	# 	raise Http404("Question does not exist")
	# return render(request, 'polls/detail.html', {'question': question})

	# question = get_object_or_404(Question, pk=question_id)
	# return render(request, 'polls/detail.html', {'question': question})
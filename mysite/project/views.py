from django.shortcuts import render
import pyrebase
from django.contrib import auth

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

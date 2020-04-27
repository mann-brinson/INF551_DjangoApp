from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
from django.template import Context, RequestContext
from django.conf import settings #to load google_auth credentials
from . import db_specs # database specifications (table names, primary keys etc.)
from .forms import SearchForm

import os #to load google_auth credentials
import json
import ast # to convert dictionaries as strings back to dictionaries
import re # regular expressions, to find whole words

from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# Define the required scopes
scopes = ["https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/firebase.database"]


def search(request):
    # If the form has been submitted...
    if request.method == 'POST': 
        form = SearchForm(request.POST or None) # A form bound to the POST data
        form_data = request.POST.copy()
        form_db = form_data['database']
        form_searchterm = form_data['searchterm']

        # Authenticate a credential with the service account
        if form_db == 'world':
            creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/world.json' )
        elif form_db == 'kickstarter':
            creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/kickstarter.json' )
        elif form_db == 'alumni':
            creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/alumni.json' )
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=scopes)
        # Use the credentials object to authenticate a Requests session.
        authed_session = AuthorizedSession(credentials)

        # context gets passed to the html template
        context = {'form': form, 'form_db': form_db}

        #Initialize database metadata
        url = get_url(form_db)
        tables = get_tables(form_db)
        fkeys, fk_pk = get_fkeys(form_db)

        # parse the keywords from the search form
        keywords = form_searchterm.lower().split(' ')
        orig_searchterm_whole="'"+form_searchterm+"'"
        orig_searchterm_partial=form_searchterm.lower()
        form_searchterm_for_link=form_searchterm.replace(" ","+")

        # searchterm (with + between separate words) gets passed to html template - this is needed for url of click-trhough links
        context.update({'form_searchterm': form_searchterm_for_link})
        
        # create a list that holds rows of the tables (as dicts) that match on one or more keywords
        match_rows = list()  
        # create error catching sets
        word_success=list()
        keyword_failure=list()
        # create object that holds the total size of the requests
        size_bytes=0
        size_kb=0
        size_mb=0
        for word in keywords:   
            try:
                # retrieve search results from the firebase index (multiple observations for each keyword)
                search_response=authed_session.get(url+'/index/'+word+'.json')
                # add the data communication overhead
                size_bytes+=len(search_response.content)
                # get search results in json format
                index_matches=search_response.json() 
                 # parse the search results
                for match in index_matches:
                    # assign the original table name
                    match_table=match['table']
                    # assign the original primary key
                    match_key = db_specs.db_specs[form_db]['tables'][match_table]['primarykeys'][0]                
                    match_id=match[match_key]
                    # firebase request based on the table, primary key and the value
                    path = f'{url}/{match_table}.json?orderBy="{match_key}"&equalTo="{match_id}"'
                    table_response = authed_session.get(path)
                    res = json.loads(table_response.content)
                    # add the matched rows to the match_rows list (list of dicts)
                    for val in res.values():
                        match_rows.append(val)
                    # if successful
                    word_success.append(word)
                    # calculate the overhead for each of the requests
                    size_bytes+=len(table_response.content)
            except TypeError:
                # catch error when none of the keywords are in the database, and render straight away 
                if keywords.index(word)==len(keywords)-1 and len(word_success)==0:
                    context.update({'none_found':orig_searchterm_whole})
                    return render(request, 'project/search.html', context)
            # add words that were no match to the keyword_failure list for error reporting         
            if word not in word_success:
                keyword_failure.append(word)
        # convert bytes to KB or MB if larger than 1 thousand or 1 million
        if size_bytes>1000:
            size_kb=round(size_bytes/1000,1)
            size_bytes=0
        if size_bytes>1000000:
            size_mb=round(size_bytes/1000000,1)
            size_bytes=0
        # if there's a results that got added for multiple keywords, they'll occur twice in the output
        # the following section counts how many of the same results there are, 
        # and orders them by their frequency (highest first), and the how well the search terms match. 
        # Since the output is in a list of dictionaries, 
        # a few back and forth conversions are necessary (dict->str->dict) 
        # only reorder the output if there is more than one entry and more than one keyword    
        ordered_output=list()
        count_output=dict()
        for row in match_rows:
            # iterate over the results, and count when they occur more than once 
            # (meaning that they had a match with multiple keywords). This creates a dictionary 
            # with the original dictionaries as keys (as a string representation) and the counter as the value
            if str(row) not in count_output:
                count_output[str(row)]=1
            else:
                count_output[str(row)]+=1
        # then pick out the results that were found most often first 
        # starting with the max nr of original keywords and counting backwards
        # first, create a holding list for non-exact matches to be added after the exact matches
        holding_list=list()           
        try:
            for i in range(max(count_output.values()), 0, -1):
                # these three lines are processing the output from the prior iteration
                for held_item in holding_list:
                    ordered_output.append(ast.literal_eval(held_item))
                holding_list.clear()
                for output, count in count_output.items():
                    if count==i:                
                        # prioritize exact matches in the values (e.g. 'United States' as the value)
                        if orig_searchterm_whole in output.lower():
                            # using ast.literal_eval to safely convert back to dict from string
                            ordered_output.append(ast.literal_eval(output))
                        # then use the holding_list, but add at the front if it's an exact match,
                        # but not standalone (e.g. 'United States Minor Islands')
                        elif orig_searchterm_partial in output.lower(): 
                            holding_list.insert(0,output)
                        # last priority is the partial match (e.g. United Kingdom)
                        else:
                            holding_list.append(output)
        # catch unlikely error where multiple keywords are all not found and they're the same (eg "blah blah")
        except ValueError:
            context.update({'none_found':orig_searchterm_whole})
            return render(request, 'project/search.html', context)
        # clear out any remaining items in the holding list from the last iteration
        for held_item in holding_list:
            ordered_output.append(ast.literal_eval(held_item))    
        # add the output and keys to the context to display
        context.update({'results':ordered_output, 'foreign_keys':fkeys, 'fk_pk':fk_pk})
        # if some of the keywords were not found, they'll be reported in addition to the output
        if keyword_failure:
            context.update({'some_not_found':keyword_failure})
        # also report on the size of the request
        if size_bytes>0:
            context.update({'size_bytes':size_bytes})           
        if size_kb>0:
            context.update({'size_kb':size_kb})
        if size_mb>0:
            context.update({'size_mb':size_mb})
        # return everything and pass to html template
        return render(request, 'project/search.html', context)
    # otherwise (if forms has not been submitted), just display the form itself
    else: 
        form = SearchForm(request.POST or None)
        if form.is_valid():
            form.save()
        context = {
            'form': form,
        }
        return render(request, "project/search.html", context)


def fk_link(request, link_search):
    size_bytes=0
    database, fkey, match_id=link_search.split('&')
    url = get_url(database)
    fkeys, fk_pk = get_fkeys(database)
    pkeys=get_pkeys(database)
    tables=get_tables(database)
    match_key=fk_pk[fkey]
    match_table=tables[pkeys.index(match_key)]

    # Authenticate a credential with the service account
    if database == 'world':
        creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/world.json' )
    elif database == 'kickstarter':
        creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/kickstarter.json' )
    elif database == 'alumni':
        creds_file =os.path.join( settings.BASE_DIR, 'project/firebase_creds/alumni.json' )
    credentials = service_account.Credentials.from_service_account_file(
        creds_file, scopes=scopes)
    # Use the credentials object to authenticate a Requests session.
    authed_session = AuthorizedSession(credentials)

    # firebase request based on the table, primary key and the value
    path = f'{url}/{match_table}.json?orderBy="{match_key}"&equalTo="{match_id}"'
    table_response = authed_session.get(path)
    res = json.loads(table_response.content)
    size_bytes+=len(table_response.content)
    # add the matched rows to the match_rows list (list of dicts)
    match_rows=list()
    for val in res.values():
        match_rows.append(val)
    context = {'link': match_rows, 'foreign_keys':fkeys, 'database':database, 'current_fkey':fkey, 'clicked_link':match_id}
    if size_bytes>0:
        context.update({'size_bytes':size_bytes}) 
    return render(request, 'project/link.html', context)

def default(request):
    return HttpResponse("Hello, world. You're at the project default.")

# several functions to retrieve basic info about the databases (from db_specs file)
# the firebase url where the data are stored
def get_url(db):
    url = db_specs.db_specs[db]['firebaseurl']
    return url
# name of the tables of the database
def get_tables(db):    
    tables = list(db_specs.db_specs[db]['tables'].keys())
    return tables
# primary keys of all of the tables
def get_pkeys(db):
    p_keys = []
    tables=get_tables(db)
    for table in tables:
        p_keys.append(db_specs.db_specs[db]['tables'][table]['primarykeys'][0])
    return p_keys
# foreign keys of all of the tables (fkeys), and a foreign key to primary key mapping (fk_pk)
def get_fkeys(db):
    tables=get_tables(db)
    fk_pk = dict() 
    for table in tables:
        fk_pk.update(db_specs.db_specs[db]['tables'][table]['fk_pk'])
    fkeys=list()
    for fkey in fk_pk:
        fkeys.append(fkey)
    return fkeys, fk_pk
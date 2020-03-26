from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import auth
from . import db_specs # database specifications (table names, primary keys etc.)
from .forms import SearchForm

import pyrebase
import requests
import json
import ast # to convert dictionaries as strings back to dictionaries
import re # regular expressions, to find whole words

# Create your views here.

def selectdb(request):
    form = SearchForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = SearchForm()
    context = {
        'form': form
    }
    return render(request, "project/selectdb.html", context)

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

    #Initialize database metadata
    url = get_url(database, db_specs)
    tables = get_tables(database, db_specs)
    pkeys = get_pkeys(database, tables, db_specs)

    # parse the keywords from the input. Separate words are indicated with + in the url
    keywords = searchterm.lower().split('+')
    orig_searchterm_whole="'"+searchterm.lower().replace('+',' ')+"'"
    orig_searchterm_partial=searchterm.lower().replace('+',' ')

    # create a list that holds rows of the tables (as dicts) that match on one or more keywords
    match_rows = list()  
    keyword_failure=True
    keyword_failure_warning=list()

    for word in keywords:   
        try:
            # retrieve search results from the firebase index (multiple observations for each keyword)
            index_matches=requests.get(url+'/index/'+word+'.json').json() 
             # parse the search results
            for match in index_matches:
                # assign the original table name
                match_table=match['table']
                # assign the original primary key
                match_key = db_specs.db_specs[database]['tables'][match_table]['primarykeys'][0]                
                match_id=match[match_key]

                # firebase request based on the table, primary key and the value
                path = f'{url}/{match_table}.json?orderBy="{match_key}"&equalTo="{match_id}"'

                response = requests.get(path)
                res = json.loads(response.content)
    
                # add the matched rows to the match_rows list (list of dicts)
                for val in res.values():
                    match_rows.append(val)

                keyword_failure=False
    
        except TypeError:
            # create a warning if some of the keywords were not found (but don't abort)
            keyword_failure_warning.append("Not found in database: "+word)
            # catch error when there are multiple keywords, and they're all not in database: 
            if keywords.index(word)==len(keywords)-1 & keyword_failure==True:
                return HttpResponse("Not found in database: %s" % (orig_searchterm_whole))
            # iterate over other keywords to see if they're valid
            else:
                continue

    # if there's a results that got added for multiple keywords, they'll occur twice in the output
    # the following section counts how many of the same results there are, 
    # and orders them by their frequency (highest first), and the how well the search terms match. 
    # Since they output is in a list of dictionaries, 
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
    # first, create a holding list for non-exact matches
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
    # catch error when there is only one keyword, and it's not in the database
    except ValueError:
        return HttpResponse("Not found in database: %s" % (orig_searchterm_whole))

    # clear out any remaining items in the holding list from the last iteration
    for held_item in holding_list:
        ordered_output.append(ast.literal_eval(held_item))    


    if len(keyword_failure_warning)>0:
        return HttpResponse("%s %s" % (ordered_output, keyword_failure_warning))
    else:
        return HttpResponse("%s" % (ordered_output))
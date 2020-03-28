
# this file specifies all the databases in the search engine, and their characteristics such as column names, 
# primary and foreign keys, and the firebase urls where they're stored

# main dictionary that holds all the databases
db_specs=dict()

####### first database is the world database ########
world=dict()

# which has 3 tables:
country=dict()
columns=['code','name','continent','region','surfacearea','indepyear','population','lifeExpectancy','gnp','gnpold','localname','governmentForm','headofstate','capital','code2']
primarykeys=['code']
fk_pk={'':''}
country['columns']=columns
country['primarykeys']=primarykeys
country['fk_pk']=fk_pk

city=dict()
columns=['id','name','countrycode','district','population']
primarykeys=['id']
fk_pk={'countrycode':'code'}
city['columns']=columns
city['primarykeys']=primarykeys
city['fk_pk']=fk_pk

countrylanguage=dict()
columns=['id','countrycode','language','isofficial','percentage']
primarykeys=['id']
fk_pk={'countrycode':'code'}
countrylanguage['columns']=columns
countrylanguage['primarykeys']=primarykeys
countrylanguage['fk_pk']=fk_pk

# combine the three tables, and add to the world dictionary
tables=dict()
tables['country']=country
tables['city']=city
tables['countrylanguage']=countrylanguage
world['tables']=tables

# and lastly, add the firebase url
world['firebaseurl']='https://inf551-world-project.firebaseio.com'


####### second database is the kickstarter database ########
kickstarter=dict()

# which has 3 tables:
project=dict()
columns=['project_id','creator_id','location_id','state','country','name','pledged','goal','category_id','blurb','backers_count',]
primarykeys=['project_id']
fk_pk={'creator_id':'creator_id'}
project['columns']=columns
project['primarykeys']=primarykeys
project['fk_pk']=fk_pk

creator=dict()
columns=['creator_id','name','slug']
primarykeys=['creator_id']
fk_pk={'':''}
creator['columns']=columns
creator['primarykeys']=primarykeys
creator['fk_pk']=fk_pk

comments=dict()
columns=['comment_id','user_name','project_id','body']
primarykeys=['comment_id']
fk_pk={'projectid':'project_id'}
comments['columns']=columns
comments['primarykeys']=primarykeys
comments['fk_pk']=fk_pk

# combine the three tables, and add to the kickstarter dictionary
tables=dict()
tables['project']=project
tables['creator']=creator
tables['comments']=comments
kickstarter['tables']=tables

# and lastly, add the firebase url
kickstarter['firebaseurl']='https://inf551kickstarter.firebaseio.com'


####### third database is the alumni database ########
alumni=dict()

# which has 3 tables:
person=dict()
columns=['person_id','first_name','last_name','last_name_new','gender','usc_email','preferred_email','lab_id','graduated','current_student','start_year','graduation_year']
primarykeys=['person_id']
fk_pk={'lab_id':'lab_id'}
person['columns']=columns
person['primarykeys']=primarykeys
person['fk_pk']=fk_pk

work=dict()
columns=['work_id','person_id','company','job_title','start_year','end_year','job_seq']
primarykeys=['work_id']
fk_pk={'person_id':'person_id'}
work['columns']=columns
work['primarykeys']=primarykeys
work['fk_pk']=fk_pk

lab=dict()
columns=['lab_id','neuroscience_lab','neuroscience_field']
primarykeys=['lab_id']
fk_pk={'':''}
lab['columns']=columns
lab['primarykeys']=primarykeys
lab['fk_pk']=fk_pk

# combine the three tables, and add to the alumni dictionary
tables=dict()
tables['person']=person
tables['work']=work
tables['lab']=lab
alumni['tables']=tables

# and lastly, add the firebase url
alumni['firebaseurl']='https://inf551alumni.firebaseio.com'


db_specs['world']=world
db_specs['kickstarter']=kickstarter
db_specs['alumni']=alumni


# # how to retrieve items from the database dictionary
# tables=list()
# columns=list()
# prim_keys=list()
# frgn_keys=list()
# # retrieve specs from the db_specs file
# for tbl in db_specs[database]['tables']:
#     # retrieve the table names:
#     tables.append(tbl)
#     # retrieve the column names:
#     columns.append(db_specs[database]['tables'][tbl]['columns'])
#     # retrieve the primary and foreign keys:
#     prim_keys.append(db_specs[database]['tables'][tbl]['primarykeys'])
#     frgn_keys.append(db_specs[database]['tables'][tbl]['fk_pk'])



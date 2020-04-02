from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    path('', views.default, name='default'),

    path('selectdb/', views.selectdb, name='selectdb'),

    # ex: /project/sweden/
    #path('<str:database>/', views.db_search, name='database'),

    #ex: /project/world/sweden
    #path('<str:database>/<str:searchterm>/', views.db_search, name='searchterm'),

    #ex: /project/world/sweden/1
    path('<str:database>/<str:searchterm>/<str:fk_value>/', views.fk_link, name='fk_value'),
]
from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    path('', views.default, name='default'),

    path('search/', views.search, name='search'),

    path('<str:link_search>/', views.fk_link, name='link_search'),
]
from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'project'
urlpatterns = [
    path('', views.default, name='default'),

    # ex: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),

    # ex: /polls/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),

    # ex: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),


    path('selectdb/', views.selectdb, name='selectdb'),

    # ex: /project/sweden/
    path('<str:database>/', views.db_test, name='database'),

    #ex: /project/world/sweden
    path('<str:database>/<str:searchterm>/', views.db_test, name='searchterm'),

    path('<str:database>/<str:searchterm>/<str:fk_value>/', views.fk_link, name='fk_value'),

    #url(r'<str:database>/<str:searchterm>/<int:fk_link>/', views.fk_link, name='fk_link'),

]
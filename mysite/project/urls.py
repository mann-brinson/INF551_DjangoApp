from django.urls import path

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

    # ex: /project/sweden/
    path('<str:searchword>/', views.detail, name='detail'),


]
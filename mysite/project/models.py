from django.db import models

# Create your models here.
class SearchForm_m(models.Model):
    database   = models.CharField(max_length=120) # max_length = required
    searchterm = models.CharField(max_length=120) # max_length = required
from django import forms

from .models import SearchForm_m

class SearchForm(forms.ModelForm):
	database = forms.CharField(label='', 
				widget=forms.TextInput(attrs={"placeholder": "Put database here"}))
	searchterm = forms.CharField(label='', 
				widget=forms.TextInput(attrs={"placeholder": "Put searchterm here"}))
	class Meta:
		model = SearchForm_m
		fields = [
			'database',
			'searchterm'
		]
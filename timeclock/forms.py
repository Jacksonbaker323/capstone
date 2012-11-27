from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
import datetime
from django.forms.fields import *
from django.forms.widgets import *
from django.forms.extras.widgets import *

class UpdateTimeForm(forms.Form):
	#StartDate = forms.DateField(initial=datetime.datetime.date.today)
	#EndDate = forms.DateField(initial=datetime.datetime.date.today)
	#StartTime = forms.TimeField()
	#EndTime = forms.TimeField()
	Deliverables = forms.CharField()
	#TestTime = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
	StartDate = forms.DateField(widget=DateTimeInput)
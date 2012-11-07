from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from timeclock.models import Semester, Project, Student, Shift, Deliverable

def index(request):
		semester_list = Semester.objects.all()
		context = {'semester_list' : semester_list }
		return render(request, 'timeclock/index.html', context)

def project(request, semester_name):
		project_list = Project.objects.all()
		context = {'project_list' : project_list }
		return render(request, 'timeclock/project.html', context)


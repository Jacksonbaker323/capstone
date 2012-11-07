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
		project_list = Project.objects.filter(semester=semester_name)
		context = { 'project_list' : project_list }
		return render(request, 'timeclock/project.html', context)

def student(request, project_name):
	student_list = Student.objects.filter(project=project_name)
	context = { 'student_list' : student_list }
	return render(request, 'timeclock/student.html', context)

def entertime(request, student_id):
	student = Student.objects.filter(pk=student_id)
	context = { 'student' : student }
	return render(request, 'timeclock/entertime.html', context)
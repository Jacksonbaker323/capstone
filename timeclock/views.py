from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from timeclock.models import Semester, Project, Student, Shift, Deliverable
from django.utils import timezone
from django.utils import tzinfo
import datetime


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
	deliverables = Deliverable.objects.all()
	context = { 'student' : student, 'deliverables' :deliverables, 'student_id' : student_id }
	return render(request, 'timeclock/entertime.html', context)


def submittime(request):
	

##### STARTDATE DATETIME OBJECT 


	#Check for the startdate to be not empty
	if request.GET['startdate'] == "":
		context = {'error' : "Please enter a start date" }
		return render(request, 'timeclock/error.html', context)
	else:
		#if startdate has text in it convert it to a date object
		startdate = request.GET['startdate']

	if request.GET['starttime'] == "":
		context = {'error' :"Please enter a start time"}
		return render(request, 'timeclock/error.html', context)
	else: 
		#Build the time_start object to put in the database
		starttime = request.GET['starttime']
		start_string = startdate + " " + starttime
		submitted_time_start = datetime.datetime.strptime(start_string, '%m/%d/%Y %I:%M %p')
		submitted_time_start = timezone.make_aware(submitted_time_start, timezone.get_default_timezone())
##### ENDDATE DATETIME OBJECT 
		#Check for the enddate to be not empty
	if request.GET['enddate'] == "":
		context = {'error' : "Please enter a end date" }
		return render(request, 'timeclock/error.html', context)
	else:
		#if enddate has text in it convert it to a date object
		enddate = request.GET['enddate']

	if request.GET['endtime'] == "":
		context = {'error' :"Please enter a end time"}
		return render(request, 'timeclock/error.html', context)
	else: 
		#Build the time_start object to put in the database
		endtime = request.GET['endtime']
		end_string = enddate + " " + endtime
		submitted_time_end = datetime.datetime.strptime(end_string, '%m/%d/%Y %I:%M %p')
		submitted_time_end = timezone.make_aware(submitted_time_end, timezone.get_default_timezone())
		submitted_total_time = submitted_time_end - submitted_time_start
		submitted_total_time = float(submitted_total_time.total_seconds()/3600)


	submitted_deliverables = request.GET['deliverables']
	student_id = request.GET['student_id']
	student_id_number = Student.objects.get(id=student_id)

	newshift = Shift(shift_student=student_id_number, time_start=submitted_time_start, time_end=submitted_time_end, total_time=submitted_total_time,  deliverables=submitted_deliverables)
	newshift.save()
	context = {'student_id':student_id}
	return render(request, 'timeclock/success.html', context)



def reporting(request, semester_id):
	end_date = datetime.date.today()
	start_date = end_date - datetime.timedelta(days=7)
	
	semester = Semester.objects.filter(id=semester_id)
	students = Student.objects.filter(semester=semester).order_by("project")


	shifts = Shift.objects.filter(time_start__gt=start_date)




	



	#Get the number of projects in a semester
	#Get the name of the project by id and then students in that project
	#Put that info in an array
	#Iterate through it in the HTML template


	context = {'students': students, 'start_date': start_date, 'end_date': end_date, 'shifts' : shifts}
	return render(request, 'timeclock/report.html', context)



from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from timeclock.models import Semester, Project, Student, Shift, Deliverable, ProjectStat
from django.utils import timezone
from django.utils import tzinfo
import datetime
from django.db.models import Avg, Count, Sum
import string
from django.shortcuts import redirect

def index(request):
		semester_list = Semester.objects.all()
		if request.session.get('semester_id', None):
			return redirect('/semester/' + request.session['semester_id']) #redirect the user to the appropriate semester page
		#var 	=  'name in html file' : variable } #see below to add more variables to html
		context = {'semester_list' : semester_list, 'test' : 'hello whatever! Maybe this works?', 'page' : 'index'}
		return render(request, 'timeclock/index.html', context)
		
def project(request, semester_name):
		semesterid = request.path.split("/")[2]
		request.session['semester_id'] = semesterid
		project_list = Project.objects.filter(semester=semester_name).order_by('project_name')
		semestername = Semester.objects.filter(id=semester_name)
		context = { 'project_list' : project_list, 'semester_name' : semestername[0].semester_name }
		return render(request, 'timeclock/project.html', context)

def student(request, project_name):
	student_list = Student.objects.filter(project=project_name).order_by('student_name')
	context = { 'student_list' : student_list }
	return render(request, 'timeclock/student.html', context)

def entertime(request, student_id):
	student = Student.objects.filter(pk=student_id)
	deliverables = Deliverable.objects.all()
	context = { 'student' : student, 'deliverables' :deliverables, 'student_id' : student_id }
	return render(request, 'timeclock/entertime.html', context)

def reportingindex(request):
	semester_list = Semester.objects.all()
	context = {'semester_list' : semester_list, 'page' : 'report'}
	return render(request, 'timeclock/reportingindex.html', context)
	
def deleteSemesterCookie(request): #Reusable function, deletes semester cookie and then fowards user onto the location specified in the URL
								   #eg http://localhost:8000/clearsemester/pmo_report_select/ would send the user to http://localhost:8000/pmo_report_select/ upon completion
								   #not specifying a redirection location will send the user back to the homepage
	redir = request.path.split("/")[2]
	try:
			del request.session['semester_id']
	except KeyError:
       		pass
	return redirect('/' + redir)
	
### BEGIN PMO DASHBOARD ###

def pmo_reportindex(request): #Semester selection page for PMO dashboard
	if request.session.get('semester_id', None):
		return redirect('/pmo_report/' + request.session['semester_id'])
	semester_list = Semester.objects.all()
	context = {'semester_list' : semester_list, 'page' : 'report'}
	return render(request, 'timeclock/pmoindex.html', context)
	
def pmo_report(request, semester_name): #PMO Dashboard report generation
	request.session['semester_id'] = request.path.split("/")[2]
	project_stats = [] #list to pass to context
	project_list = Project.objects.filter(semester=semester_name)
	for project in project_list:
		avg = Shift.objects.filter(project_id=project.id).aggregate(Sum('total_time')) #What do I divide this by to obtain the actual average?
		ltweeks = 0 #still need to make query for sum of last two weeks.
		project_stats.append(ProjectStat(project.id,project.project_name,avg,ltweeks)) #Using a new class ProjectStat which holds project info and stats together
	context = {'project_list' : project_stats, 'page' : 'pmo', 'page' : 'report'}
	return render(request, 'timeclock/pmo_report.html', context)

### END PMO DASHBOARD ###
	
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

	project1 = Project.objects.get(student=student_id)

	if submitted_deliverables == '':
		newshift = Shift(project=project1, shift_student=student_id_number, time_start=submitted_time_start, time_end=submitted_time_end, total_time=submitted_total_time)
	else:
		newshift = Shift(project=project1, shift_student=student_id_number, time_start=submitted_time_start, time_end=submitted_time_end, total_time=submitted_total_time,  deliverables=submitted_deliverables)
	newshift.save()
	context = {'student_id':student_id}
	return render(request, 'timeclock/success.html', context)



def reporting(request):

	semester_id = request.GET['semester_id']
	
	

	try:
		end_date = request.GET['enddate']
		end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y')
	except:
		end_date = datetime.datetime.today()


	try:
		start_date = request.GET['startdate']
		start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y')
	except:
		start_date = end_date - datetime.timedelta(days=7)


	#Getting some information that I need to do things
	
	#if start_date or end_date == "":
	#	end_date = datetime.date.today()
	#	start_date = end_date - datetime.timedelta(days=7)
	semester = Semester.objects.filter(id=semester_id)
	students = Student.objects.filter(semester=semester).order_by("project")
#This is the object that is used to spit out all of the 
	shifts = Shift.objects.filter(time_start__gte=start_date, time_start__lte=end_date + datetime.timedelta(days=1)).order_by('project')


	simple_report = []
	hours = []
	deliverables_list = []


#Generates the aggregated table
	for x in Project.objects.filter(semester=semester_id):
		z = Shift.objects.filter(project=x, time_start__gte=start_date, time_start__lt=end_date + datetime.timedelta(days=1)).aggregate(Avg('total_time'))
		hours.append(z.get('total_time__avg'))



#Generates the detailed table
	for shift in shifts:
		#Get the unique project names
		y = shift.shift_student.project.project_name
		y = str(y)
		#For each project name total up the student time in that range
		if y not in simple_report:
			simple_report.append(y)


#	for x in Project.objects.filter(semester=semester_id).order_by("project_name"):
#		z = Shift.objects.filter(project=x, time_start__gt=start_date).annotate(dcount=Count("project"))
#		for shift in z:
#			if shift.deliverables not in deliverables_list and shift.deliverables != string.whitespace:
#				deliverables_list.append(shift.deliverables)





	context = {'students': students, 'start_date': start_date, 'end_date': end_date, 'shifts' : shifts, 'simple_report' : simple_report, 'hours' : hours, 'deliverables_list' : deliverables_list, 'semester_id' : semester_id } 
	return render(request, 'timeclock/report.html', context)



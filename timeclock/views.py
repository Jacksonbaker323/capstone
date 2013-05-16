from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.shortcuts import render_to_response
from timeclock.models import Semester, Project, Student, Shift, Deliverable, ReportStat, ShiftStat
from django.utils import timezone
from django.utils import tzinfo
import datetime
from django.db.models import Avg, Count, Sum
import string
from django.shortcuts import redirect
from datetime import date, datetime
import datetime


def index(request):
		semester_list = Semester.objects.all()
		if request.session.get('semester_id', None):
			return redirect('/semester/' + request.session['semester_id']) #redirect the user to the appropriate semester page
		#var 	=  'name in html file' : variable } #see below to add more variables to html
		context = {'semester_list' : semester_list, 'page' : 'index'}
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
	shift_list = []
	today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	startdate = today - datetime.timedelta(days=14)
	today = today + datetime.timedelta(days=1)
	print(str(today))
	shifts =  Shift.objects.filter(shift_student=student_id).filter(time_start__gte=startdate).filter(time_end__lt=today).order_by("-time_start")
	
	for shift in shifts:
		shiftDate = shift.time_start.date()
		shiftStart = shift.time_start.time()
		shiftEnd = shift.time_end.time()
		hours = shift.total_time
		deliverables = shift.deliverables
		shift_list.append(ShiftStat(shiftDate,hours,shiftStart,shiftEnd,deliverables))
	#shift_list populated
	deliverables = Deliverable.objects.all()
	context = { 'student' : student, 'deliverables' :deliverables, 'student_id' : student_id, 'shift_list' : shift_list }
	return render(request, 'timeclock/entertime.html', context)

def reportingindex(request):
	semester_list = Semester.objects.all()
	if request.session.get('semester_id', None):
			return redirect('/reporting/' + request.session['semester_id']) #redirect the user to the appropriate semester page
	context = {'semester_list' : semester_list, 'page' : 'report', 'report' : 'faculty'}
	return render(request, 'timeclock/reportingindex.html', context)
	
def deleteSemesterCookie(request): #Reusable function, deletes semester cookie and then fowards user onto the location specified in the URL
								   #eg http://localhost:8000/clearsemester/pmo_report_select/ would send the user to http://localhost:8000/pmo_report_select/ upon completion
								   #not specifying a redirection location will send the user back to the homepage
	redir = request.path.split("/")[2]
	try:
			del request.session['semester_id']
	except KeyError: #Catch error from trying to delete non-existent cookie
       		pass
	return redirect('/' + redir)
	
### BEGIN PMO DASHBOARD ###

def pmo_reportindex(request): #Semester selection page for PMO dashboard
	if request.session.get('semester_id', None):
		return redirect('/pmo_report/' + request.session['semester_id'])
	semester_list = Semester.objects.all()
	context = {'semester_list' : semester_list, 'page' : 'report', 'report' : 'pmo'}
	return render(request, 'timeclock/pmoindex.html', context)
	
def pmo_report(request, semester_name): #PMO Dashboard report generation
	request.session['semester_id'] = request.path.split("/")[2]
	project_stats = [] #list to pass to context
	project_list = Project.objects.filter(semester=semester_name)
	curSemester = Semester.objects.filter(id=semester_name) #Get current semester so we can get start and end dates
	sb = curSemester[0].start_date #start date of semester
	se = curSemester[0].end_date #end date of semester
	today = date.today()
	if today < se: #if we haven't reached the end of the semester, use today as our boundary, otherwise we're using the semester end date
		se = today
	## BEGIN WEEK COUNT ##	
	weekcnt = 0
	weeks = []
	dt = sb
	while dt <= se:
		week = [0] * 2
		week[0] = dt
		week[1] = dt + datetime.timedelta(days=7)
		weeks.append(week)
		dt = dt + datetime.timedelta(days=7)
	for week in weeks:
		if len(Shift.objects.filter(time_start__gte=week[0]).filter(time_end__lt=week[1])) > 0: #This week has at least one shift in it
			weekcnt += 1
	if weekcnt == 0:
		weekcnt = 1 #To prevent divide by zero
	## END WEEK COUNT ##
	#weeks = se.isocalendar()[1] - sb.isocalendar()[1] #compute the weeks between the two dates using the ISO calendar
	for project in project_list:
		avg = Shift.objects.filter(project_id=project.id).aggregate(Sum('total_time')) #What do I divide this by to obtain the actual average?
		if avg['total_time__sum'] != None: #checking if there's actually numbers to average
			avg['total_time__sum'] = round(float(avg['total_time__sum']) / weekcnt,4) #divide and convert into a 4 digit decimal number
		ltwkstart = today - datetime.timedelta(days=7) #start a week ago
		while ltwkstart.weekday() != 0: #0 is monday
			ltwkstart = ltwkstart - datetime.timedelta(days=1) #count backwards from a week ago until we find monday
		ltwkend = ltwkstart + datetime.timedelta(days=6)
		ltweeks = Shift.objects.filter(project_id=project.id).filter(time_start__gte=ltwkstart).filter(time_end__lt=ltwkend).aggregate(Sum('total_time'))
		#above line means:											time_start >= ltwkstart				time_end <= ltwkend
		#NOTE: This is read as project_id=project.id AND time_start >= ltwkstart AND time_end <= ltwkend
		#I know this is an awful place to put this, but to do an OR criteria, you would do .filter(A, B)
		#for some reason, >= and <= are not acceptable to django's module.. despite being the scheme for python in general.
		project_stats.append(ReportStat(project.id,project.project_name,avg,ltweeks)) #Using a new class ReportStat which holds project info and stats together
	context = {'project_list' : project_stats, 'page' : 'pmo', 'page' : 'report', 'report' : 'pmo'}
	return render(request, 'timeclock/pmo_report.html', context)

### END PMO DASHBOARD ###

### BEGIN PM DASHBOARD ###

def pm_reportindex(request, semester_name=None): #Semester/Project selection page for PM dashboard
	if request.session.get('semester_id', None):
		if semester_name == None: #Semester cookie is set, but we're not looking at that semester yet so we redirect user to project selection for that semester
			return redirect('/pm_report_select/' + str(request.session['semester_id']))
	if semester_name:
		request.session['semester_id'] = request.path.split("/")[2] #store the cookie in case it isn't already present
		listobj = 'Project' #We're going to want our dropdown to say select a project
		list = Project.objects.filter(semester=semester_name) #Get our list of projects in the selected semester
	else:
		listobj = 'Semester' #We're going to want our dropdown to say select a semester
		list = Semester.objects.all() #Get our list of semesters
	context = {'list' : list, 'listobj' : listobj, 'page' : 'report', 'report' : 'pm'}
	return render(request, 'timeclock/pmindex.html', context)
	
def pm_report(request, project_name): #PMO Dashboard report generation
	projectid = request.path.split("/")[2]
	student_stats = [] #list to pass to context
	student_list = Student.objects.filter(project=projectid)
	curProject = Project.objects.filter(id=projectid) #Get current project object so we can get our semester id
	curSemester = Semester.objects.filter(id=curProject[0].semester.id) #Get current semester so we can get start and end dates
	sb = curSemester[0].start_date #start date of semester
	se = curSemester[0].end_date #end date of semester
	today = date.today()
	if today < se: #if we haven't reached the end of the semester, use today as our boundary, otherwise we're using the semester end date
		se = today
	## BEGIN WEEK COUNT ##	
	weekcnt = 0
	weeks = []
	dt = sb
	while dt <= se:
		week = [0] * 2
		week[0] = dt
		week[1] = dt + datetime.timedelta(days=7)
		weeks.append(week)
		dt = dt + datetime.timedelta(days=7)
	for week in weeks:
		if len(Shift.objects.filter(project_id=projectid).filter(time_start__gte=week[0]).filter(time_end__lt=week[1])) > 0: #This week has at least one shift in it
			weekcnt += 1
	if weekcnt == 0:
		weekcnt = 1 #To prevent divide by zero
	## END WEEK COUNT ##
	#weeks = se.isocalendar()[1] - sb.isocalendar()[1] #compute the weeks between the two dates using the ISO calendar
	for student in student_list:
		avg = Shift.objects.filter(project_id=projectid).filter(shift_student=student.id).aggregate(Sum('total_time')) #gets raw total
		if avg['total_time__sum'] != None: #checking if there's actually numbers to average
			avg['total_time__sum'] = round(float(avg['total_time__sum']) / weekcnt,4) #divide and convert into a 4 digit decimal number
		ltwkstart = today - datetime.timedelta(days=7) #start a week ago
		while ltwkstart.weekday() != 0: #0 is monday
			ltwkstart = ltwkstart - datetime.timedelta(days=1) #count backwards from a week ago until we find monday
		ltwkend = ltwkstart + datetime.timedelta(days=6)
		ltweeks = Shift.objects.filter(project_id=projectid).filter(shift_student=student.id).filter(time_start__gte=ltwkstart).filter(time_end__lt=ltwkend).aggregate(Sum('total_time'))
		#above line means:																			time_start >= ltwkstart				time_end <= ltwkend
		#NOTE: This is read as project_id=project.id AND shift_student=student.id AND time_start >= ltwkstart AND time_end <= ltwkend
		#I know this is an awful place to put this, but to do an OR criteria, you would do .filter(A, B)
		#for some reason, >= and <= are not acceptable to django's module.. despite being the scheme for python in general.
		student_stats.append(ReportStat(student.id,student.student_name,avg,ltweeks)) #Using a new class ReportStat which holds project info and stats together
	context = {'project_list' : student_stats, 'page' : 'pmo', 'page' : 'report', 'report' : 'pm'}
	return render(request, 'timeclock/pm_report.html', context)

### END PM DASHBOARD ###
	
def submittime(request):
	

##### STARTDATE DATETIME OBJECT 


	#Check for the startdate to be not empty
	if request.GET['startdate'] == "":
		context = {'error' : "Please enter a date" }
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
		#submitted_time_start = timezone.make_aware(submitted_time_start, timezone.get_default_timezone())
##### ENDDATE DATETIME OBJECT 
		#Check for the enddate to be not empty
	#if request.GET['enddate'] == "":
		#context = {'error' : "Please enter a end date" }
		#return render(request, 'timeclock/error.html', context)
	#else:
		#if enddate has text in it convert it to a date object
		#enddate = request.GET['enddate']

	#if request.GET['endtime'] == "":
		#context = {'error' :"Please enter a end time"}
		#return render(request, 'timeclock/error.html', context)
	#else: 
		#Build the time_start object to put in the database
		endtime = request.GET['endtime']
		end_string = startdate + " " + endtime
		submitted_time_end = datetime.datetime.strptime(end_string, '%m/%d/%Y %I:%M %p')
		#submitted_time_end = timezone.make_aware(submitted_time_end, timezone.get_default_timezone())
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
	return redirect('/student/' + str(student_id)) #redirect the user to the appropriate semester page
	#return render(request, 'timeclock/success.html', context)



def reporting(request, semester_name = 0):
	
	if semester_name == 0:
		today = date.today()
		currentSemester = Semester.objects.filter(start_date__lt=today).filter(end_date__gte=today)
		try:
			semester_name = currentSemester[0].id
		except: #Today doesn't fall into a semester, take the newest semester instead
			semesterList = Semester.objects.all.order_by('-id')
			semester_name = semesterList[0].id
	else:
		request.session['semester_id'] = semester_name
	semester_id = semester_name		
	semester = Semester.objects.filter(id=semester_id)
	semester = semester[0]
	try:
		end_date = request.GET['enddate']
		end_date = datetime.datetime.strptime(end_date, '%m/%d/%Y')
	except:
		#end_date = datetime.datetime.today()
		end_date = semester.end_date


	try:
		start_date = request.GET['startdate']
		start_date = datetime.datetime.strptime(start_date, '%m/%d/%Y')
	except:
		#start_date = end_date - datetime.timedelta(days=7)
		start_date = semester.start_date


	#Getting some information that I need to do things
	
	#if start_date or end_date == "":
	#	end_date = datetime.date.today()
	#	start_date = end_date - datetime.timedelta(days=7)
	sem = Semester.objects.filter(id=semester_id)
	students = Student.objects.filter(semester=sem).order_by("project")
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





	context = {'students': students, 'start_date': start_date, 'end_date': end_date, 'shifts' : shifts, 'simple_report' : simple_report, 'hours' : hours, 'deliverables_list' : deliverables_list, 'semester_id' : semester_id, 'page' : 'report', 'report' : 'faculty' , 'semester' : semester} 
	return render(request, 'timeclock/report.html', context)



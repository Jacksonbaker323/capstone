from django.db import models

# Create your models here.

class Semester(models.Model):
	semester_name = models.CharField(max_length=200)
	#variable that matches DB table field = models.Type(parameters)
	#For a list of models see https://docs.djangoproject.com/en/dev/ref/models/fields/
	start_date = models.DateField()
	end_date = models.DateField()
	
	def __unicode__(self):
		return self.semester_name

class Project(models.Model):
	semester = models.ForeignKey(Semester)
	project_name = models.CharField(max_length=200)

	def __unicode__(self):
		return self.project_name

class ReportStat:  #Class used by PM and PMO dashboard, allows for the combination of database and computed variables into one object for easier transport to the HTML view
				   #This class is currently the only class that is not backed by an identical database structure.
	def __init__(self,id,name,avg,lstwk):
		self.id = id
		self.name = name
		self.avghrs = avg
		self.lstwkhrs = lstwk
		
	def __str__(self):
		return self.project_name
		
class ShiftStat:

	def __init__(self,shiftDate,hours,stTime,edTime,deliverables,shiftID):
		self.shiftDate = shiftDate
		self.hours = hours
		self.stTime = stTime
		self.edTime = edTime
		self.deliverables = deliverables
		self.shiftID = shiftID
	
	
		
class Student(models.Model):
	project = models.ForeignKey(Project)
	student_name = models.CharField(max_length=200)
	semester = models.ForeignKey(Semester)
	
	def __unicode__(self):
		return self.student_name

class Shift(models.Model):
	project = models.ForeignKey(Project)
	shift_student = models.ForeignKey(Student)
	time_start = models.DateTimeField('Start Time')
	time_end = models.DateTimeField('End Time')
	total_time = models.FloatField('Total Time')
	deliverables = models.CharField(max_length=1000)


	def __unicode__(self):
		return str(self.shift_student) + " Start: "  + str(self.time_start) + " End: " + str(self.time_end)

class Deliverable(models.Model):
	deliverable_name = models.CharField(max_length=1000)

	def __unicode__(self):
		return self.deliverable_name

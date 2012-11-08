from django.db import models

# Create your models here.

class Semester(models.Model):
	semester_name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.semester_name

class Project(models.Model):
	semester = models.ForeignKey(Semester)
	project_name = models.CharField(max_length=200)

	def __unicode__(self):
		return self.project_name

class Student(models.Model):
	project = models.ForeignKey(Project)
	student_name = models.CharField(max_length=200)
	
	def __unicode__(self):
		return self.student_name

class Shift(models.Model):
	shift_student = models.ForeignKey(Student)
	time_start = models.DateTimeField('Start Time')
	time_end = models.DateTimeField('End Time')
	deliverables = models.CharField(max_length=1000)

	def __unicode__(self):
		return str(self.shift_student) + " Start: "  + str(self.time_start) + " End: " + str(self.time_end)

class Deliverable(models.Model):
	deliverable_name = models.CharField(max_length=1000)

	def __unicode__(self):
		return self.deliverable_name

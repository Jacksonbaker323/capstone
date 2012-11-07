from timeclock.models import Semester
from timeclock.models import Project
from timeclock.models import Student
from timeclock.models import Shift
from timeclock.models import Deliverable

from django.contrib import admin

admin.site.register(Semester)
admin.site.register(Project)
admin.site.register(Student)
admin.site.register(Shift)
admin.site.register(Deliverable)
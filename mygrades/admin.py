from django.contrib import admin
from django.conf.urls import handler404, handler500

# Register your models here.
from mygrades.models import (
    Student,  
    #Authentication, 
    Curriculum,
    #Enrollment,
    )

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = (
        "epicenter_id",
        "last_name",
    )


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_filter = (
        "subject",
        "id",
        
    )

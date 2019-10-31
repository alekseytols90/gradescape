from django.contrib import admin
from django.conf.urls import handler404, handler500

# Register your models here.
from mygrades.models import (
    Student,
    # Authentication,
    Curriculum,
    # Enrollment,
    Assignment,
    Standard,
    ExemptAssignment,
    User,
    Teacher,
    GradeBook)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_filter = (
        "epicenter_id",
        "last_name",
    )
    raw_id_fields = ['curriculum']


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_filter = (
        "subject",
        "id",

    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = (
        "last_name",
        "first_name",
    )


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_filter = (
        "last_name",
        "first_name",
    )


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_filter = (
        "name",
    )
    raw_id_fields = ['standard']
    fields = ['standard', 'curriculum', 'name', 'description', 'status', 'type_of', 'submission_date', 'active', 'late']
    readonly_fields = ('active', 'late', 'registered_datetime')


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_filter = (
        "standard_code",
    )


@admin.register(ExemptAssignment)
class ExceptAssignmentAdmin(admin.ModelAdmin):
    raw_id_fields = ['student', 'assignments']
    fields = ['student', 'assignments']


@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):
    list_filter = (
        "week",
    )


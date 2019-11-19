from django.contrib import admin
from django.conf.urls import handler404, handler500

# Register your models here.
from mygrades.models import (
    Student,
    # Authentication,
    Curriculum,
    Enrollment,
    Assignment,
    StudentAssignment,
    Standard,
    ExemptAssignment,
    User,
    Teacher,
    GradeBook,
    StudentGradeBookReport,
    Attendance)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student','curriculum','weight','level']
    raw_id_fields = ['student','curriculum']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    raw_id_fields = ['curriculum']
    search_fields = ['last_name','first_name']


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
    list_filter = ("type_of",)
    raw_id_fields = ['standard', 'curriculum']
    fields = ['standard', 'curriculum', 'name', 'description', 'type_of']


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_filter = ("status","active","late")
    list_display = ("__str__","status")
    raw_id_fields = ['assignment','student', 'enrollment']
    fields = ['student','assignment', 'enrollment', 'status', 'submission_date', 'registered_datetime', 'active', 'late']
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

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    raw_id_fields = ['student','enrollment']
    list_display = ("student","enrollment", "enr_gradassign", "quarter","week","semester", "complete")

    def enr_gradassign(self, obj):
        return obj.enrollment.gradassign

@admin.register(StudentGradeBookReport)
class StudentReportAdmin(admin.ModelAdmin):
    raw_id_fields = ['student']
    list_display = ("student","created","updated", "report_type", "academic_semester", "quarter", "week", "semester")
    list_filter = ("report_type",)


import datetime
import json
from django import forms
from django.forms import BaseModelFormSet 
from django.forms import BaseFormSet
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.db.models import Count, F
from django.contrib.admin import widgets
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from mygrades.models import (
    Student,
    Curriculum,
    Enrollment,
    Standard,
    Assignment,
    Attendance,
    StudentAssignment,
    GradeBook,
    User,
    Teacher,
    StudentGradeBookReport,
)

CURRICULUMGRADE = [
    ("P", "Pre-K"),
    ("K", "Kinder"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
    ("All", "All"),
    ("High School", "High School"),
]

SUBJECT = [
    ("Math", "Math"),
    ("ELA", "ELA"),
    ("Science", "Science"),
    ("History", "History"),
    ("Other", "Other"),
]

GRADELEVEL = [
    ("P", "Pre-K"),
    ("K", "Kindergarten"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
    ("11", "11"),
    ("12", "12"),
]

SEMESTER = [("1", "1"),
            ("2", "2"),
            ("Full Year", "Full Year"),
            ]

STATUS = [
    ("Not Assigned", "Not Assigned"),
    ("Assigned", "Assigned"),
    ("Incomplete", "Incomplete"),
    ("Complete", "Complete"),
]

RECORDED = [("Manual", "Manual"),
            ("Automatic", "Automatic"),
            ]

LEVEL = [("Core", "Core"),
         ("Supplemental", "Supplemental"),
         ]

TRACKING = [
    ("Minutes", "Minutes"),
    ("Lessons or Quizzes", "Lessons or Quizzes"),
    ("Percentage Complete", "Percentage Complete"),

]

def generate_semester_choices(for_choice_field=False):
    """ Generate options for per semester for the current academic year and the next

        1- get current year
        2- if I'm before Jul 30 of c_year, base:  (c_year-1)-c_year    -> start by c_year-1
           if I'm after  Jul 30 of c_year, base: c_year-(c_year+1)    -> start by c_year

        Examples:
        19-20 A
        19-20 B
        20-21 A
        20-21 B

        Formulation:
        start-(start+1)-A
        start-(start+1)-B
        (start+1)-(start+2)-A
        (start+1)-(start+2)-B
    """
    now = timezone.now()
    current_year = now.year
    start = current_year
    july_end = datetime.datetime(current_year,7,30) 
    july_end_tz_aware = timezone.make_aware(july_end, timezone.get_default_timezone())

    if now < july_end_tz_aware:
        start = current_year - 1

    options = []
    options.append("%s-%s-%s" % (str(start)[2:],str(start+1)[2:], "A"))
    options.append("%s-%s-%s" % (str(start)[2:],str(start+1)[2:], "B"))
    options.append("%s-%s-%s" % (str(start+1)[2:],str(start+2)[2:], "A"))
    options.append("%s-%s-%s" % (str(start+1)[2:],str(start+2)[2:], "B"))

    if for_choice_field:
        choices = []
        for option in options:
            choices.append((option,option))
        return choices

    return options


def set_css_attr(form):
    input_class = [forms.widgets.TextInput, forms.widgets.ClearableFileInput]
    for name, field in form.fields.items():
        field.widget.attrs['max_length'] = 200
        if field.widget.__class__ in input_class:
            field.widget.attrs.update({'class': 'form-control placeholder-no-fix input-circle'})

        if field.widget.__class__ == forms.widgets.ClearableFileInput:
            field.widget.attrs.update({'multiple': '', 'id': 'filepicker', 'webkitdirectory': '', 'directory': ''})


class CustomCurriculumSetUpForm(forms.ModelForm):
    # username=forms.CharField(required=False, label="Your Username For Website (Only if Data Pulls Automatically - You may leave blank.)")
    # password=forms.CharField(required=False, label="Your Password For Website (Only if Data Pulls Automatically - You may leave blank.)")
    # loginurl=forms.CharField(required=False, label = "EXACT URL Of Page With Data (Copy and Paste - Only if Data Pulls Automatically - You may leave blank.)")
    # required=forms.CharField(required=False, label="Number of Minues or Lessons Required EACH WEEK")
    # weight=forms.CharField(required=False, label="Leave BLANK if no weighting is used. \nIf Weighted, What Percentage of the Subject Grade Will This Be?  \nNOTE:  If you weight one item for a subject, you must weight them all and make sure the weights add up to 100.  If you do NOT enter a value, all curriculum items for one subject will be weighted evenly.")
    # level=forms.ChoiceField(choices = LEVEL, widget=forms.RadioSelect, label="CORE Determines order of Assignments on Pacing, Supplemental follows the Progress of the CORE Curriculum based on common standards.")
    subject = forms.ChoiceField(choices=SUBJECT, widget=forms.RadioSelect, label="Subject")

    # tracking=forms.ChoiceField(choices = TRACKING, widget=forms.RadioSelect, label="How will you track this curriculum?")
    # gradassign=forms.CharField(required=False, label = "For Which Gradable Assignment Will This Curriculum Be Recorded?")

    class Meta:
        model = Curriculum
        fields = [
            "name",
            "subject",
            "grade_level",
            # "tracking",
            # "weight",
            # "semesterend",
            # "username",
            # "password",
            # "loginurl",
            # "recorded_from",
            # "required",
            # "level",
        ]
        labels = {
            "name": "Title of Curriculum",
            "subject": "Subject",
            "grade_level": "Grade Level",
            # "tracking": "How Will You Track This Data?",
            # "recorded_from": "How Will You Get This Data?",
            # "required":"Number of Minutes or Lessons Required Each Week?",
            # "weight":"Leave BLANK if no weighting is used. \nIf Weighted, What Percentage of the Subject Grade Will This Be?  \nNOTE:  If you weight one item for a subject, you must weight them all and make sure the weights add up to 100.  If you do NOT enter a value, all curriculum items for one subject will be weighted evenly.",
            # "semesterend":"SEMESTER Completion Date for This Curriculum",
            # "username":"Your Username For Website (Only if Data Pulls Automatically - You may leave blank.)",
            # "password":"Your Password For Website (Only if Data Pulls Automatically - You may leave blank.)",
            # "loginurl":"EXACT URL Of Page With Data (Copy and Paste - Only if Data Pulls Automatically - You may leave blank.)",
            # "level": "CORE Determines order of Assignments on Pacing, Supplemental follows the Progress of the CORE Curriculum based on common standards."
        }


class StudentModelForm(forms.ModelForm):
    additional_email = forms.CharField(required=False)
    additional_phone_number = forms.CharField(required=False)

    class Meta:
        model = Student
        fields = [
            "epicenter_id",
            "first_name",
            "last_name",
            "email",
            "additional_email",
            "phone_number",
            "additional_phone_number",
            "grade",
            "birthdate",
            "teacher_email",

        ]
        labels = {
            "epicenter_id": "Epicenter ID (ONLY NUMBERS)",
            "first_name": "Student's First Name - Capitalize First Letter ONLY",
            "last_name": "Student's Last Name - Capitalize First Letter ONLY",
            "email": "Student e-Mail",
            "additional_email": "Second eMail Contact - May Be Left Blank",
            "phone_number": "Phone Number",
            "additional_phone_number": "Second Phone Number - May Be Left Blank",
            "grade": "Student Enrollment Grade - Change this each year for previous students.",
            "birthdate": "Date of Birth (Happy Birthday shows on Student's screen)",
            "teacher_email": "Teacher's eMail - MUST be the email that you supplied when you purchased your site.  ALL LOWERCASE.  Any mis-spelling will hide your students from you.",
        }

    def clean_epicenter_id(self, *arts, **kwargs):
        instance = self.instance
        print(instance)
        cleaned_epicenter_id = self.cleaned_data.get("epicenter_id")
        qs = Student.objects.filter(
            epicenter_id__iexact=cleaned_epicenter_id
        )  # icontains is case insensitive
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "This Epicenter ID is already registered."
            )
        return cleaned_epicenter_id


SUBJECT_EMPTY = [('','---------')] + Curriculum.SUBJECT
CURRICULUMGRADE_EMPTY = [('','---------')] + Curriculum.CURRICULUMGRADE

class CurriculumViewForm(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECT_EMPTY, required=False) # js filter purposes, value not used
    grade_level = forms.ChoiceField(choices=CURRICULUMGRADE_EMPTY, required=False) # js filter purposes, value not used

class CurriculumEnrollmentForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=SUBJECT_EMPTY, required=False) # js filter purposes, value not used
    grade_level = forms.ChoiceField(choices=CURRICULUMGRADE_EMPTY, required=False) # js filter purposes, value not used 
    is_min_required = forms.BooleanField(required=False, label="Is minimum required?", help_text="Is there a minimum number of lessons or minutes required each week?") # whether to collect required field, also note that help_texts doesn't work on Meta for extra fields

    class Meta:
        model = Enrollment
        
        #weight is not in the form
        fields = ["student","academic_semester","subject","grade_level","curriculum","tracking","is_min_required", "required","semesterend","level","gradassign","recorded_from", "username","password","loginurl"] 

        labels = {
            "required": "Minimum",
            "semesterend": "Completion Date (Don't forget to advance this date for breaks and vacations.)",
            "level": "Level",
            "recorded_from": "Progress",
            "tracking": "Pacing Method",
            "gradassign": "Gradable Assignments",
            "username": "Username",
            "password": "Password",
            "loginurl": "YOUR Website",
        }

        help_texts = {
            "required": "Number of Minutes, Classes or Lessons Required Each Week",
            "semesterend": "By What Date Should This Curriculum Be Finished (Don't forget to back up for vacations)?",
            "level": "Is this CORE (determines pace) or Supplemental?",
            "recorded_from": "Will you manually enter this progress or will the system retrieve data automatically?",
            "tracking": "Will These Assignments Come from a Pacing Guide or Repeat Each Week?",
            "gradassign": "In which gradable assignment will this curriculum be included?",
            "username": "What is your username into the site from which this progress will be pulled?",
            "password": "What is your password into the site from which this progress will be pulled?",
            "loginurl": "What is EXACT URL - Copy and Paste it here - of the page on which the student progress is found?",

        }
        widgets = {
                'curriculum': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        student_pk = kwargs.pop("student_pk",None)
        cqs = kwargs.pop("curriculum_qs",None)
        super(CurriculumEnrollmentForm, self).__init__(*args, **kwargs)
        qs = Student.objects.filter(pk=student_pk)
        self.fields["student"].queryset = qs.order_by("last_name")
        self.fields["student"].widget = forms.HiddenInput()
        self.fields["academic_semester"].widget = forms.HiddenInput() 

        if not self.instance.pk:
            self.fields["curriculum"].queryset = Curriculum.objects.none()
            if cqs: # early range restriction on submitted grade_level and subject
                self.fields["curriculum"].queryset = cqs
        else: # support editing
            self.fields["student"].queryset = Student.objects.filter(pk=self.instance.student.pk)
            self.fields["curriculum"].queryset = Curriculum.objects.filter(pk=self.instance.curriculum.pk)
            self.fields["curriculum"].widget = forms.HiddenInput() 

    def clean_semesterend(self):
        sem = self.cleaned_data['semesterend']
        if sem < timezone.now():
            raise forms.ValidationError("Semester end must be set to a date in future.")
        return sem

    def clean_academic_semester(self):
        as_options = generate_semester_choices()
        asem = self.cleaned_data['academic_semester']
        if not asem in as_options:
            raise forms.ValidationError("Academic semester must be in options: %s" % str(as_options))
        return asem

    def clean(self):
        cleaned_data = super().clean()
        cur = cleaned_data['curriculum']
        semester = cleaned_data['academic_semester']
        student = cleaned_data['student']
        subject = cur.subject

        if not self.instance.pk:
            core_enrollment = Enrollment.objects.filter(student=student, academic_semester=semester, curriculum__subject=subject, level="Core")

            if cleaned_data['level'] == "Core":
                if core_enrollment.count() > 0:
                    self.add_error(None, "A core enrollment already exist for subject \"%s\"." % subject)
            else: #supplemental
                if core_enrollment.count() == 0:
                    self.add_error(None, "First enrollment must be core for subject \"%s\"." % subject)
        else:
            if self.initial["level"] == "Core" and cleaned_data["level"] == "Supplemental":
                self.add_error(None, mark_safe("Hey, wait Teacher, %s is %s's CORE curriculum. It is setting her pace. If you want to make it a Supplemental curriculum, first choose another CORE <a href='%s'>here</a> first for subject %s." % (cur.name,student.get_full_name(), reverse("curriculum-schedule-detail",args=[self.instance.student.pk]), subject)))

        recorded_from = cleaned_data['recorded_from']
        username = cleaned_data['username']
        password = cleaned_data['password']
        loginurl = cleaned_data['loginurl']
        if recorded_from == 'Automatic' and not (username and password and loginurl):
            self.add_error(None, "You must enter username/password/loginurl when recording is set to automatic.")
        is_min_required = cleaned_data['is_min_required']
        required = cleaned_data['required']
        if is_min_required and required == None: 
            self.add_error(None, "You must enter a value in required if this enrollment requires minimum number of minutes/attendance/lessons/reads.")

    def save(self):
        m = super(CurriculumEnrollmentForm, self).save(commit=True)

        # distribute weight
        student = self.cleaned_data['student']
        academic_semester = self.cleaned_data['academic_semester']
        distribute_weights_for_sem(student, academic_semester, self.instance.curriculum.subject)

        # copy assignments
        for item in self.instance.curriculum.curriculum_assignment.all():
            sa = StudentAssignment(student=self.instance.student, assignment=item, enrollment=m, status="Not Assigned")
            sa.save()

        return m

class CurriculumEnrollmentUpdateForm(CurriculumEnrollmentForm):
    def __init__(self, *args, **kwargs):
        super(CurriculumEnrollmentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget = forms.HiddenInput()
        self.fields['grade_level'].widget = forms.HiddenInput()

    def save(self):
        # update the new core
        if self.initial["level"] == "Supplemental" and self.cleaned_data["level"] == "Core":
            core_enrollment = Enrollment.objects.filter(student=self.instance.student, academic_semester=self.instance.academic_semester, curriculum__subject=self.instance.curriculum.subject, level="Core")
            core_enrollment.update(level="Supplemental")

        m = super(CurriculumEnrollmentForm, self).save(commit=True)
        return m


# to know which sems/subjects are editable for weight
# Example:
# >> get_active_sems(student)
# [{'sem': '19-20-A', 'subjects': ['Math', 'Science', 'History']}]
def get_active_sems(student):
    as_options = generate_semester_choices()
    active_sems = []
    for sem in as_options:
        enrollments = Enrollment.objects.filter(student=student, academic_semester=sem)
        if enrollments.count() > 0:
            data = {'sem':sem,'subjects':[]}
            for enr in enrollments:
                subject = enr.curriculum.subject
                if not subject in data['subjects']:
                    data['subjects'].append(subject)
            active_sems.append(data)
    return active_sems


# make sure total weight is 100
# this should be called whenever enroll/withdraw happens
def distribute_weights_for_sem(student, sem, subject):
    enr_set = Enrollment.objects.filter(academic_semester=sem, student=student, curriculum__subject=subject)
    count = enr_set.count()

    if count > 0:
        average = 100 // count

        for enr in enr_set:
            enr.weight = average
            enr.save()

        if average*count < 100:
            remaining = 100 - average*count
            enr.weight += remaining
            enr.save()

class StandardSetupForm(forms.ModelForm):
    strand_description = forms.CharField(required=False)
    strand = forms.CharField(required=False)
    strand_code = forms.CharField(required=False)
    PDF_link = forms.CharField(required=False)

    class Meta:
        model = Standard

        fields = [
            "grade_level",
            "standard_number",
            "standard_description",
            "strand_code",
            "strand",
            "strand_description",
            "objective_number",
            "objective_description",
            "standard_code",
            "subject",
            "PDF_link",
        ]

        labels = {
            "grade_level": "Grade Level",
            "standard_number": "Standard Number or Letter Designation",
            "standard_description": "Standard Description",
            "strand_code": "Strand Code (May Be Blank)-See Diagram",
            "strand": "Strand Title (May Be Blank)-See Diagram",
            "strand_description": "Strand Description (May Be Blank)-See Diagram",
            "objective_number": "Objective Number",
            "objective_description": "Objective Description",
            "standard_code": "Complete Standard Code",
            "subject": "Subject",
            "PDF_link": "Link to State Department PDF (May Be Blank)",
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        request = kwargs.pop("request", None)
        super(StandardSetupForm, self).__init__(*args, **kwargs)

class RecordGradeManualForm(forms.ModelForm):
    WEEK = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("11", "11"),
        ("12", "12"),
        ("13", "13"),
        ("14", "14"),
        ("15", "15"),
        ("16", "16"),
        ("17", "17"),
        ("18", "18"),
        ("19", "19"),
        ("20", "20"),
        ("21", "21"),
        ("22", "22"),
        ("23", "23"),
        ("24", "24"),
        ("25", "25"),
        ("26", "26"),
        ("27", "27"),
        ("28", "28"),
        ("29", "29"),
        ("30", "30"),
        ("31", "31"),
        ("32", "32"),
        ("33", "33"),
        ("34", "34"),
        ("35", "35"),
        ("36", "36"),
    ]

    QUARTER = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    ]

    SEMESTER = [
        ("1", "1"),
        ("2", "2"),
    ]

    class Meta:
        model = GradeBook

        fields = [
            "student",
            "curriculum",
            "academic_semester",
            "complete",
            "required",
            "quarter",
            "week",
            "grade",
            "semester",
        ]

        labels = {
            "student": "Student",
            "curriculum": "Curriculum",
            "enrollment": "Enrollment",
            "complete": "Number of Lessons or Minutes Completed",
            "required": "Number of Lessons or Minutes Required",
            "quarter": "Quarter",
            "week": "Week",
            "grade": "Grade",
            "semester": "Semester",
        }

        widgets = {
            'student': forms.HiddenInput(),
            'curriculum': forms.HiddenInput(),
            'academic_semester': forms.HiddenInput(),
        }

        # def __init__(self, *args, **kwargs):
            # super(RecordGradeManualForm, self).__init__(*args, **kwargs)
            # self.fields['student'].widget = forms.HiddenInput()
            # self.fields['curriculum'].widget = forms.HiddenInput()
            # self.fields['academic_semester'].widget = forms.HiddenInput()


class RecordGradeForm(forms.ModelForm):
    WEEK = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("11", "11"),
        ("12", "12"),
        ("13", "13"),
        ("14", "14"),
        ("15", "15"),
        ("16", "16"),
        ("17", "17"),
        ("18", "18"),
        ("19", "19"),
        ("20", "20"),
        ("21", "21"),
        ("22", "22"),
        ("23", "23"),
        ("24", "24"),
        ("25", "25"),
        ("26", "26"),
        ("27", "27"),
        ("28", "28"),
        ("29", "29"),
        ("30", "30"),
        ("31", "31"),
        ("32", "32"),
        ("33", "33"),
        ("34", "34"),
        ("35", "35"),
        ("36", "36"),
    ]

    QUARTER = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    ]

    SEMESTER = [
        ("1", "1"),
        ("2", "2"),
    ]

    class Meta:
        model = GradeBook

        fields = [
            "student",
            "curriculum",
            "complete",
            "required",
            "quarter",
            "week",
            "grade",
            "semester",
        ]

        labels = {
            "student": "Student",
            "curriculum": "Curriculum",
            "complete": "Number of Lessons or Minutes Completed",
            "required": "Number of Lessons or Minutes Required",
            "quarter": "Quarter",
            "week": "Week",
            "grade": "Grade",
            "semester": "Semester",
        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(RecordGradeForm, self).__init__(*args, **kwargs)
            self.fields["student"].queryset = Student.objects.all()
            self.fields["curriculum"].queryset = Enrollment.objects.filter(course_enrollment__icontains=self.student.id)
            set_css_attr(self)


class AssignmentCreateForm(forms.ModelForm):
    standard = forms.ModelMultipleChoiceField(queryset=Standard.objects.all(), required=False)
    description = forms.CharField(required=False)
    
    class Meta:
        model = Assignment

        fields = [
            "name",
            "description",
            "standard",
            "curriculum",
            
        ]

        labels = {
            "name": "Title",
            "description": "Instructions or Link",
            "standard": "OAS Standard Number",
            "curriculum": "In Which Curriculum Will This Assignment Be Included?",

        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(StudentEnrollmentForm, self).__init__(*args, **kwargs)
            self.fields["standard"].queryset = Standard.objects.all()
            self.fields["curriculum"].queryset = Curriculum.objects.all()


class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(value) if value is not None else '-'


class StudentAssignmentForm(forms.ModelForm):
    desc = forms.CharField(widget=PlainTextWidget, required=False, label="Assignment")
    status = forms.ChoiceField(choices=StudentAssignment.STATUS, widget=forms.RadioSelect())

    class Meta:
        model = StudentAssignment
        fields = ('desc','status',)

    def __init__(self, *args, **kwargs):
        super(StudentAssignmentForm, self).__init__(*args, **kwargs)
        if self.instance.pk != None:
            self.fields['desc'].initial = self.instance.assignment.name + "<br/><small>" + self.instance.assignment.description + "</small>"


class SendPacingGuideForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student"]

        labels = {
            "student": "Send This Student His or Her Pacing Guide For The Week",
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        request = kwargs.pop("request", None)
        super(SendPacingGuideForm, self).__init__(*args, **kwargs)


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]

        labels = {
            "username": "Username",
            "password": "Password",
        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(LoginForm, self).__init__(*args, **kwargs)


class TeacherModelForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "last_name",
            "email",
            "zoom",
            "syllabus",
        ]
        labels = {
            "first_name": "Teacher's First Name - Capitalize First Letter ONLY",
            "last_name": "Teacher's Last Name - Capitalize First Letter ONLY",
            "email": "Teacher e-Mail",
            "zoom": "Zoom Link",
            "syllabus":"Syllabus Link",
        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(TeacherModelForm, self).__init__(*args, **kwargs)

class WeightForm(forms.ModelForm):
    class Meta: 
        model = Enrollment
        fields = ('curriculum', 'level', 'weight',)

    def __init__(self, *args, **kwargs):
        super(WeightForm, self).__init__(*args, **kwargs)
        self.fields['curriculum'].queryset = Curriculum.objects.filter(pk=self.instance.curriculum.pk)
        self.fields['curriculum'].widget = forms.HiddenInput()
        self.fields['level'].widget = forms.HiddenInput() 
        self.fields['weight'].label = ""


class BaseWFSet(BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return

        total = 0
        for form in self.forms:
            total += form.cleaned_data.get('weight')

        if total != 100:
            raise forms.ValidationError("Total weight must be 100.")

class ReportProgressForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    student_desc = forms.CharField(widget=PlainTextWidget, required=False, label="Student Name")

    def __init__(self, *args, **kwargs):
        super(ReportProgressForm, self).__init__(*args, **kwargs)
        self.fields['student'].widget = forms.HiddenInput()

    def save(self, asem=None, quarter=None, semester=None):
        if not asem or not quarter or not semester:
            raise Exception("make sure to provide all required parameters to save the report")
        save_report(asem, self.cleaned_data['student'], semester=semester, quarter=quarter, report_type="progress-weekly")


class StatusChangeForm(forms.Form):
    assignment = forms.ModelChoiceField(queryset=StudentAssignment.objects.all())
    assignment_description = forms.CharField(widget=PlainTextWidget, required=False, label="Assignment")
    status = forms.CharField(widget=PlainTextWidget, required=False, label="Status")
    new_status = forms.ChoiceField(choices=StudentAssignment.STATUS)

    def __init__(self, *args, **kwargs):
        super(StatusChangeForm, self).__init__(*args, **kwargs)
        self.fields['assignment'].widget = forms.HiddenInput()

        if "assignment" in self.initial:
            self.fields['status'].initial = "".join([x[0] for x in self.initial['assignment'].status.split(" ")])

    
    def save(self):
        assignment = self.cleaned_data['assignment']
        new_status = self.cleaned_data['new_status']

        assignment.status = new_status 
        #if not new_status in ['Not Assigned', 'Exempt']:
        #    assignment.shown_in_weekly = True 

        assignment.save()

class QuarterForm(forms.Form):
    QUARTER = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    ]

    SEMESTER = [
        ("1", "1"),
        ("2", "2"),
    ]
    semester = forms.ChoiceField(choices=SEMESTER)
    quarter = forms.ChoiceField(choices=QUARTER)
    academic_semester = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(QuarterForm, self).__init__(*args, **kwargs)
        self.fields['academic_semester'].widget = forms.HiddenInput()


class GradableFormStep1(forms.Form):
    WEEK = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("11", "11"),
        ("12", "12"),
        ("13", "13"),
        ("14", "14"),
        ("15", "15"),
        ("16", "16"),
        ("17", "17"),
        ("18", "18"),
        ("19", "19"),
        ("20", "20"),
        ("21", "21"),
        ("22", "22"),
        ("23", "23"),
        ("24", "24"),
        ("25", "25"),
        ("26", "26"),
        ("27", "27"),
        ("28", "28"),
        ("29", "29"),
        ("30", "30"),
        ("31", "31"),
        ("32", "32"),
        ("33", "33"),
        ("34", "34"),
        ("35", "35"),
        ("36", "36"),
    ]

    QUARTER = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    ]

    SEMESTER = [
        ("1", "1"),
        ("2", "2"),
    ]
    semester = forms.ChoiceField(choices=SEMESTER)
    quarter = forms.ChoiceField(choices=QUARTER)
    week = forms.ChoiceField(choices=WEEK)
    academic_semester = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(GradableFormStep1, self).__init__(*args, **kwargs)
        self.fields['academic_semester'].choices = generate_semester_choices(for_choice_field=True)


class EnrollmentGradable(forms.Form):
    desc = forms.CharField(widget=PlainTextWidget, required=False, label="Curriculum", disabled=True) #disabled needed to prevent clean/wipe
    gradassign = forms.CharField(widget=PlainTextWidget, required=False, label="GradAssign", disabled=True) #disabled needed to prevent clean/wipe
    enrollment = forms.ModelChoiceField(queryset=Enrollment.objects.all())
    STATUS = [
        ("Incomplete","Incomplete"),
        ("Complete","Complete")
    ]
    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super(EnrollmentGradable, self).__init__(*args, **kwargs)
        self.fields['enrollment'].widget = forms.HiddenInput()
        if "enrollment" in self.initial:
            self.fields['desc'].initial = self.initial['enrollment'].curriculum.name
            self.fields['gradassign'].initial = self.initial['enrollment'].gradassign



from itertools import groupby

def funk(item):
    return item.cleaned_data['enrollment'].student.pk

class EGBaseFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        self.week_data = kwargs.pop("week_data",None)
        super(EGBaseFormSet, self).__init__(*args, **kwargs)


    def save(self):
        self.alert_email_sent = False
        academic_semester = self.week_data['asem']
        sem = self.week_data['sem']
        week = self.week_data['week']
        quarter = self.week_data['quarter']

        self.forms.sort(key=funk)
        groups = groupby(self.forms, funk)
        student_forms = [[key, [item for item in data]] for (key, data) in groups]

        for form_group in student_forms:
            student = Student.objects.get(pk=form_group[0])
            stats = {}
            for x in range(1,6):
                stats.update({str(x):{"val":0,"count":0}})

            for form in form_group[1]:
                enr = form.cleaned_data['enrollment']
                gradassign = enr.gradassign
                status = form.cleaned_data['status']
                if status == "Complete":
                    stats[gradassign]["val"] += 1
                stats[gradassign]["count"] += 1

                # save individual curriculum attendance 
                attendance = Attendance.objects.filter(student=enr.student,enrollment=enr,week=week,semester=sem,quarter=quarter)
                attended = status == "Complete"
                if attendance.count() > 0:
                    attendance = attendance[0]
                    attendance.complete = attended 
                else:
                    attendance = Attendance(student=enr.student,enrollment=enr,week=week,semester=sem,quarter=quarter, complete=attended)
                attendance.save()

            total_points = 0
            for x in range(1,6):
                stat = stats[str(x)]
                if stat["count"] != 0:
                    if stat["val"] == stat["count"]:
                        total_points += 1

            # Gradable curriculum should exists, so we can note the total gradassign earned for the week.
            # It's advised to have a different model in future to store gradable assignment stats..
            curriculum, created = Curriculum.objects.get_or_create(name='Gradable Assignments', subject='Other', grade_level='All')

            gradebook = GradeBook.objects.filter(student=student,
                                     curriculum=curriculum,
                                     academic_semester=academic_semester,
                                     quarter=quarter,
                                     week=week,
                                     semester=sem)
            if gradebook.count() > 0:
                gradebook = gradebook[0]
                gradebook.grade = total_points
                gradebook.save()
            else:
                gradebook = GradeBook(student=student,
                                     curriculum=curriculum,
                                     academic_semester=academic_semester,
                                     quarter=quarter,
                                     week=week,
                                     semester=sem,
                                     grade=total_points)
                gradebook.save()

            # freeze report
            save_report(academic_semester, student, semester=sem,week=week,quarter=quarter, report_type="gradassign")  

            # alert to both student and teacher if 2 consequent weeks with ZERO gradable assignments
            if gradebook.grade == 0 and gradebook.week != '1': 
                prev_week = GradeBook.objects.filter(student=student,
                                     curriculum=curriculum,
                                     quarter=quarter,
                                     week=str(int(week)-1),
                                     semester=sem)

                if prev_week.count() > 0 and prev_week[0].grade == 0:
                    subject, from_email, to = "%s's Risk of Truancy" % (student.get_full_name(),), 'yourepiconline@gmail.com', [
                    student.email, student.additional_email]
                    text_content ='You have not completed a gradable assignment in 2 weeks.  You are at risk of truancy and need to contact your teacher at: ' + student.teacher_email
                    html_content = "You have not completed a gradable assignment in 2 weeks.  You are at risk of truancy and need to contact your teacher at: <a href=\"mailto:%s\">%s</a>" % (student.teacher_email,student.teacher_email)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    to =  [student.teacher_email]
                    text_content = "%s has not completed a gradable assignment in two weeks.  The student received this message: \"%s\". If this is an error, please edit the gradebook and reach out to the family." % (student.get_full_name(), text_content,)
                    html_content = "%s has not completed a gradable assignment in two weeks.  The student received this message: \"%s\". If this is an error, please edit the gradebook and reach out to the family." % (student.get_full_name(), html_content,)
                    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    self.alert_email_sent = True


def save_report(academic_semester, student, semester="", week="", quarter="", report_type=""): 
    if report_type=="gradassign":
        if not week:
            raise Exception("Week is needed for gradassign report type")
        curriculum, created = Curriculum.objects.get_or_create(name='Gradable Assignments', subject='Other', grade_level='All')
        gradebook = GradeBook.objects.filter(student=student, curriculum=curriculum, quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
        attendances = Attendance.objects.filter(student=student,semester=semester,week=week,quarter=quarter,enrollment__academic_semester=academic_semester).order_by('enrollment__gradassign')

        if gradebook.count() == 0 or attendances.count() == 0:
            raise Exception("Not enought data to generate 'gradassign' report.")

        total_points = gradebook[0].grade

        data = {"total": 0, "details":{"1":[],"2":[],"3":[],"4":[],"5":[]}}
        for attendance in attendances:
            data["details"][attendance.enrollment.gradassign].append({"name": attendance.enrollment.curriculum.name,"complete":attendance.complete})
            data.update({"total":total_points})


        final_data = data
    elif report_type == "progress-weekly":
        final_data = gen_rep_data_progress_weekly(academic_semester, student, semester, quarter)
    else:
        raise Exception("Unrecognized report type. Can not generate.")


    report = StudentGradeBookReport.objects.filter(report_type=report_type,student=student,semester=semester,week=week,quarter=quarter, academic_semester=academic_semester)
    if report.count() > 0:
        report = report[0]
        report.json = json.dumps(final_data)
    else:
        report = StudentGradeBookReport(json=json.dumps(final_data), report_type=report_type, student=student,semester=semester,week=week,quarter=quarter, academic_semester=academic_semester)

    report.save()


def gen_overall_data_progress_weekly(academic_semester, student, semester, quarter):
    start_week = (int(quarter)-1)*9 + 1

    #summary per week
    overall = {'Math':[],'ELA':[],'Science':[],'Other':[],'History':[], 'GA':[]}
    for subject in ['Math','ELA','Science','Other','History']:
        enrollments = Enrollment.objects.filter(student=student, academic_semester=academic_semester, curriculum__subject=subject)
        for week in range(start_week,start_week+9): #for each week (1-9)
            gradebook = GradeBook.objects.filter(student=student, curriculum__pk__in=enrollments.values_list('curriculum',flat=True), quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
            if gradebook.count() == 0:
                overall[subject].append('')
                continue

            total = 0
            for enr in enrollments:
                gradebook = GradeBook.objects.filter(student=student, curriculum=enr.curriculum, quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
                if gradebook.count() == 1:
                    gradebook = gradebook[0]
                    total += round(gradebook.grade * (enr.weight/100))
            overall[subject].append(total)

    ga_cur, created = Curriculum.objects.get_or_create(name='Gradable Assignments', subject='Other', grade_level='All')
    for week in range(start_week,start_week+9): #for each week (1-9)
        gradebook = GradeBook.objects.filter(student=student, curriculum=ga_cur, quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
        if gradebook.count() == 0:
            overall['GA'].append('')
            continue

        total = 0
        gradebook = GradeBook.objects.filter(student=student, curriculum=ga_cur, quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
        if gradebook.count() == 1:
            gradebook = gradebook[0]
            total += gradebook.grade
        overall['GA'].append(total)

    return overall

def gen_rep_data_progress_weekly(academic_semester, student, semester, quarter): 
    start_week = (int(quarter)-1)*9 + 1
    enrollments = Enrollment.objects.filter(student=student, academic_semester=academic_semester)
    ga1 = enrollments.filter(gradassign=1)
    ga2 = enrollments.filter(gradassign=2)
    ga3 = enrollments.filter(gradassign=3)
    ga4 = enrollments.filter(gradassign=4)
    ga5 = enrollments.filter(gradassign=5)
    data = [{'raw':ga1,'curs':[]},{'raw':ga2,'curs':[]},{'raw':ga3,'curs':[]},{'raw':ga4,'curs':[]},{'raw':ga5,'curs':[]}]
    for item in data:  # for each GA
        for enr in item['raw']:  #for each enrollment under group
            cur = enr.curriculum
            cur_info = {"name":cur.name, "data":[]}
            for week in range(start_week,start_week+9): #for each week in the quarter e.g. q3 should have weeks 19-27
                gradebook = GradeBook.objects.filter(student=student, curriculum=cur, quarter=quarter, week=week, semester=semester, academic_semester=academic_semester)
                if gradebook.count() == 1:
                    gradebook = gradebook[0]
                    cur_info['data'].append({'grade':gradebook.grade, 'current':''}) # to test the render   'current':100
                else:
                    cur_info['data'].append({'grade':'', 'current':''})
            item['curs'].append(cur_info)

    overall = gen_overall_data_progress_weekly(academic_semester, student, semester, quarter)

    for item in data:
        del item['raw']

    return {'grades':data,'overall':overall}

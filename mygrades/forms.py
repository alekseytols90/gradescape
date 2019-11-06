from django import forms
from django.utils.safestring import mark_safe
from django.db.models import Count, F

from mygrades.models import (
    Student,
    Curriculum,
    Enrollment,
    Standard,
    Assignment,
    GradeBook,
    User,
    Teacher,
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
            # "date_of_birth",
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
            # "date_of_birth": "Date of Birth",
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


class CurriculumEnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "curriculum"]

        labels = {
            "student": "Add Curriculum to This Student's Gradebook (Must Be Set UP FIRST)",
            "curriculum": "Choose a Curriculum",
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance", None)
        request = kwargs.pop("request", None)
        super(CurriculumEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields["student"].queryset = Student.objects.all().order_by("last_name")
        self.fields["curriculum"].queryset = Curriculum.objects.all()


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
            # "complete",
            # "required",
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
    STATUS = [
        ("Not Assigned", "Not Assigned"),
        ("Assigned", "Assigned"),
        ("Incomplete", "Incomplete"),
        ("Exempt", "Exempt"),
    ]

    TYPE = [
        ("Repeating Weekly", "Repeating Weekly"),
        ("From Pacing List", "From Pacing List"),
    ]

    status = forms.ChoiceField(choices=STATUS, widget=forms.RadioSelect, label="What is the status of this assignment?")

    class Meta:
        model = Assignment

        fields = [
            "name",
            "description",
            "standard",
            "curriculum",
            "status",
            "type_of",
        ]

        labels = {
            "name": "Title",
            "description": "Instructions or Link",
            "standard": "OAS Standard Number",
            "curriculum": "In Which Curriculum Will This Assignment Be Included? Hold Control to DESELECT or Select "
                          "Multiple Curriculum.",
            "status": "What is the status of this assignment?",
            "type_of": "What type of assignment is this?",
        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(StudentEnrollmentForm, self).__init__(*args, **kwargs)
            self.fields["standard"].queryset = Standard.objects.all()
            self.fields["curriculum"].queryset = Curriculum.objects.all()


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
        ]
        labels = {
            "first_name": "Teacher's First Name - Capitalize First Letter ONLY",
            "last_name": "Teacher's Last Name - Capitalize First Letter ONLY",
            "email": "Teacher e-Mail",
        }

        def __init__(self, *args, **kwargs):
            instance = kwargs.pop("instance", None)
            request = kwargs.pop("request", None)
            super(TeacherModelForm, self).__init__(*args, **kwargs)

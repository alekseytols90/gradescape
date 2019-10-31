from mygrades.models import Student, Curriculum, Assignment, Standard, GradeBook
import django_filters


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


class StudentFilter(django_filters.FilterSet):
    epicenter_id = django_filters.CharFilter(
        lookup_expr="icontains", label="Epicenter ID"
    )
    first_name = django_filters.CharFilter(
        lookup_expr="icontains", label="First Name Contains(Complete Name Not Required)"
    )
    last_name = django_filters.CharFilter(
        lookup_expr="icontains", label="Last Name Contains(Complete Name Not Required)"
    )
    grade = django_filters.CharFilter(
        lookup_expr="icontains", label="Grade Level"
    )

    class Meta:
        model = Student
        fields = {}


class CurriculumFilter(django_filters.FilterSet):

    SUBJECT = [
        ("Math", "Math"),
        ("ELA", "ELA"),
        ("Science", "Science"),
        ("History", "History"),
        ("Other", "Other"),
    ]
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
    ] 
    SEMESTER = [("1", "1"), ("2", "2"), ("Full Year", "Full Year"),]
    name = django_filters.CharFilter(
        lookup_expr="icontains", label="Title"
    )
    subject = django_filters.CharFilter(
        lookup_expr="icontains", label="Subject"
    )
    grade_level = django_filters.CharFilter(
        lookup_expr="icontains", label="Grade Level"
    )
    recorded_from = django_filters.CharFilter(
        lookup_expr="icontains", label="Manual or Automatic?"
    )

    class Meta:
        model = Curriculum
        fields = {}


class StandardFilter(django_filters.FilterSet):
    GRADELEVEL = [
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
    ]
    SUBJECT = [
        ("Math", "Math"),
        ("ELA", "ELA"),
        ("Science", "Science"),
        ("History", "History"),
        ("Other", "Other"),
    ]

    subject = django_filters.CharFilter(
        lookup_expr="icontains", label="Subject")
    grade_level = django_filters.CharFilter(
        lookup_expr="icontains", label="Grade Level" )
    # name = django_filters.CharFilter(
    #     lookup_expr="icontains", label="Number Contains")
    objective_description = django_filters.CharFilter(
        lookup_expr="icontains", label="Objective Description Contains The Words")

    class Meta:
        model = Standard
        fields = {}


class AssignmentFilter(django_filters.FilterSet):
    GRADEMETHOD = [
        ("Manual", "Manual"),
        ("Automatic", "Automatic"),
        ]
    standard = django_filters.CharFilter(
        lookup_expr="icontains", label="Standard")
    curriculum = django_filters.CharFilter(
        lookup_expr="icontains", label="Curriculum")
    name = django_filters.CharFilter(
        lookup_expr="icontains", label="Title")
    tracking = django_filters.CharFilter(
        lookup_expr="icontains", label="Grading Method")

    class Meta:
        model = Assignment
        fields = {}


class GradeBookFilter(django_filters.FilterSet):
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
    # student = django_filters.CharFilter(
    #     lookup_expr="icontains", label="Student")
    # curriculum = django_filters.CharFilter(
    #     lookup_expr="icontains", label="Curriculum")
    quarter = django_filters.CharFilter(
        lookup_expr="exact", label="Quarter")
    semester = django_filters.CharFilter(
        lookup_expr="exact", label="Semester")
    week = django_filters.CharFilter(
        lookup_expr="exact", label="Week")
    grade = django_filters.CharFilter(
        lookup_expr="icontains", label="Grade")

    class Meta:
        model = GradeBook
        fields = {}
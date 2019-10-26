import json
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings


class Curriculum(models.Model):
    SUBJECT = [
        ("Math", "Math"),
        ("ELA", "ELA"),
        ("Science", "Science"),
        ("History", "History"),
        ("Other", "Other"),
    ]
    TRACKING = [
        ("Minutes", "Minutes"),
        ("Lessons", "Lessons"),
        ("Percentage Complete", "Percentage Complete"),

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
        ("High School", "High School"),
    ]

    RECORDED = [("Manual", "Manual"),
                ("Automatic", "Automatic"),
                ]

    LEVEL = [("Core", "Core"),
             ("Supplemental", "Supplemental"),
             ]

    name = models.CharField(max_length=50, null=False)
    subject = models.CharField(max_length=30, choices=SUBJECT)
    grade_level = models.CharField(max_length=20, choices=CURRICULUMGRADE, null=False)
    tracking = models.CharField(max_length=20, choices=TRACKING, null=False)
    required = models.CharField(max_length=20, null=True)
    recorded_from = models.CharField(max_length=20, choices=RECORDED, null=False)
    semesterend = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, null=True)
    password = models.CharField(max_length=50, null=True)
    loginurl = models.CharField(max_length=100, null=True)
    weight = models.IntegerField(null=True)
    level = models.CharField(max_length=20, choices=LEVEL, null=False)

    class Meta:
        ordering = ["grade_level"]
        # descending order = ["-id"]

        # unique_together = ('name', 'gradelevel', 'semester','subject',)

    def get_absolute_url(self):
        return "/curriculum/{self.id}".format(self=self)

    def get_edit_url(self):
        return "/curriculum/{self.id}/edit".format(self=self)

    def get_delete_url(self):
        return "/curriculum/{self.id}/delete".format(self=self)

    # def record_attendance_url(self):
    #     return f"/students/{self.Epicenter_ID}/record-attendance"

    def __str__(self):
        return " %s %s %s %s " % (
            self.id,
            self.name,
            self.subject,
            self.grade_level,

        )


class ScrapyItem(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    data = models.TextField()  # this stands for our crawled data
    date = models.DateTimeField(auto_now=True)

    # This is for basic and custom serialisation to return it to client as a JSON.
    @property
    def to_dict(self):
        data = {
            'data': json.loads(self.data),
            'date': self.date
        }
        return data

    def __str__(self):
        return self.unique_id


class Student(models.Model):
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

    epicenter_id = models.CharField(
        null=False, blank=False, unique=True, max_length=10
    )
    last_name = models.CharField(null=False, max_length=50)
    first_name = models.CharField(null=False, max_length=50)
    email = models.EmailField(null=False, max_length=120)
    phone_number = models.CharField(null=False, max_length=50)
    additional_email = models.EmailField(max_length=120, null=True)
    additional_phone_number = models.CharField(max_length=20, null=True)
    grade = models.CharField(max_length=20, choices=GRADELEVEL, null=False)

    def get_absolute_url(self):
        return "/students/{self.epicenter_id}".format(self=self)

    def get_edit_url(self):
        return "/students/{self.epicenter_id}/edit".format(self=self)

    def get_delete_url(self):
        return "/students/{self.epicenter_id}/delete".format(self=self)

    def __str__(self):
        return "%s %s %s %s " % (
            self.last_name,
            self.first_name,
            self.epicenter_id,
            self.grade,
        )


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_enrollment"
    )
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="curriculum_enrollment"
    )

    class Meta:
        unique_together = ("curriculum", "student")

    def get_absolute_url(self):
        return "/enrollment/{self.id}".format(self=self)

    def get_delete_url(self):
        return "/enrollment/{self.id}/delete".format(self=self)

    def get_edit_url(self):
        return "/enrollment/{self.id}/edit".format(self=self)

    def __str__(self):
        return "%s %s" % (self.student, self.id)


class Standard(models.Model):
    GRADELEVEL = [
        ("PK", "Pre-K"),
        ("K", "Kindergarten"),
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("PA", "PA"),
        ("HS", "HS"),
        ("9", "9"),
        ("A1", "A1"),
        ("10", "10"),
        ("A2", "A2"),
        ("11", "11"),
        ("G", "G"),
        ("12", "12"),
    ]
    SUBJECT = [
        ("Math", "Math"),
        ("ELA", "ELA"),
        ("Science", "Science"),
        ("History", "History"),
        ("Other", "Other"),
    ]

    grade_level = models.CharField(max_length=60, choices=GRADELEVEL)
    standard_number = models.CharField(max_length=5, null=False)
    standard_description = models.CharField(max_length=2000, null=False)
    strand_code = models.CharField(max_length=10, null=False)
    strand = models.CharField(max_length=50, null=True)
    strand_description = models.CharField(max_length=1000, null=True)
    objective_number = models.CharField(max_length=4, null=False)
    objective_description = models.CharField(max_length=1000, null=False)
    standard_code = models.CharField(max_length=20, null=False)
    subject = models.CharField(max_length=30, choices=SUBJECT)
    PDF_link = models.CharField(max_length=100, choices=SUBJECT)

    def get_absolute_url(self):
        return "/standard/{self.id}".format(self=self)

    def get_delete_url(self):
        return "/standard/{self.id}/delete".format(self=self)

    def get_edit_url(self):
        return "/standard/{self.id}/edit".format(self=self)

    def __str__(self):
        return "%s %s" % (self.strand_code, self.id)


class Assignment(models.Model):
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

    standard = models.ManyToManyField(
        Standard)
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="curriculum_assignment"
    )
    name = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=500, null=False)
    status = models.CharField(max_length=30, choices=STATUS, null=False)
    type_of = models.CharField(max_length=30, choices=TYPE, null=False)

    class Meta:
        unique_together = ("name", "curriculum",)

    def get_absolute_url(self):
        return "/assignment/{self.id}".format(self=self)

    def get_delete_url(self):
        return "/assignment/{self.id}/delete".format(self=self)

    def get_edit_url(self):
        return "/assignment/{self.id}/edit".format(self=self)

    def __str__(self):
        return "%s %s" % (self.name, self.id)


class Gradebook(models.Model):
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

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="gradebook_student"
    )
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="curriculum_grade"
    )
    complete = models.CharField(max_length=20, null=False)
    required = models.CharField(max_length=20, null=False)
    quarter = models.CharField(max_length=1, choices=QUARTER, null=False)
    week = models.CharField(max_length=2, choices=WEEK, null=False)
    grade = models.IntegerField(null=False)
    semester = models.CharField(max_length=1, choices=SEMESTER, null=False)

    class Meta:
        unique_together = ("student", "curriculum", "week", "quarter",)

    def get_absolute_url(self):
        return "/grades/{self.id}".format(self=self)

    def get_delete_url(self):
        return "/grades/{self.id}/delete".format(self=self)

    def get_edit_url(self):
        return "/grades/{self.id}/edit".format(self=self)

    def __str__(self):
        return "%s %s" % (self.name, self.id)


class PulledRecords(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    score = models.CharField(max_length=5, null=True)
    grade = models.CharField(max_length=10, null=True)
    completed = models.CharField(max_length=20, null=True)
    quiz = models.CharField(max_length=5, null=True)
    attendance = models.CharField(max_length=5, null=True)
    average_score = models.CharField(max_length=5, null=True)
    site = models.CharField(max_length=5, null=False)
    previous = models.CharField(max_length=5, null=True)
    total_time = models.CharField(max_length=5, null=True)
    presence = models.CharField(max_length=5, null=True)
    date_taken = models.DateField()
    date_pulled = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" % (self.first_name, self.last_name, self.id)

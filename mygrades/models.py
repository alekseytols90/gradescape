import json
from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=100, null=False)
    password = models.CharField(max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return " %s %s %s %s %s " % (
            self.last_name,
            self.first_name,
            self.username,
            self.password,
            self.pk,

        )


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
        ("Lessons or Quizzes", "Lessons or Quizzes"),
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

    GRADASSIGN = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
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

    # tracking = models.CharField(max_length=50, choices=TRACKING, null=False)
    # required = models.CharField(max_length=20, null=True)
    # recorded_from = models.CharField(max_length=50, choices=RECORDED, null=False)
    # semesterend = models.CharField(max_length=20, null=True)
    # username = models.CharField(max_length=50, null=True)
    # password = models.CharField(max_length=50, null=True)
    # loginurl = models.CharField(max_length=100, null=True)
    # weight = models.IntegerField(null=True)
    # level = models.CharField(max_length=20, choices=LEVEL, null=False)
    # gradassign = models.CharField(max_length=5, choices=GRADASSIGN, null=True)

    class Meta:
        ordering = ["pk"]
        # descending order = ["-pk"]

        # unique_together = ('name', 'gradelevel', 'semester','subject',)

    def get_absolute_url(self):
        return f"/curriculum/{self.pk}"

    def get_edit_url(self):
        return f"/curriculum/{self.pk}/edit"

    def get_delete_url(self):
        return f"/curriculum/{self.pk}/delete"

    # def record_attendance_url(self):
    #     return f"/students/{self.Epicenter_ID}/record-attendance"

    def __str__(self):
        return " %s %s %s %s " % (
            self.pk,
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
    curriculum = models.ForeignKey('curriculum', null=True, blank=True, on_delete=models.SET_NULL)
    teacher_email = models.CharField(max_length=75, null=False)
    birthdate = models.CharField(max_length=30, null=True)

    def get_absolute_url(self):
        return f"/students/{self.epicenter_id}"

    def get_edit_url(self):
        return f"/students/{self.epicenter_id}/edit"

    def get_delete_url(self):
        return f"/students/{self.epicenter_id}/delete"

    def get_curriculum_list_url(self):
        return f"/curriculum-schedule-detail/" + str(self.pk) + "/"

    def get_full_name(self):
        return "%s %s" % (
            self.first_name,
            self.last_name
        )

    def __str__(self):
        return "%s %s %s %s " % (
            self.last_name,
            self.first_name,
            self.epicenter_id,
            self.grade,
        )


class Enrollment(models.Model):
    GRADASSIGN = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    ]

    RECORDED = [("Manual", "Manual"),
                ("Automatic", "Automatic"),
                ]

    LEVEL = [("Core", "Core"),
             ("Supplemental", "Supplemental"),
             ]

    TRACKING = [
        ("Repeating Weekly", "Repeating Weekly"),
        ("From Pacing List", "From Pacing List"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="student_enrollment"
    )
    curriculum = models.ForeignKey(
        Curriculum, on_delete=models.CASCADE, related_name="curriculum_enrollment"
    )

    academic_semester = models.CharField(max_length=16)
    tracking = models.CharField(max_length=50, choices=TRACKING)
    required = models.CharField(max_length=20, blank=True)
    semesterend = models.DateTimeField()
    weight = models.IntegerField(null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL)
    gradassign = models.CharField(max_length=5, choices=GRADASSIGN, null=True, blank=True)
    recorded_from = models.CharField(max_length=50, choices=RECORDED)

    #IF AUTOMATIC IS SELECTED FOR "recorded_from" then ask for this information:
    username = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=50, blank=True)
    loginurl = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("curriculum", "student")

    def get_absolute_url(self):
        return f"/enrollment/{self.pk}"

    def get_delete_url(self):
        return f"/enrollment/{self.pk}/delete"

    def get_edit_url(self):
        return f"/enrollment/{self.pk}/edit"

    def __str__(self):
        if self.curriculum:
            return "%s -> %s" % (self.student, self.curriculum)
        return "%s %s" % (self.student, self.pk)


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

    grade_level = models.CharField(max_length=20, choices=GRADELEVEL)
    standard_number = models.CharField(max_length=8, null=False)
    standard_description = models.CharField(max_length=1000, null=False)
    strand_code = models.CharField(max_length=8, null=False)
    strand = models.CharField(max_length=50, null=True)
    strand_description = models.CharField(max_length=600, null=True)
    objective_number = models.CharField(max_length=2, null=False)
    objective_description = models.CharField(max_length=1000, null=False)
    standard_code = models.CharField(max_length=16, null=False)
    subject = models.CharField(max_length=30, choices=SUBJECT)
    PDF_link = models.CharField(max_length=300, null=False)

    def get_absolute_url(self):
        return f"/standard/{self.pk}"

    def get_delete_url(self):
        return f"/standard/{self.pk}/delete"

    def get_edit_url(self):
        return f"/standard/{self.pk}/edit"

    def __str__(self):
        return "%s %s %s" % (self.standard_code, self.subject, self.pk)


class Assignment(models.Model):
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
    type_of = models.CharField(max_length=30, choices=TYPE, null=False)

    class Meta:
        unique_together = ("name", "curriculum", "description")

    def get_absolute_url(self):
        return f"/assignment/{self.id}"

    def get_delete_url(self):
        return f"/assignment/{self.id}/delete"

    def get_edit_url(self):
        return f"/assignment/{self.id}/edit"

    def __str__(self):
        return "%s %s" % (self.name, self.id)

class StudentAssignment(models.Model):
    STATUS = [
        ("Not Assigned", "Not Assigned"),
        ("Assigned", "Assigned"),
        ("Incomplete", "Incomplete"),
        ("Exempt", "Exempt"),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True) #TODO: remove null=True
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS, null=False)
    shown_in_weekly = models.BooleanField(default=False)

    # not used yet
    active = models.BooleanField(default=False)
    late = models.BooleanField(default=0)
    registered_datetime = models.DateTimeField(auto_now=True)
    submission_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Student Assignments"

    def save(self, *args, **kwargs):
        if self.status == "Assigned":
            self.submission_date = timezone.now()+timezone.timedelta(days=7)
            self.active = True
        super(StudentAssignment, self).save(*args, **kwargs)

    def __str__(self):
        return "%s -> %s" % (str(self.student), self.assignment.name)


class GradeBook(models.Model):
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
        Curriculum, on_delete=models.CASCADE, related_name="curriculum_grade",
    )
    complete = models.CharField(max_length=20, null=False, default='true')
    required = models.CharField(max_length=20, null=False, default='true')
    quarter = models.CharField(max_length=1, choices=QUARTER, null=False)
    week = models.CharField(max_length=2, choices=WEEK, null=False)
    grade = models.IntegerField(null=False)
    semester = models.CharField(max_length=1, choices=SEMESTER, null=False)

    class Meta:
        unique_together = ("student", "curriculum", "week", "quarter",)

    def get_absolute_url(self):
        return f"/grades/{self.pk}"

    def get_delete_url(self):
        return f"/grades/{self.pk}/delete"

    def get_edit_url(self):
        return f"/grades/{self.pk}/edit"

    def __str__(self):
        return "%s %s" % (self.pk, self.grade)


class Teacher(models.Model):
    # student = models.ForeignKey(
    #     Student, on_delete=models.CASCADE, related_name="student_teacher")
    first_name = models.CharField(max_length=75, null=False)
    last_name = models.CharField(max_length=75, null=False)
    email = models.CharField(max_length=75, null=False)

    class Meta:
        unique_together = ("first_name", "last_name", "email")

    def get_absolute_url(self):
        return f"/teachers/{self.pk}"

    def get_delete_url(self):
        return f"/teachers/{self.pk}/delete"

    def get_edit_url(self):
        return f"/teachers/{self.pk}/edit"

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.last_name, self.first_name, self.email)


class ExemptAssignment(models.Model):
    class Meta:
        verbose_name_plural = "Exempt Assignments"

    student = models.ForeignKey('student', null=True, blank=True, on_delete=models.SET_NULL)
    assignments = models.ManyToManyField('assignment', null=True, blank=True)

    def __str__(self):
        return "# {} - {}".format(self.pk, self.student)

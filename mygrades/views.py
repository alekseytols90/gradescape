from gradebook.admin.placeholderadmin import FrontendEditableAdminMixin
from django.shortcuts import render, redirect, render_to_response
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from itertools import chain
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.conf import settings
from datetime import date
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST, require_http_methods
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.db.models import Count
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core import mail
from django.utils.html import strip_tags
from django.urls import reverse
from django.http import HttpResponseRedirect
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
#from mygrades.utils import URLUtil
#from mygrades.models import ScrapyItem
import csv, io
from django.contrib import messages
from django.contrib.auth.decorators import permission_required


# connect scrapyd service
#scrapyd = ScrapydAPI('http://localhost:6800')

from mygrades.models import (
    Student,
    Curriculum,
    Enrollment,
    Standard,
    Assignment,
    Gradebook,
    )


from mygrades.filters import (
    StudentFilter,
    CurriculumFilter,
    AssignmentFilter,
    StandardFilter,
    GradebookFilter,

    )

from mygrades.forms import (
    CurriculumEnrollmentForm,
    StudentModelForm,
    AssignmentCreateForm,
    StandardSetupForm,
    CustomCurriculumSetUpForm,
    RecordGradeForm,
    SendPacingGuideForm,
    )

@login_required
def send_pacing_guide(request):
    form = SendPacingGuideForm(request.POST or None, request=request)
    if form.is_valid():
        student = form.cleaned_data["student"]
        first_name = form.cleaned_data["student"].first_name
        last_name = form.cleaned_data["student"].last_name

        subject, from_email, to = 'Your Assignments For This Week', 'tynercreeksoftware@gmail.com', [form.cleaned_data["student"].email, form.cleaned_data["student"].additional_email]
        text_content = 'Your Most Updated Epic Live Schedule.  You may need to open this in a different browser if you do not see it here.'
        html_content = render_to_string('mail_pacing_guide.html', context=form.cleaned_data)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    else:
        form = SendPacingGuideForm(request=request)
    form = SendPacingGuideForm(request=request)
    my_title = "Send a Student His or Her Assignments for This Week"
    template_name = "send_pacing_guide_form.html"
    context =  {"title":my_title, "form": form, 'data': request.POST} 
    return render(request, template_name, context)

# def is_valid_url(url):
#     validate = URLValidator()
#     try:
#         validate(url) # check if url format is valid
#     except ValidationError:
#         return False
#     return True

# @csrf_exempt
# @require_http_methods(['POST', 'GET']) # only get and post
# def crawl(request):
#     # Post requests are for new crawling tasks
#     if request.method == 'POST':

#         url = request.POST.get('url', None) # take url comes from client. (From an input may be?)

#         if not url:
#             return JsonResponse({'error': 'Missing  args'})

#         if not is_valid_url(url):
#             return JsonResponse({'error': 'URL is invalid'})

#         domain = urlparse(url).netloc # parse the url and extract the domain
#         unique_id = str(uuid4()) # create a unique ID.

#         # This is the custom settings for scrapy spider.
#         # We can send anything we want to use it inside spiders and pipelines.
#         # I mean, anything
#         settings = {
#             'unique_id': unique_id, # unique ID for each record for DB
#             'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
#         }

#         # Here we schedule a new crawling task from scrapyd.
#         # Notice that settings is a special argument name.
#         # But we can pass other arguments, though.
#         # This returns a ID which belongs and will be belong to this task
#         # We are goint to use that to check task's status.
#         task = scrapyd.schedule('default', 'gradebook',
#             settings=settings, url=url, domain=domain)

#         return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started' })

#     # Get requests are for getting result of a specific crawling task
#     elif request.method == 'GET':
#         # We were passed these from past request above. Remember ?
#         # They were trying to survive in client side.
#         # Now they are here again, thankfully. <3
#         # We passed them back to here to check the status of crawling
#         # And if crawling is completed, we respond back with a crawled data.
#         task_id = request.GET.get('task_id', None)
#         unique_id = request.GET.get('unique_id', None)
#         print(task_id, unique_id)

#         if not task_id or not unique_id:
#             return JsonResponse({'error': 'Missing args'})

#         # Here we check status of crawling that just started a few seconds ago.
#         # If it is finished, we can query from database and get results
#         # If it is not finished we can return active status
#         # Possible results are -> pending, running, finished
#         status = scrapyd.job_status('default', task_id)
#         if status == 'finished':
#             try:
#                 # this is the unique_id that we created even before crawling started.
#                 item = ScrapyItem.objects.get(unique_id=unique_id)
#                 return JsonResponse({'data': item.to_dict['data']})
#             except Exception as e:
#                 return JsonResponse({'error': str(e)})
#         else:
#             return JsonResponse({'status': status})



# Teacher account will be set up when he or she pays.

# First step:  register students.

# Model is set up.  Needs to link to available curriculum.

# You will be able to edit this (number of weeks to complete work)

# Import curriculum assignments into the Curriculum database.

# When registering students, select curriculum and the weight of each.

# Teacher has choices of grading curriculum:  number of lessons, minutes per day, minutes per weeks

# After scraping:

# Report of incomplete assignments per students
# Top Student in each curriculum
# %complete of total
# Who is ahead of pace
# Prepare schedules for the next week or two weeks, up to Teacher
# Teachers suggests day of the week for each curric item
# Give a standards mastered checklist to teacher each week from pacing guide

# Must upload CSV list into curric database....
@login_required
def standard_upload(request):
    template = "standard_upload.html"
    prompt = {
        'order':"The columns should be: Grade, Standard Number, Standard Description, Strand Code, Strand, Strand Description, Objective Number, Objective Description, Standard Code, and Subject."
    }
    if request.method == "GET":
        return render (request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")

    data_set = csv_file.read().decode("UTF-8")
    #for row in data_set:
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = Standard.objects.update_or_create(
            grade_level = column[0],
            standard_number = column[1],
            standard_description = column[2],
            strand_code = column[3],
            strand = column[4],
            strand_description = column[5],
            objective_number = column[6],
            objective_description = column[7],
            standard_code = column[8],
            PDF_link = column [9], 
            subject= column[10]
            )
    return redirect ("/standard")
    context = {}
    return render(request, template, context)

@login_required
def curriculum_upload(request):
    template = "curriculum_upload.html"
    prompt = {
        'order':"The columns should be: Name, Subject, Grade Level, Tracking (Minutes, Lessons, Percent Complete), Recorded From (Manual/Automatic), Username, Password, Login URL."
    }
    if request.method == "GET":
        return render (request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")

    data_set = csv_file.read().decode("UTF-8")
    #for row in data_set:
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = Curriculum.objects.update_or_create(
            name = column[0],
            subject = column[1],
            grade_level = column[2],
            tracking = column[3],
            recorded_from = column[4],
            semesterend = column[5],
            username = column[6],
            password = column[7],
            loginurl = column[8],
            )
    return redirect ("/curriculum")
    context = {}
    return render(request, template, context)

@login_required
def assignment_upload(request):
    template = "assignment_upload.html"
    prompt = {
        'order':"The columns should be: Name, Instructions or Link, Curriculum, Standard."
    }
    if request.method == "GET":
        return render (request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")

    data_set = csv_file.read().decode("UTF-8")
    #for row in data_set:
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        obj_c, curriculum = Curriculum.objects.update_or_create(...)
        obj_a, created = Assignment.objects.update_or_create(
            name = column[1],
            description = column [2],
            curriculum=obj_c,
            standard = column [3],
            )
        
    return redirect ("/assignment")
    context = {}
    return render(request, template, context)

@login_required
def student_setup_view(request):
    my_title = "Register a Student"
    form = StudentModelForm(request.POST or None)
    if form.is_valid():
        form.cleaned_data["additional_email"] = form.cleaned_data["additional_email"].lower()
        form.cleaned_data["email"] = form.cleaned_data["email"].lower()
        form.save()
        # emailto = [request.user.email]
        # send_mail(
        #     "Student Registration Confirmation",
        #     "You successfully registered {0} {1} in the Epic Live system.  \nIf you are the Epic Live Teacher and you checked the confirmation box, you may receive more than one eMail.  That is normal.  \nHere is what was received: \nEpicenter ID: {2} \neMail: {3} \nPhone: {5} \nAlternate eMail: {4} \nAlternate Phone: {6} \nStudent is Enrolled in Grade: {7} \nReading RIT Level: {8} \nMath RIT Level: {9} \nBirthdate: {10}  \nPrimary Teacher eMail: {11}  \n Primaary Teacher: {12} {13} \nThe Primary Teacher may Edit {0} {1}'s Personal Information in Epic Live Services if it is incorrect here:  www.epicliveservices.com/students. \n\nCongratulations!  The Primary Teacher may now enroll them in Epic Live Courses.  They should start by looking through the Course Catalog for Teachers here:  www.epicliveservices.com/courses . Making a pencil/paper list of COURSE NUMBERS for each student will be most helpful in the enrollment process.\nWhen they are ready, they will enroll the student in the selected courses here:  www.epiccliveservices.com/enroll-student.\n\nPLEASE NOTE:  Students may NOT enter a Google classroom without using their Epic student eMail address.  If you did not provide this address, the Epic Live teacher is unable invite them to join the classroom.  Please go back and update your student's information now, as many teachers utilize Google classroom.".format(
        #         form.cleaned_data["first_name"], form.cleaned_data["last_name"], form.cleaned_data["epicenter_id"], form.cleaned_data["email"], form.cleaned_data["additional_email"], form.cleaned_data["phone_number"], form.cleaned_data["additional_phone_number"], form.cleaned_data["grade"], form.cleaned_data["reading_RIT_level"], form.cleaned_data["math_RIT_level"], form.cleaned_data["date_of_birth"], form.cleaned_data["regular_teacher_email"], form.cleaned_data["regular_teacher_first_name"], form.cleaned_data["regular_teacher_last_name"],
        #     ),
        #     "epiclive@epiccharterschools.org",
        #     emailto,
        #     fail_silently=True,
        # )
        return redirect ("/students")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)

@login_required
def student_list_view(request):
    my_title = "Your Students"
    qs = Student.objects.all()
    student_filter = StudentFilter(request.GET, queryset=qs)
    template_name = "student_list_view.html"
    context = {"object_list": student_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def student_update_view(request, epicenter_id):
    obj = get_object_or_404(Student, epicenter_id=epicenter_id)
    form = StudentModelForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.cleaned_data["email"] = form.cleaned_data["email"].lower()
        form.cleaned_data["additional_email"] = form.cleaned_data["additional_email"].lower()
        form.save()
        return redirect("/students")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.epicenter_id}", "form": form}
    return render(request, template_name, context)

@staff_member_required
def student_delete_view(request, epicenter_id):
    obj = get_object_or_404(Student, epicenter_id=epicenter_id)
    template_name = "student_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/students")
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def curriculum_create_view(request):
    my_title = "Create a Custom Curriculum"
    form = CustomCurriculumSetUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/curriculum")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)

@login_required
def curriculum_list_view(request):
    my_title = "Curriculum Choices"
    qs = Curriculum.objects.all()
    curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "curriculum_list_view.html"
    context = {"object_list": curriculum_filter, "title": my_title}
    #context = {"title": my_title}
    return render(request, template_name, context)


@login_required
def curriculum_update_view(request, id):
    obj = get_object_or_404(Curriculum, id=id)
    form = CustomCurriculumSetUpForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/curriculum")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.id}", "form": form}
    return render(request, template_name, context)



@staff_member_required
def curriculum_delete_view(request, epicenter_id):
    obj = get_object_or_404(Curriculum, id=id)
    template_name = "curriculum_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/curriculum")
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def standard_create_view(request):
    my_title = "Setup a New Standard"
    form = StandardSetupForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/standard")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)

@login_required
def standard_list_view(request):
    my_title = "Standards"
    qs = Standard.objects.all()
    standard_filter = StandardFilter(request.GET, queryset=qs)
    template_name = "standard_list_view.html"
    context = {"object_list": standard_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def standard_update_view(request, id):
    obj = get_object_or_404(Standard, id=id)
    form = StandardSetupForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        form = StandardSetupForm()
    template_name = "form.html"
    context = {"title": f"Change Information for: {obj.standard_code}", "form": form}
    return render(request, template_name, context)

@staff_member_required
def standard_delete_view(request, id):
    obj = get_object_or_404(Standard, id=id)
    template_name = "standard_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/standard")
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def assignment_create_view(request):
    my_title = "Setup a New Assignment"
    form = AssignmentCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/assignment")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)

@login_required
def assignment_list_view(request):
    my_title = "Assignments"
    qs = Assignment.objects.all()
    assignment_filter = AssignmentFilter(request.GET, queryset=qs)
    template_name = "assignment_list_view.html"
    context = {"object_list": assignment_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def assignment_update_view(request, id):
    obj = get_object_or_404(Assignment, id=id)
    form = AssignmentCreateForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/curriculum")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.id}", "form": form}
    return render(request, template_name, context)




@staff_member_required
def assignment_delete_view(request, epicenter_id):
    obj = get_object_or_404(Assignment, id=id)
    template_name = "assignment_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/assignment")
    context = {"object": obj}
    return render(request, template_name, context)


@login_required
def enroll_student_view(request):
    qs = Curriculum.objects.all()
    my_title = (
        "Add a Curriculum to Student Gradebook"
    )
    form = CurriculumEnrollmentForm(request.POST or None, request=request)
    if form.is_valid():
        form.save()
    template_name = "enroll_student_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)


@login_required
def grades_record_view(request):
    my_title = "Record Grades"
    form = RecordGradeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("/grades")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)

@login_required
def grades_list_view(request):
    my_title = "Gradebook"
    qs = Gradebook.objects.all()
    gradebook_filter = GradebookFilter(request.GET, queryset=qs)
    template_name = "gradebook_list_view.html"
    context = {"object_list": gradebook_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def grades_update_view(request, id):
    obj = get_object_or_404(Student, id=id)
    form = RecordGradeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/students")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.id}", "form": form}
    return render(request, template_name, context)


@staff_member_required
def grades_delete_view(request, epicenter_id):
    obj = get_object_or_404(Gradebook, id=id)
    template_name = "gradebook_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/grades")
    context = {"object": obj}
    return render(request, template_name, context)


@login_required
def student_curriculum_schedule(request):
    my_title = "Student Curriculum Enrollment"
    qs = Student.objects.all()
    curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "student_curriculum_view.html"
    context = {"object_list": curriculum_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def curriculum_assignment_list(request):
    my_title = "Assignments in Curriculum"
    qs = Curriculum.objects.all()
    curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "curriculum_assignment_view.html"
    context = {"object_list": curriculum_filter, "title": my_title}
    return render(request, template_name, context)
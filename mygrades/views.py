import csv
import io
from datetime import datetime, timedelta
from dateutil import rrule
from urllib.parse import urlparse
from uuid import uuid4

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q
from django.forms import formset_factory
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic.edit import UpdateView
from django.utils import timezone
from django.utils.safestring import mark_safe
from scrapyd_api import ScrapydAPI

from rest_framework.decorators import api_view
from rest_framework.response import Response

from mygrades.crawler import *
from mygrades.filters import (
    StudentFilter,
    CurriculumFilter,
    EnrollmentFilter,
    AssignmentFilter,
    StandardFilter,
    GradeBookFilter,
    TeacherFilter,
    StudentAssignmentFilter,

)
from mygrades.forms import (
    CurriculumEnrollmentForm,
    CurriculumEnrollmentUpdateForm,
    StudentModelForm,
    AssignmentCreateForm,
    StandardSetupForm,
    StudentAssignmentForm,
    CustomCurriculumSetUpForm,
    RecordGradeForm,
    SendPacingGuideForm,
    TeacherModelForm,
    WeightForm,
    BaseWFSet,
    StatusChangeForm,
    generate_semester_choices,
    get_active_sems,
    distribute_weights_for_sem,
)
from mygrades.models import (
    Student,
    Curriculum,
    Enrollment,
    Standard,
    Assignment,
    StudentAssignment,
    GradeBook,
    ExemptAssignment,
    Teacher,
    
)

@login_required
def home_page_view(request):
    if request.user.groups.filter(name="Student").count() > 0:
        student = get_object_or_404(Student, email=request.user.email)
        teacher =Teacher.objects.get(email=student.teacher_email)
    else:
        return render(request, "index.html")
    template_name = "index.html"
    context = {"object": student}
    return render(request, template_name, context)

def tutorials_page_view(request):
    my_title = "How To Videos"
    context = {"title": my_title}
    return render(request, "tutorials.html", {})


@login_required
def login_help(request):
    my_title = "Login and Website Help"
    # template_name = "login_help.html"
    context = {"title": my_title}
    return render(request, "login_help.html",{})

    # def home(response):
    # return render(response, "main/home.html", {})


@login_required
def user_upload(request):
    template = "user_upload.html"
    prompt = {
        'order': "The columns should be: First Name, Last Name, eMail Address, Password, Group, Staff?, Active?, Superuser?, Date Joined, Last Login."
    }
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    io_string = io.StringIO(data_set)

    # header count check
    header = next(io_string)
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) != 5:
        messages.error(request, "Make sure table consists of 10 columns. %s" % prompt['order'])
        return render(request, template)

    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        _, created = Teacher.objects.update_or_create(
            first_name=clear_field(column[0]),
            last_name=clear_field(column[1]),
            email=clear_field(column[2]),
            password=clear_field(column[3]),
            groups=clear_field(column[4]),
            # is_staff=clear_field(column[5]),
            # is_active=clear_field(column[6]),
            # is_superuser=clear_field(column[7]),
            # date_joined=clear_field(column[8]),
            # last_login=clear_field(column[9]),
        )

    return redirect("/")

  
@login_required
def teacher_upload(request):
    template = "teacher_upload.html"
    prompt = {
        'order': "The columns should be: First Name, Last Name, eMail Address, Syllabus Link, Zoom Link."
    }
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    io_string = io.StringIO(data_set)

    # header count check
    header = next(io_string)
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) != 11:
        messages.error(request, "Make sure header consists of 5 items. %s" % prompt['order'])
        return render(request, template)

    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        _, created = Teacher.objects.update_or_create(
            first_name=clear_field(column[0]),
            last_name=clear_field(column[1]),
            email=clear_field(column[2]),
            syllabus=clear_field(column[3]),
            zoom=clear_field(column[4])
        )

    return redirect("/teachers")


@csrf_exempt
def user_login(request):
    # form =  LoginForm(request)
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_active:
                return HttpResponseRedirect("/")
            else:
                return HttpResponse("Your account is inactive.")
        else:
            return HttpResponse("Invalid Login Credentials,  <a href='/login'>Try Again</>")

    # else:
    #     form = LoginForm(request=request)
    # form = LoginForm(request=request)
    # my_title = "Log In"
    # template_name = "login.html"
    # context =  {"title":my_title, "form": form}
    return render_to_response('login.html')


def user_logout(request):
    # form =  LoginForm(request)
    username = ""
    password = ""
    return HttpResponse("<a href='/login'>Log In</>")


# connect scrapyd service
scrapyd = ScrapydAPI('http://localhost:6800')


@login_required
def send_pacing_guide(request):
    form = SendPacingGuideForm(request.POST or None, request=request)
    if form.is_valid():
        student = form.cleaned_data["student"]
        first_name = form.cleaned_data["student"].first_name
        last_name = form.cleaned_data["student"].last_name

        subject, from_email, to = 'Your Assignments For This Week', 'yourepiconline@gmail.com', [
            form.cleaned_data["student"].email, form.cleaned_data["student"].additional_email]
        text_content = 'Your most updated list of weekly assignments.  You may need to open this in a different browser if you do not see it here. '
        html_content = render_to_string('mail_pacing_guide.html', context=form.cleaned_data)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    else:
        form = SendPacingGuideForm(request=request)
    form = SendPacingGuideForm(request=request)
    my_title = "E-mail Student Weekly Assignment List"
    template_name = "send_pacing_guide_form.html"
    context = {"title": my_title, "form": form, 'data': request.POST}
    return render(request, template_name, context)


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True


def clear_field(content):
    return content.strip() if content else ""

@csrf_exempt
@require_http_methods(['POST', 'GET'])  # only get and post
def crawl(request):
    if request.method == 'POST':
        url = request.POST.get('www.google.com', None)
        if not url:
            return JsonResponse({'error': 'Missing  args'})
        if not is_valid_url(url):
            return JsonResponse({'error': 'URL is invalid'})

        domain = urlparse(url).netloc  # parse the url and extract the domain
        unique_id = str(uuid4())  # create a unique ID.

        # This is the custom settings for scrapy spider.
        # We can send anything we want to use it inside spiders and pipelines.
        # I mean, anything
        settings = {
            'unique_id': unique_id,  # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # Here we schedule a new crawling task from scrapyd.
        # Notice that settings is a special argument name.
        # But we can pass other arguments, though.
        # This returns a ID which belongs and will be belong to this task
        # We are goint to use that to check task's status.
        task = scrapyd.schedule('default', 'gradebook',
                                settings=settings, url=url, domain=domain)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    # Get requests are for getting result of a specific crawling task
    elif request.method == 'GET':
        # We were passed these from past request above. Remember ?
        # They were trying to survive in client side.
        # Now they are here again, thankfully. <3
        # We passed them back to here to check the status of crawling
        # And if crawling is completed, we respond back with a crawled data.
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)
        print(task_id, unique_id)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        # Here we check status of crawling that just started a few seconds ago.
        # If it is finished, we can query from database and get results
        # If it is not finished we can return active status
        # Possible results are -> pending, running, finished
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                item = ScrapyItem.objects.get(unique_id=unique_id)
                return JsonResponse({'data': item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})


@login_required
def crawler(request, site_name=None):
    template_name = "report_page.html"
    if site_name == 'Dreambox':
        response = get_dream_box_data()
    elif site_name == 'Epic Live Attendance':
        response = get_epiclive_data()
    elif site_name == 'Reading Eggs':
        response = get_reading_eggs_data()
    elif site_name == 'Compass':
        response = get_learning_wood_data()
        print('response => \n', response)
    elif site_name == 'MyON':
        response = get_my_on_data()
    elif site_name == 'all':
        response = get_all_data()
    else:
        response = {"status_code": "204", 'message': "Site not handled, Invalid URL"}

    if request.method == 'POST':
        print('site name => ', site_name)
        if site_name == 'all':
            for resp in response['data']:
                save_grade(request, resp, resp['site'])
        else:
            save_grade(request, response, site_name)
        # return redirect('/grades')

    return render(request, template_name, response)


def get_registrar(response):
    presents = []
    for i in response['data'].values():
        if i['attendance'] == 'Present':
            presents.append(i['epic_id'])
    return collections.Counter(presents)


def save_grade(request, response, site_name):
    registered = []
    if site_name == 'Epic Live Attendance':
        registrar = get_registrar(response)
    for key, value in response['data'].items():
        try:
            student = Student.objects.filter(first_name__exact=value['first_name']).filter(
                last_name__exact=value['last_name'])[0]
            curriculum_name = site_name.replace('Attendance', '').lower().replace(' ', '')
            print(curriculum_name)
            student_enrollment = Enrollment.objects.filter(student=student)
            # student_curriculum_id = student_enrollment.values_list('curriculum_id', flat=True)[0]
            curriculum = Curriculum.objects.filter(name__icontains=curriculum_name)[0]
            print(curriculum)
            # curriculum = Curriculum.objects.filter(id=student_curriculum_id)[0]
            if student_enrollment:
                print(student)
                if curriculum:
                    form_data = request.POST
                    if site_name == 'Epic Live Attendance':
                        epic_id = value['epic_id']
                        grade = registrar[epic_id] if registrar[epic_id] else 0
                    elif site_name == 'Compass':
                        grade = value['score']
                    elif site_name == 'MyON':
                        grade = value['previous']
                    elif site_name == 'Reading Eggs':
                        grade = value['attendance']
                    else:
                        grade = value['lesson_completed']
                    if student not in registered:
                        GradeBook.objects.create(student=student,
                                                 curriculum=curriculum,
                                                 quarter=form_data['quarter'][0],
                                                 week=form_data['week'],
                                                 semester=form_data['semester'],
                                                 grade=grade)
                        if site_name == 'Epic Live Attendance':
                            registered.append(student)
        except IndexError:
            print('no such student')
            pass


@login_required
def standard_upload(request):
    template = "standard_upload.html"
    prompt = {
        'order': "The columns should be: Grade, Standard Number, Standard Description, Strand Code, Strand, Strand Description, Objective Number, Objective Description, Standard Code, and Subject."
    }
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    io_string = io.StringIO(data_set)

    # header count check
    header = next(io_string)
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) != 11:
        messages.error(request, "Make sure table consists of 11 columns. %s" % prompt['order'])
        return render(request, template)

    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        _, created = Standard.objects.update_or_create(
            grade_level=clear_field(column[0]),
            standard_number=clear_field(column[1]),
            standard_description=clear_field(column[2]),
            strand_code=clear_field(column[3]),
            strand=clear_field(column[4]),
            strand_description=clear_field(column[5]),
            objective_number=clear_field(column[6]),
            objective_description=clear_field(column[7]),
            standard_code=clear_field(column[8]),
            PDF_link=clear_field(column[9]),
            subject=clear_field(column[10])
        )

    return redirect("/standard")


@login_required
def curriculum_upload(request):
    template = "curriculum_upload.html"
    prompt = {
        'order':"The columns should be: Name, Subject, Grade Level." 
        #, Tracking (Minutes, Lessons, Percent Complete)," 
        #"Recorded From (Manual/Automatic), Username, Password, Login URL."
    }
    if request.method == "GET":
        return render (request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    io_string = io.StringIO(data_set)

    # header count check
    header = next(io_string)
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) != 3:
        messages.error(request, "Make sure table consists of 3 columns. %s" % prompt['order'])
        return render(request, template)

    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        _, created = Curriculum.objects.update_or_create(
            name=clear_field(column[0]),
            subject=clear_field(column[1]),
            grade_level=clear_field(column[2]),
            # tracking=tracking,
            # recorded_from=recorded_time,
            # username=username,
            # password=password,
            # loginurl=login_url
        )

    return redirect ("/curriculum")


@login_required
def assignment_upload(request):
    template = "assignment_upload.html"
    prompt = {
        'order': "The columns should be : Grade, Curriculum Name, Subject, Standard Code, Description, Name"
    }
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    # header count check
    header = data_set.splitlines()[0]
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) < 6:
        messages.error(request, "Make sure table consists of 6 columns. %s" % prompt['order'])
        return render(request, template)

    dict_reader = csv.DictReader(data_set.splitlines(), delimiter=",", quotechar='"', dialect=csv.excel_tab)
    counter = 2
    for row in dict_reader:
        row = dict(row)
        # filtering the row values
        grade_level = row['Grade'].replace(',', "") if type(row['Grade']) == str else None
        subject = row['Subject'].replace(',', "") if isinstance(row['Subject'], str) else None
        name = row['Name'].replace(',', "") if isinstance(row['Name'], str) else None
        standard = row['Standard'].replace(',', '') if isinstance(row['Standard'], str) else None
        curriculum = row['Curriculum'].replace(',', '') if isinstance(row['Curriculum'], str) else None
        #status = row['Status'].replace(',', '') if isinstance(row['Status'], str) else None
        description = row['Description'].replace(',', '') if isinstance(row['Description'], str) else None
        standards = Standard.objects.filter(standard_code=standard,
                                            grade_level=grade_level,
                                            subject=subject)
        curriculum = Curriculum.objects.filter(grade_level=grade_level,
                                               subject=subject,
                                               name=curriculum)
        #print("curriculum is %s" % curriculum)
        if curriculum:
            try:
                assignment, created = Assignment.objects.get_or_create(name=name,
                                                                       #status=status,
                                                                       description=description,
                                                                       curriculum=curriculum.first(),
                                                                       type_of="Repeating Weekly")
                assignment.standard.add(*standards.values_list('id', flat=True))
            except Exception as e:
                messages.error(request, "Fix error in row number %s :: <br/> %s" % (counter, e))
                return render(request, template)
        else:
            messages.error(request,
                           "The curriculum in row number %s does not exist.  You may import it or set it up manually." % counter)
            return render(request, template)
        counter += 1

    return redirect("/assignment")

@login_required
def student_upload(request):
    template = "student_upload.html"
    prompt = {
        'order': "The columns should be: First Name, Last Name, Primary email, Second email (not required), Primary phone, Second phone (not required), Grade, Epicenter ID, Birthdate, and Teacher eMail Address." 
    }
    if request.method == "GET":
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, "Only CSV files may be uploaded.")
        return render(request, template)

    data_set = ""
    try:
        data_set = csv_file.read().decode("UTF8")
    except Exception as e:
        csv_file.seek(0)
        data_set = csv_file.read().decode("ISO-8859-1") 

    io_string = io.StringIO(data_set)

    # header count check
    header = next(io_string)
    header_clean = [x for x in  header.split(',') if not x in ['','\r\n','\n']]
    if len(header_clean) != 9:
        messages.error(request, "Make sure header consists of 9 elements. %s" % prompt['order'])
        return render(request, template)

    for column in csv.reader(io_string, delimiter=',', quotechar='"'):
        _, created = Student.objects.update_or_create(
            first_name=clear_field(column[0]),
            last_name=clear_field(column[1]),
            email=clear_field(column[2]),
            additional_email=clear_field(column[3]),
            phone_number=clear_field(column[4]),
            additional_phone_number=clear_field(column[5]),
            grade=clear_field(column[6]),
            epicenter_id=clear_field(column[7]),
            birthdate=clear_field(column[8]),
            teacher_email=clear_field(column[9]),
        )

    return redirect("/students")


@login_required
def student_setup_view(request):
    my_title = "Register a Student"
    form = StudentModelForm(request.POST or None)
    if form.is_valid():
        form.cleaned_data["additional_email"] = form.cleaned_data["additional_email"].lower()
        form.cleaned_data["email"] = form.cleaned_data["email"].lower()
        form.save()
        emailto = [request.user.email]
        send_mail(
            "Student Setup Confirmation",
            "You successfully registered {0} {1} in your online system.\nHere is what was received: \nEpicenter "
            "ID: {2} \neMail: {3} \nPhone: {5} \nAlternate eMail: {4} \nAlternate Phone: {6} \nStudent is Enrolled in "
            "Grade: {7}\nThe next step is to add some curriculums for grade tracking and pacing guides.".format(
                form.cleaned_data["first_name"], form.cleaned_data["last_name"], form.cleaned_data["epicenter_id"],
                form.cleaned_data["email"], form.cleaned_data["additional_email"], form.cleaned_data["phone_number"],
                form.cleaned_data["additional_phone_number"], form.cleaned_data["grade"],
            ),
            "yourepiconline@gmail.com",
            emailto,
            fail_silently=True,
        )
        return redirect("/students")
    template_name = "basic_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)


def teacher_setup_view(request):
    my_title = "Setup a Teacher"
    form = TeacherModelForm(request.POST or None)
    if form.is_valid():
        form.cleaned_data["email"] = form.cleaned_data["email"].lower()
        form.save()
        return redirect("/teachers")
    template_name = "teacher_setup_view.html"
    context = {"form": form, "title": my_title}
    return render(request, template_name, context)


@login_required
def student_list_view(request):
    my_title = "Your Students"
    qs = Student.objects.filter(teacher_email=request.user.email)
    student_filter = StudentFilter(request.GET, queryset=qs)

    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)

    template_name = "student_list_view.html"
    context = {"object_list": object_list, "filter": student_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def teacher_list_view(request):
    my_title = "Teachers"
    qs = Teacher.objects.all()
    teacher_filter = TeacherFilter(request.GET, queryset=qs)
    template_name = "teacher_list_view.html"
    context = {"object_list": teacher_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def teacher_update_view(request, id):
    obj = get_object_or_404(Teacher, id=id)
    form = TeacherModelForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.cleaned_data["email"] = form.cleaned_data["email"].lower()
        form.save()
        return redirect("/teachers")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.firstname}", "form": form}
    return render(request, template_name, context)

@login_required
def curriculum_assignments_included_view(request, id):
    #qs = Assignment.objects.all()
    obj = get_object_or_404(Curriculum, id=id)
    #curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "curriculum_assignments_included_view.html"
    context = {"title": f"Assignments in {obj.name}"}
    # context = {"title": my_title}
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
def teacher_delete_view(request, id):
    obj = get_object_or_404(Teacher, id=id)
    template_name = "teacher_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/teachers")
    context = {"object": obj}
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
def curriculum_detail_view(request, id):
    my_title = "Curriculum Details"
    qs = Assignment.objects.filter(curriculum__pk=id)
    assignment_filter = AssignmentFilter(request.GET, queryset=qs)
    template_name = "assignment_list_view.html"
    context = {"object_list": assignment_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def curriculum_list_view(request):
    my_title = "Curriculum Choices - Missing One? Look on Your Home Page!"
    qs = Curriculum.objects.all()
    curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "curriculum_list_view.html"
    context = {"object_list": curriculum_filter, "title": my_title}
    # context = {"title": my_title}
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
    my_title = "Standards - Spot a mistake or missing one? Look on your Home page to contact us!"
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
def student_assignment_list_view(request,sid,cid):
    my_title = "Student Curriculum Assignment Detail"
    student = get_object_or_404(Student, pk=sid)
    curriculum = get_object_or_404(Curriculum, pk=cid)
    assignments = StudentAssignment.objects.filter(student=student, assignment__curriculum=curriculum)
    SAFormSet = inlineformset_factory(Student, StudentAssignment, extra=0, can_delete=False, form=StudentAssignmentForm)
    formset = SAFormSet(instance=student, queryset=assignments)

    if request.method == "POST":
        formset = SAFormSet(request.POST, instance=student, queryset=assignments)
        if formset.is_valid():
            formset.save()
            return redirect(reverse("student-assignment-list-view", args=[sid,cid]))

    template_name = "student_assignment_list_view.html"
    context = {"formset": formset, "object_list": assignments, "student":student, "curriculum":curriculum, "title": my_title}
    return render(request, template_name, context)



@login_required
def assignment_list_view(request):
    my_title = "Assignments - Missing One?  Look on your Home page to contact us!"
    qs = Assignment.objects.all()
    assignment_filter = AssignmentFilter(request.GET, queryset=qs)
    template_name = "assignment_list_view.html"
    context = {"object_list": assignment_filter, "title": my_title}
    return render(request, template_name, context)


@staff_member_required
def assignment_update_view(request, id):
    obj = get_object_or_404(Assignment, id=id)
    form = AssignmentCreateForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("/assignment")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.id}", "form": form}
    return render(request, template_name, context)


@staff_member_required
def assignment_delete_view(request, id):
    obj = get_object_or_404(Assignment, id=id)
    template_name = "assignment_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/assignment")
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def enroll_student_step2(request, semester, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    semester_options = generate_semester_choices()
    if not semester in semester_options:
        raise Http404

    form = CurriculumEnrollmentForm(student_pk=student_pk, initial={"student":student, "academic_semester":semester})

    # restrict curriculum range for safety, defaults to none if not set during form initialization
    subject = request.POST.get('subject','')
    cqs = Curriculum.objects.filter(
        grade_level__in=[request.POST.get('grade_level',''), 'All'],
        subject=subject)

    if request.method == "POST":
        form = CurriculumEnrollmentForm(request.POST, curriculum_qs=cqs, student_pk=student_pk, initial={"student":student, "academic_semester":semester})

        if form.is_valid():
            form.save()
            messages.info(request, "You successfuly added %s to %s's gradebook!" % (form.instance.curriculum, student))
            messages.info(request, mark_safe("Weights are automatically evenly distributed per subject %s.  You may edit the weights <a href=\"%s\" target=\"_blank\">here.</a>" % (subject, reverse('weight_edit_view', args=[semester, student.pk, subject]),)))

            if "enroll_stay" in request.POST:
                # reinit the form with student and semester
                form = CurriculumEnrollmentForm(student_pk=student_pk, initial={"student":student,"academic_semester":semester})
            else:
                return redirect(reverse("enroll_student_step1"))

    template_name = "enroll_student_view_step2.html"
    context = {"form": form, "student": student, "semester":semester} 
    return render(request, template_name, context)



@login_required
def enroll_student_step1(request):
    qs = Student.objects.filter(teacher_email=request.user.email)
    student_filter = StudentFilter(request.GET, queryset=qs)
    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)
    template_name = "enroll_student_view.html"
    semester_options = generate_semester_choices()
    context = {"object_list": object_list, "semester_options":semester_options, "filter":student_filter}

    if request.method == "POST":
        try:
            student_pk = int(request.POST.get('student_pk',0))
        except Exception as e:
            return render(request, template_name, context)
        semester = request.POST.get('semester','')
        return redirect(reverse("enroll_student_step2", args=[semester, student_pk]))

    return render(request, template_name, context)


class EnrollmentUpdate(SuccessMessageMixin, UpdateView):
    model = Enrollment
    form_class = CurriculumEnrollmentUpdateForm
    template_name = "enroll_student_view_step2.html"
    success_message = "Enrollment successfully updated!"

    def get_success_url(self):
        return reverse("curriculum-schedule-detail", args=[self.object.student.pk])


@login_required
def enroll_delete(request, enrollment_pk):
    enrollment = get_object_or_404(Enrollment,pk=enrollment_pk, student__teacher_email=request.user.email)
    student = enrollment.student
    sem = enrollment.academic_semester
    subject = enrollment.curriculum.subject

    if enrollment.level == "Core" and Enrollment.objects.filter(student=student, academic_semester=sem, curriculum__subject=subject).count() > 1:
       messages.error(request,mark_safe("Hey, wait Teacher, %s is %s's CORE curriculum. It is setting her pace. If you want delete it, first choose another CORE on this page first for subject %s." % (enrollment.curriculum.name,student.get_full_name(), subject)))
       return redirect(reverse("curriculum-schedule-detail", args=[student.pk]))

    enrollment.delete()
    distribute_weights_for_sem(student, sem, subject)
    messages.success(request, "Deleted enrollment %s and all its assignments successfuly. " % (enrollment,))
    messages.info(request, mark_safe("Weights are automatically evenly distributed per subject %s.  You may edit the weights <a href=\"%s\" target=\"_blank\">here.</a>" % (subject, reverse('weight_edit_view', args=[sem, student.pk, subject]),)))
    return redirect(reverse("curriculum-schedule-detail", args=[student.pk]))

@login_required
def weight_edit_view(request, semester, student_pk, subject):
    enrollment_instances = []
    student = get_object_or_404(Student,pk=student_pk)
    qs = Enrollment.objects.filter(academic_semester=semester, student=student, curriculum__subject=subject)

    WFSet = modelformset_factory(Enrollment, form=WeightForm, extra=0, can_delete=False, formset=BaseWFSet)
    formset = WFSet(queryset=qs)
    if request.method == "POST":
        formset = WFSet(request.POST, queryset=qs)
        if formset.is_valid():
            formset.save()
            messages.info(request, "You successfuly set the weights for that student and subject!")

    template_name = "weight_form.html"
    context = {"formset": formset, "student":student, "semester":semester, "subject":subject}
    return render(request, template_name, context)

def weeks_between(start_date, end_date):
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()

@login_required
def create_weekly_step2(request, semester):
    preview = request.GET.get("preview","true")
    qs = Student.objects.filter(teacher_email=request.user.email)

    # single student
    if "student_pk" in request.GET:
        qs = qs.filter(pk=int(request.GET.get("student_pk")))

    student_filter = StudentFilter(request.GET, queryset=qs)

    # make status changes when submitted
    if request.method == "POST":
        StatusChangeFormset = formset_factory(StatusChangeForm, extra=0, can_delete=False)
        formset = StatusChangeFormset(request.POST)
        if formset.is_valid():
            # #hide current assignments from weekly
            # sa = StudentAssignment.objects.filter(student__teacher_email=request.user.email, student__in=student_filter.qs)
            # sa.update(shown_in_weekly=False)

            # make status changes, also marks 'shown'
            for form in formset.forms:
                form.save()

            messages.success(request, "All assignments are updated on the student screen.")

            return redirect('/')

    data = []
    for student in student_filter.qs: 
        ordered = []
        assignments = StudentAssignment.objects.filter(student=student, enrollment__academic_semester=semester).filter(Q(status='Not Assigned')|Q(status='Assigned',enrollment__tracking='Repeating Weekly')) #, shown_in_weekly=False)

        # group by curriculum
        curriculum_pks = list(assignments.values_list('assignment__curriculum',flat=True).distinct())
        curriculums = Curriculum.objects.filter(pk__in=curriculum_pks) 
        for cur in curriculums:
            cur_assignments = assignments.filter(assignment__curriculum=cur)
            enrollment = Enrollment.objects.get(academic_semester=semester, student=student, curriculum=cur)
            if enrollment.tracking == "Repeating Weekly":
                weekly_assignments = StudentAssignment.objects.filter(student=student, enrollment__academic_semester=semester,status="Assigned", assignment__curriculum=cur) 
                ordered += weekly_assignments
                cur.repeating = True # mark for presentation
            elif enrollment.tracking == "From Pacing List":
                # pick by formulation, examples:
                # Rules:
                #   - if exact, then assign that much
                #   - if remainder then assign + 1

                # Examples:
                # assignment count / weeks left
                #  4/4 -> 1
                #  8/4 -> 2
                # 12/4 -> 3
                #  5/4 -> 2
                #  6/4 -> 2
                #  7/4 -> 2
                #  8/4 -> 2
                #  9/4 -> 3
                # 10/4 -> 3
                # 11/4 -> 3
                # 12/4 -> 3
                #  0/4 -> 0

                sem_end = enrollment.semesterend
                weeks_left = weeks_between(timezone.now(), sem_end)
                if weeks_left == 0: # prevent division by 0
                    weeks_left = 1 
                assignments_count = cur_assignments.count()

                # only comment in for debugging purposes
                # print("curriculum: %s semesterend: %s" % (str(cur), str(sem_end)))
                # print("assigments:%d weeksleft:%d\n" % (assignments_count, weeks_left))

                exact_result = assignments_count // weeks_left
                real_result = assignments_count / weeks_left
                if real_result > exact_result:
                    exact_result += 1

                ordered += assignments.filter(assignment__curriculum=cur)[:exact_result]
                ordered += StudentAssignment.objects.filter(student=student, enrollment__academic_semester=semester,status="Assigned", assignment__curriculum=cur) 

        data.append({"student":student, "assignments":ordered, "curriculums":curriculums})
        
    # generate form
    initial = []
    students = []
    for change in data:
        if len(change["assignments"]) == 0:
            continue

        students.append({"pk":change["student"].pk, "name":change["student"].get_full_name(), "curriculums":change["curriculums"]})
        
        for assignment in change["assignments"]:
            initial.append({
                'assignment':assignment,
                'new_status':'Assigned', 
                'assignment_description': assignment.assignment.name +"<br/><small>" + assignment.assignment.description + "</small>"})
    StatusChangeFormset = formset_factory(StatusChangeForm, extra=0, can_delete=False)
    formset = StatusChangeFormset(request.POST or None, initial=initial)

    # skip preview
    if preview == "false":
        for form in formset.forms:
            form.cleaned_data = {
                'assignment': form.initial['assignment'],
                'new_status': form.initial['new_status']}
            form.save()
        messages.success(request, "All assignments marked as assigned are now showing on the student screen. You may always re-generate a new list.")
        return redirect('/')

    context = {"formset": formset, "students":students}
    template_name = "create_weekly_step2.html"
    return render(request, template_name, context)


@login_required
def create_weekly_step1(request, semester):
    my_title = "Send Weekly Assignment List to Student Screen"
    qs = Student.objects.filter(teacher_email=request.user.email)
    student_filter = StudentFilter(request.GET, queryset=qs)

    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)

    template_name = "create_weekly_step1.html"
    context = {"object_list": object_list, "filter": student_filter, "title": my_title, "semester": semester}
    return render(request, template_name, context)

@login_required
def create_weekly_home(request):
    semester_options = generate_semester_choices()
    template_name = "create_weekly_home.html"
    context = {"semesters": semester_options}
    return render(request, template_name, context)

@login_required
def see_late_home(request):
    my_title = "Late Assignments"

    if request.user.groups.filter(name="Student").count() > 0: # student is viewing
        student = get_object_or_404(Student, email=request.user.email)
        return redirect(reverse("see_late_detail", args=[student.pk]))

    if request.user.groups.filter(name="Owner").count() > 0:
        qs = Student.objects.all()
    else:
        qs = Student.objects.filter(teacher_email=request.user.email)

    student_filter = StudentFilter(request.GET, queryset=qs)

    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)

    template_name = "student_weekly_home.html"
    context = {"object_list": object_list, "filter": student_filter, "title": my_title, "late_view": True}
    return render(request, template_name, context)

@login_required
def see_late_detail(request, student_pk):
    if request.user.groups.filter(name="Student").count() > 0: # student is viewing
        student = get_object_or_404(Student, pk=student_pk, email=request.user.email)
    elif request.user.groups.filter(name="Owner").count() > 0:
        student = get_object_or_404(Student, pk=student_pk)
    else:
        student = get_object_or_404(Student, pk=student_pk, teacher_email=request.user.email)

    assignments = StudentAssignment.objects.filter(student=student, status='Incomplete') 

    data = [] 
    for asm in assignments:
        data.append({'title':asm.assignment.name, 'detail':asm.assignment.description, 'curriculum':asm.assignment.curriculum.name, 'cur_pk':asm.assignment.curriculum.pk})

    template_name = "student_weekly_detail.html"
    context = {"object": student, "assignments": data, "late_view": True}
    return render(request, template_name, context)

@login_required
def see_weekly_home(request):
    my_title = "This Week's Assignments"

    if request.user.groups.filter(name="Student").count() > 0: # student is viewing
        student = get_object_or_404(Student, email=request.user.email)
        return redirect(reverse("see_weekly_detail", args=[student.pk]))

    if request.user.groups.filter(name="Owner").count() > 0:
        qs = Student.objects.all()
    else:
        qs = Student.objects.filter(teacher_email=request.user.email)

    student_filter = StudentFilter(request.GET, queryset=qs)

    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)

    template_name = "student_weekly_home.html"
    context = {"object_list": object_list, "filter": student_filter, "title": my_title}
    return render(request, template_name, context)

@login_required
def see_weekly_detail(request, student_pk):
    if request.user.groups.filter(name="Student").count() > 0: # student is viewing
        student = get_object_or_404(Student, pk=student_pk, email=request.user.email)
    elif request.user.groups.filter(name="Owner").count() > 0:
        student = get_object_or_404(Student, pk=student_pk)
    else:
        student = get_object_or_404(Student, pk=student_pk, teacher_email=request.user.email)

    assignments = StudentAssignment.objects.filter(student=student, status='Assigned') #, shown_in_weekly=True)

    data = [] 
    for asm in assignments:
        data.append({'title':asm.assignment.name, 'detail':asm.assignment.description, 'curriculum':asm.assignment.curriculum.name, 'cur_pk':asm.assignment.curriculum.pk})

    template_name = "student_weekly_detail.html"
    context = {"object": student, "assignments": data}
    return render(request, template_name, context)

@login_required
def send_weekly_email(request, student_pk):
    if request.user.groups.filter(name="Owner").count() > 0:
        student = get_object_or_404(Student, pk=student_pk)
    else:
        student = get_object_or_404(Student, pk=student_pk, teacher_email=request.user.email)

    assignments = StudentAssignment.objects.filter(student=student, status='Assigned') #, shown_in_weekly=True)

    data = [] 
    for asm in assignments:
        data.append({'title':asm.assignment.name, 'detail':asm.assignment.description, 'curriculum':asm.assignment.curriculum.name, 'cur_pk':asm.assignment.curriculum.pk})

    subject, from_email, to = "%s's Assignments for This Week" % student.get_full_name(), 'yourepiconline@gmail.com', [
    student.email, student.additional_email]
    text_content = 'Your most updated list of weekly assignments.  You may need to open this in a different browser if you do not see it here. '
    html_content = render_to_string('mail_weekly_assignments.html', context={'assignments':data, 'student':student})
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    messages.success(request, "Weekly assignments are sent to %s!" % student.get_full_name())
    return redirect(reverse("see_weekly_detail", args=[student.pk]))


@login_required
def send_late_email(request, student_pk):
    if request.user.groups.filter(name="Owner").count() > 0:
        student = get_object_or_404(Student, pk=student_pk)
    else:
        student = get_object_or_404(Student, pk=student_pk, teacher_email=request.user.email)

    assignments = StudentAssignment.objects.filter(student=student, status='Incomplete') 

    data = [] 
    for asm in assignments:
        data.append({'title':asm.assignment.name, 'detail':asm.assignment.description, 'curriculum':asm.assignment.curriculum.name, 'cur_pk':asm.assignment.curriculum.pk})

    subject, from_email, to = "%s's Late Assignments As Of: %s" % (student.get_full_name(),timezone.now().date()), 'yourepiconline@gmail.com', [
    student.email, student.additional_email]
    text_content = 'Your most updated list of late assignments.  You may need to open this in a different browser if you do not see it here. '
    html_content = render_to_string('mail_late_assignments.html', context={'assignments':data, 'student':student})
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    messages.success(request, "Late assignments are sent to %s!" % student.get_full_name())
    return redirect(reverse("see_late_detail", args=[student.pk]))


@login_required
@api_view(['GET'])
def api_curriculum_list(request):
    subject = request.GET.get('subject','')
    grade_level = request.GET.get('grade_level','')
    results = []
    for cur in Curriculum.objects.filter(subject=subject,grade_level__in=[grade_level, 'All']).order_by('grade_level'):
        results.append({"id":cur.pk,"name":str(cur)})
    return Response({"results":results})


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
    qs = GradeBook.objects.all()
    gradebook_filter = GradeBookFilter(request.GET, queryset=qs)
    template_name = "gradebook_list_view.html"
    context = {"object_list": gradebook_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def grades_update_view(request, id):
    obj = get_object_or_404(GradeBook, id=id)
    form = RecordGradeForm(request.POST or None, instance=obj)
    if form.is_valid():
        print('form is valid')
        form.save()
        return redirect("/grades")
    template_name = "form.html"
    context = {"title": f"Update Information for: {obj.id}", "form": form}
    return render(request, template_name, context)


@staff_member_required
def grades_delete_view(request, epicenter_id):
    obj = get_object_or_404(GradeBook, id=id)
    template_name = "gradebook_delete_view.html"
    if request.method == "POST":
        obj.delete()
        return redirect("/grades")
    context = {"object": obj}
    return render(request, template_name, context)

@login_required
def student_curriculum_schedule(request):
    my_title = "Add a Curriculum to Student Gradebook"
    qs = Student.objects.filter(teacher_email=request.user.email)
    student_filter = StudentFilter(request.GET, queryset=qs)
    #curriculum_filter = CurriculumFilter(request.GET, queryset=qs)

    p = Paginator(student_filter.qs, 10)
    page = request.GET.get('page',1)
    object_list = p.get_page(page)

    template_name = "student_curriculum_view.html"
    context = {"object_list": object_list, "filter": student_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def student_curriculum_schedule_detail(request, id):
    my_title = "Student Curriculum Details"
    student = get_object_or_404(Student, pk=id)
    curriculum_filter = EnrollmentFilter(request.GET, queryset=student.student_enrollment)
    active_weights = get_active_sems(student)
    template_name = "student_curriculum_detail_view.html"
    context = {"student": student, "active_weights": active_weights, "object_list": curriculum_filter.qs, "filter": curriculum_filter, "title": my_title}
    return render(request, template_name, context)


@login_required
def curriculum_assignment_list(request):
    my_title = "Assignments in Curriculum"
    qs = Curriculum.objects.all()
    curriculum_filter = CurriculumFilter(request.GET, queryset=qs)
    template_name = "curriculum_assignment_view.html"
    context = {"object_list": curriculum_filter, "title": my_title}
    return render(request, template_name, context)


class ShowStudents(View):
    template_name = "show-students.html"

    def get(self, request):
        students = Student.objects.all().order_by("id")
        return render(self.request, template_name=self.template_name, context={'students': students})


#class StudentAssignmentView(View):
#    template_name = "student-assignments.html"
#
#    def get(self, request, id):
#        student = get_object_or_404(Student, id=id)
#
#        try:
#            exempt_assignment = ExemptAssignment.objects.get(student=student)
#        except Exception as e:
#            exempt_assignment = None
#            assignments = Assignment.objects.filter(curriculum=student.curriculum)
#
#        if exempt_assignment:
#            exempt_assignment_ids = [x.id for x in exempt_assignment.assignments.all()]
#            assignments = Assignment.objects.filter(curriculum=student.curriculum).exclude(
#                id__in=exempt_assignment_ids).order_by("id")
#
#        return render(request, template_name=self.template_name,
#                      context={"student": student, "assignments": assignments})

@login_required
def roster_list_view(request):
    my_title = "Your Roster"
    qs = Student.objects.all()
    student_filter = StudentFilter(request.GET, queryset=qs)
    template_name = "roster_list_view.html"
    context = {"object_list": student_filter, "title": my_title}
    return render(request, template_name, context)

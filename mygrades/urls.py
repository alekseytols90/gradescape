from django.conf import settings
from django.conf.urls import url,static
from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls import handler404, handler500


from mygrades.views import (
	student_list_view,
    student_delete_view,
    student_update_view,
    student_setup_view,
    curriculum_create_view,
    curriculum_list_view,
    curriculum_update_view,
    curriculum_delete_view,
    enroll_student_view,
    crawl,
    standard_create_view,
    standard_list_view,
    standard_update_view,
    standard_delete_view,
    assignment_create_view,
    assignment_list_view,
    assignment_update_view,
    assignment_delete_view,
    grades_record_view,
    grades_list_view,
    grades_update_view,
    grades_delete_view,
    student_curriculum_schedule,
    curriculum_assignment_list,
    standard_upload,
    curriculum_upload,
    assignment_upload,
    send_pacing_guide,
    crawler,

    )

urlpatterns = [
    path("assignment-upload/", assignment_upload, name="assignment_upload"),
    path("curriculum-upload/", curriculum_upload, name="curriculum_upload"),
    path("standard-upload/", standard_upload, name="standard_upload"),
    path('admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    #path("api/crawl/", crawl),
    path("students/", student_list_view),
    path("students/<int:epicenter_id>/edit/", student_update_view),
    path("students/<int:epicenter_id>/delete/", student_delete_view),
    path("students-setup/", student_setup_view),
    path("curriculum-schedule/", student_curriculum_schedule),
    path("curriculum-create/", curriculum_create_view),
    path("curriculum/", curriculum_list_view),
    path("curriculum-update/", curriculum_list_view),
    path("curriculum/<int:id>/delete/", curriculum_delete_view),
    path("curriculum/<int:id>/edit/", curriculum_update_view),
    path("curriculum-assignments/", curriculum_assignment_list),
    path("enroll-student/", enroll_student_view),
    path("standard-create/", standard_create_view),
    path("standard/", standard_list_view),
    path("standard-update/", standard_list_view),
    path("standard/<int:id>/delete/", standard_delete_view),
    path("standard/<int:id>/edit/", standard_update_view),
    path("assignment-create/", assignment_create_view),
    path("assignment/", assignment_list_view),
    path("assignment-update/", assignment_list_view),
    path("assignment/<int:id>/delete/", assignment_delete_view),
    path("assignment/<int:id>/edit/", assignment_update_view),
    path("send-pacing-guide/", send_pacing_guide),
    path("grades-record/", grades_record_view),
    path("grades/", grades_list_view),
    path("grades-update/", grades_list_view),
    path("grades/<int:id>/delete/", grades_delete_view),
    path("grades/<int:id>/edit/", grades_update_view),
    url(r'^api/crawl/', crawl, name='crawl'),
    path(r"api/crawler/<str:site>",crawler,name="crawler"),



    # path("send-schedule/", ),
    # path("late-assignment/", ),
    # path("progress/", ),
    # path("report-card/", ),
    # path("plp/", ),
]

# This is required for static files while in development mode. (DEBUG=TRUE)
# No, not relevant to scrapy or crawling :)
# if settings.DEBUG:
#     urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

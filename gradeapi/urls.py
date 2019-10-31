from django.urls import path
from rest_framework import routers
from gradeapi.views import ShowStudents, ExemptStudentsModelViewSet
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register('show-students', ShowStudents, base_name='show-students')
router.register('exempt-student', ExemptStudentsModelViewSet, base_name='exempt-student')

urlpatterns = [
    path('token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls

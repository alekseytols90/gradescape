from django.contrib import admin
from django.urls import path, include

#added these two for the 404 experiment
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static


urlpatterns = [

    #path('$/404/$'), error_404),
    #python mpath('admin/', admin.site.urls),
    path('',include('mygrades.urls')),
    
]
#+ static(settings.MEDIA_URL, document_root-settings.MEDIA_ROOT)
#
# #added these below AND the + static info just above for the 404 experiment
# handler404 = common_views.error_404
# handler500 = common_views.error_500
admin.site.site_header = "Gradebook"
admin.site.site_title = "Gradebook"
admin.site.index_title = "Your Gradebook"
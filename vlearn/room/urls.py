from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.rooms, name='rooms'),
    path('create/', views.create_room, name='create_room'),
    path('<slug:slug>/', views.room, name='room'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
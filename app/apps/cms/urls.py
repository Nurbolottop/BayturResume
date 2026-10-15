from django.urls import path

from . import views

app_name = 'cms'

urlpatterns = [
    path('news/', views.post_list, name='posts'),
    path('news/<slug:slug>/', views.post_detail, name='post'),
    path('history/', views.history, name='history'),
    # Последним: объекты (/resort/, /kymyz/, /ski/) и свободные страницы
    path('<slug:slug>/', views.slug_page, name='page'),
]

from django.urls import path

from . import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('llms.txt', views.llms_txt, name='llms'),
    path(f'{views.INDEXNOW_KEY}.txt', views.indexnow_key),
]

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.base.sitemaps import SITEMAPS

admin.site.site_header = 'Байтур — управление сайтом'
admin.site.site_title = 'Байтур'
admin.site.index_title = 'Разделы'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('', include('apps.base.urls')),
    path('', include('apps.contacts.urls')),
    # cms последним: в нём маршрут /<slug>/ для страниц объектов
    path('', include('apps.cms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

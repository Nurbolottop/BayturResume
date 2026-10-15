from django.conf import settings

from apps.base import company
from apps.cms.models import HistoryEvent, Page, Property


def site(request):
    pages = list(Page.objects.filter(is_published=True).only('title', 'slug', 'in_menu', 'in_footer'))
    return {
        'site_url': settings.SITE_URL,
        'canonical': settings.SITE_URL + request.path,
        'company': company,
        'nav_properties': Property.objects.filter(is_active=True),
        'menu_pages': [p for p in pages if p.in_menu],
        'footer_pages': [p for p in pages if p.in_footer],
        'has_history': HistoryEvent.objects.filter(is_published=True).exists(),
    }

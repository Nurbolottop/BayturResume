from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.cms.models import HistoryEvent, Page, Post, Property


class HubSitemap(Sitemap):
    """Адреса строятся от SITE_URL, а не от домена запроса: иначе www или IP попадут в карту."""

    def get_protocol(self, protocol=None):
        return urlsplit(settings.SITE_URL).scheme

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc


class StaticSitemap(HubSitemap):
    def items(self):
        items = [('base:home', 1.0), ('base:about', 0.8), ('cms:posts', 0.7), ('contacts:contacts', 0.6)]
        if HistoryEvent.objects.filter(is_published=True).exists():
            items.append(('cms:history', 0.7))
        return items

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class PropertySitemap(HubSitemap):
    priority = 0.9

    def items(self):
        return Property.objects.filter(is_active=True)


class PostSitemap(HubSitemap):
    priority = 0.6

    def items(self):
        return Post.objects.published()

    def lastmod(self, post):
        return post.updated_at


class PageSitemap(HubSitemap):
    priority = 0.6

    def items(self):
        return Page.objects.filter(is_published=True)

    def lastmod(self, page):
        return page.updated_at


SITEMAPS = {'pages': StaticSitemap, 'properties': PropertySitemap, 'posts': PostSitemap, 'info': PageSitemap}

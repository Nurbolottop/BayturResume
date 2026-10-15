"""
Микроразметка Schema.org.

Ради неё хаб и делается: он объявляет Organization с постоянным @id, а три
объекта — её подразделения. Объекты ссылаются обратно через parentOrganization
с тем же @id; без обратной ссылки поисковик связь не засчитает.
"""
import json

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from apps.base import company


def org_id():
    return f'{settings.SITE_URL}/#organization'


def website_id():
    return f'{settings.SITE_URL}/#website'


def absolute(path):
    if path.startswith('http'):
        return path
    return settings.SITE_URL + path


def to_script(data):
    raw = json.dumps(data, ensure_ascii=False, indent=None).replace('</', '<\\/')
    return mark_safe(f'<script type="application/ld+json">{raw}</script>')


def property_node(prop):
    node = {
        '@type': prop.schema_type,
        '@id': prop.schema_id,
        'name': prop.name,
        'url': prop.site_url,
        'description': strip_tags(prop.lead).strip(),
        'image': absolute(prop.image_url),
        'parentOrganization': {'@id': org_id()},
    }
    if prop.phone:
        node['telephone'] = prop.phone
    if prop.address:
        node['address'] = {'@type': 'PostalAddress', 'streetAddress': prop.address, 'addressCountry': 'KG'}
    if prop.instagram:
        node['sameAs'] = [prop.instagram]
    return node


def organization(properties):
    data = {
        '@type': 'Organization',
        '@id': org_id(),
        'name': company.NAME_LATIN,
        'alternateName': [company.NAME, 'Байтур Кыргызстан'],
        'legalName': company.LEGAL_NAME,
        'description': company.DESCRIPTION,
        'url': settings.SITE_URL + '/',
        'logo': {'@type': 'ImageObject', 'url': absolute(static('img/logo.png'))},
        'email': company.EMAIL,
        'telephone': company.PHONES[0],
        'taxID': company.INN,
        'areaServed': 'Кыргызстан',
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': company.ADDRESS['street'],
            'addressLocality': company.ADDRESS['locality'],
            'addressRegion': company.ADDRESS['region'],
            'postalCode': company.ADDRESS['postal_code'],
            'addressCountry': company.ADDRESS['country'],
        },
        'subOrganization': [property_node(p) for p in properties],
    }
    if company.SAME_AS:
        data['sameAs'] = company.SAME_AS
    return data


def website():
    return {
        '@type': 'WebSite',
        '@id': website_id(),
        'url': settings.SITE_URL + '/',
        'name': company.NAME,
        'inLanguage': 'ru-RU',
        'publisher': {'@id': org_id()},
    }


def breadcrumbs(items):
    """items: [(название, путь)] начиная с главной."""
    return {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': absolute(path)}
            for i, (name, path) in enumerate(items, start=1)
        ],
    }


def blog_posting(post):
    url = absolute(post.get_absolute_url())
    data = {
        '@type': 'BlogPosting',
        '@id': url + '#article',
        'headline': post.title,
        'description': post.description,
        'datePublished': post.published_at.isoformat(),
        'dateModified': post.updated_at.isoformat(),
        'inLanguage': 'ru-RU',
        'author': {'@id': org_id()},
        'publisher': {'@id': org_id()},
        'isPartOf': {'@id': website_id()},
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'image': absolute(post.cover_url),
    }
    about = [{'@id': p.schema_id} for p in post.properties.all()]
    if about:
        data['about'] = about
    return data


def graph(*nodes):
    return to_script({'@context': 'https://schema.org', '@graph': [n for n in nodes if n]})

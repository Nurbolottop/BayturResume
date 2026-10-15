from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from apps.cms.models import HistoryEvent, Page, Post, Property

# Ключ IndexNow: файл с ним лежит в корне сайта и подтверждает, что мы владельцы.
INDEXNOW_KEY = '7d3e9a41c2b84f0e9a6b1c5d8e2f4a70'

# Роботы ИИ-поиска и ассистентов перечислены явно: часть из них по умолчанию
# считает молчание запретом, а нам нужно, чтобы на вопрос «что такое Байтур»
# они отвечали по этому сайту.
AI_BOTS = [
    'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
    'ClaudeBot', 'Claude-SearchBot', 'Claude-User',
    'PerplexityBot', 'Perplexity-User',
    'Google-Extended', 'Applebot-Extended',
    'YandexAdditional', 'YandexAdditionalBot',
]


def home(request):
    return render(request, 'pages/home.html', {
        'posts': Post.objects.published().select_related('category').prefetch_related('properties')[:3],
        'history': HistoryEvent.objects.filter(is_published=True).order_by('-year', '-order')[:3],
    })


def about(request):
    return render(request, 'pages/about.html', {
        'crumbs': [('Главная', '/'), ('О компании', request.path)],
    })


@require_GET
@cache_control(max_age=3600)
def robots_txt(request):
    lines = ['User-agent: *', 'Allow: /', 'Disallow: /admin/', 'Disallow: /ckeditor5/', '']
    for bot in AI_BOTS:
        lines += [f'User-agent: {bot}', 'Allow: /', 'Disallow: /admin/', '']
    lines.append(f'Sitemap: {settings.SITE_URL}/sitemap.xml')
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')


@require_GET
@cache_control(max_age=3600)
def llms_txt(request):
    text = render_to_string('seo/llms.txt', {
        'properties': Property.objects.filter(is_active=True),
        'posts': Post.objects.published()[:10],
        'pages': Page.objects.filter(is_published=True),
        'history': HistoryEvent.objects.filter(is_published=True),
    }, request=request)
    return HttpResponse(text, content_type='text/markdown; charset=utf-8')


@require_GET
def indexnow_key(request):
    return HttpResponse(INDEXNOW_KEY, content_type='text/plain; charset=utf-8')

from itertools import groupby

from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from apps.base import seo

from .models import Category, HistoryEvent, Page, Post, Property


def slug_page(request, slug):
    """baytur.kg/<адрес>/ — сначала объект, потом свободная страница."""
    prop = Property.objects.filter(slug=slug, is_active=True).first()
    if prop:
        return property_detail(request, prop)
    page = Page.objects.filter(slug=slug, is_published=True).first()
    if page:
        return render(request, 'pages/page.html', {
            'page': page,
            'crumbs': [('Главная', '/'), (page.title, request.path)],
            'og_image': page.cover_url,
        })
    raise Http404


def property_detail(request, prop):
    return render(request, 'pages/property.html', {
        'property': prop,
        'posts': prop.posts.published().select_related('category').prefetch_related('properties')[:3],
        'history': prop.history.filter(is_published=True)[:6],
        'others': Property.objects.filter(is_active=True).exclude(pk=prop.pk),
        'crumbs': [('Главная', '/'), (prop.name, request.path)],
        'og_image': prop.image_url,
    })


def post_list(request):
    posts = Post.objects.published().select_related('category').prefetch_related('properties')
    category = Category.objects.filter(slug=request.GET.get('category')).first()
    if category:
        posts = posts.filter(category=category)
    page = Paginator(posts, 12).get_page(request.GET.get('page'))
    return render(request, 'pages/news_list.html', {
        'page': page,
        'category': category,
        'categories': Category.objects.filter(posts__is_published=True).distinct(),
        'crumbs': [('Главная', '/'), ('Публикации', request.path)],
        # Фильтры и страницы — те же материалы, в индекс их не пускаем
        'noindex': bool(request.GET),
    })


def post_detail(request, slug):
    qs = Post.objects.published().select_related('category').prefetch_related('properties')
    post = get_object_or_404(qs, slug=slug)
    return render(request, 'pages/news_detail.html', {
        'post': post,
        'more': qs.exclude(pk=post.pk)[:3],
        'crumbs': [('Главная', '/'), ('Публикации', '/news/'), (post.title, request.path)],
        'schema_nodes': [seo.blog_posting(post)],
        'og_image': post.cover_url,
        'og_type': 'article',
    })


def history(request):
    events = HistoryEvent.objects.filter(is_published=True).prefetch_related('properties').select_related('post')
    years = [(year, list(items)) for year, items in groupby(events, key=lambda e: e.year)]
    return render(request, 'pages/history.html', {
        'years': years,
        'crumbs': [('Главная', '/'), ('История', request.path)],
    })

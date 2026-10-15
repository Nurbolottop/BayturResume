from django.core.exceptions import ValidationError
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django_ckeditor_5.fields import CKEditor5Field
from django_resized import ResizedImageField

from apps.base.models import SEOModel, TimeStampedModel

# Объекты и свободные страницы живут на одном уровне: baytur.kg/<адрес>/.
# Эти адреса заняты разделами сайта.
RESERVED_SLUGS = {'admin', 'about', 'news', 'history', 'contacts', 'static', 'media', 'ckeditor5',
                  'sitemap', 'robots', 'llms', 'en', 'ky', 'ru'}


def validate_top_slug(slug, exclude_model, exclude_pk):
    if slug in RESERVED_SLUGS:
        raise ValidationError({'slug': 'Этот адрес занят разделом сайта.'})
    for model in (Property, Page):
        qs = model.objects.filter(slug=slug)
        if model is exclude_model:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise ValidationError({'slug': f'Адрес уже занят: {qs.first()}.'})


class Property(SEOModel):
    """
    Объект группы: курорт, кымызолечебница, горнолыжная база.

    На хабе — только кто, где, для кого и когда. Цены, номера и бронирование
    живут на сайте объекта: если перенести их сюда, вернутся дубли.
    """

    slug = models.SlugField('адрес на хабе', unique=True, help_text='resort → baytur.kg/resort/')
    name = models.CharField('название', max_length=120)
    kind = models.CharField('что это', max_length=60, help_text='Курорт, кымызолечебница…')
    region = models.CharField('место', max_length=120, help_text='Например: Иссык-Куль · Бостери')
    season = models.CharField('сезон', max_length=120, blank=True)
    lead = models.TextField('анонс', help_text='Две строки для карточки на главной.')
    body = CKEditor5Field('описание', help_text='Абзац-другой своими словами. Без цен и списков номеров.')
    facts = models.TextField(
        'короткие факты', blank=True,
        help_text='По одному на строке в виде «Название: значение».',
    )

    site_url = models.URLField('сайт объекта')
    link_text = models.CharField(
        'текст ссылки на сайт', max_length=160,
        help_text='Осмысленный текст: «Сайт курорта Baytur Resort & Spa», не «Подробнее».',
    )
    link_note = models.CharField('подпись под ссылкой', max_length=240, blank=True)

    phone = models.CharField('телефон', max_length=40, blank=True)
    phone_note = models.CharField('к телефону', max_length=60, blank=True, help_text='Например: WhatsApp')
    instagram = models.URLField('Instagram', blank=True)
    address = models.CharField('адрес', max_length=200, blank=True)

    schema_type = models.CharField('тип schema.org', max_length=40, default='LodgingBusiness')
    schema_id = models.URLField(
        '@id на сайте объекта',
        help_text='Должен совпадать с @id в разметке самого объекта — иначе связь не склеится.',
    )

    image = ResizedImageField('фото', size=[1600, 1200], quality=82, force_format='WEBP',
                              upload_to='properties/', blank=True)
    static_image = models.CharField('фото из статики', max_length=60, blank=True,
                                    help_text='Имя без размера, напр. resort. Используется, если фото не загружено.')

    order = models.PositiveSmallIntegerField('порядок', default=0)
    is_active = models.BooleanField('показывать', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'объект'
        verbose_name_plural = 'объекты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cms:page', args=[self.slug])

    def clean(self):
        validate_top_slug(self.slug, Property, self.pk)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        if self.static_image:
            return static(f'img/{self.static_image}-1920.webp')
        return static('img/og.jpg')

    @property
    def image_small_url(self):
        if self.image or not self.static_image:
            return self.image_url
        return static(f'img/{self.static_image}-960.webp')

    @property
    def site_host(self):
        return self.site_url.split('//', 1)[-1].rstrip('/')

    @property
    def facts_list(self):
        rows = []
        for line in self.facts.splitlines():
            if ':' in line:
                label, value = line.split(':', 1)
                rows.append((label.strip(), value.strip()))
        return rows


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())


class Category(models.Model):
    """Рубрика публикаций: новости, статьи, события, награды, пресса — сколько понадобится."""

    name = models.CharField('название', max_length=80)
    slug = models.SlugField('адрес', unique=True)
    order = models.PositiveSmallIntegerField('порядок', default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'рубрика'
        verbose_name_plural = 'рубрики'

    def __str__(self):
        return self.name


class Post(TimeStampedModel, SEOModel):
    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField('адрес', max_length=200, unique=True)
    category = models.ForeignKey(Category, verbose_name='рубрика', on_delete=models.PROTECT, related_name='posts')
    properties = models.ManyToManyField(
        Property, verbose_name='о каких объектах', blank=True, related_name='posts',
        help_text='Публикация появится на странице объекта, ссылки на него — в тексте.',
    )
    excerpt = models.TextField('анонс', max_length=400, help_text='Пара предложений для списка и соцсетей.')
    body = CKEditor5Field('текст')
    cover = ResizedImageField('обложка', size=[1600, 1000], quality=82, force_format='WEBP',
                              upload_to='posts/', blank=True)
    cover_alt = models.CharField('описание обложки', max_length=200, blank=True)

    published_at = models.DateTimeField('дата публикации', default=timezone.now)
    is_published = models.BooleanField('опубликовано', default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:post', args=[self.slug])

    @property
    def description(self):
        return self.seo_description or Truncator(strip_tags(self.excerpt)).chars(200)

    @property
    def cover_url(self):
        """Обложка, а если её нет — фото первого объекта, о котором публикация."""
        if self.cover:
            return self.cover.url
        prop = self.properties.all()[:1]
        return prop[0].image_url if prop else static('img/resort-aerial-1920.webp')

    @property
    def cover_small_url(self):
        if self.cover:
            return self.cover.url
        prop = self.properties.all()[:1]
        return prop[0].image_small_url if prop else static('img/resort-aerial-960.webp')


class HistoryEvent(TimeStampedModel):
    """Событие в истории компании: открытие объекта, стройка, награда, юбилей."""

    year = models.PositiveSmallIntegerField('год')
    date_label = models.CharField('уточнение даты', max_length=40, blank=True,
                                  help_text='Необязательно: «весна», «июнь», «15 августа».')
    title = models.CharField('заголовок', max_length=200)
    text = CKEditor5Field('рассказ', blank=True)
    image = ResizedImageField('фото', size=[1600, 1200], quality=82, force_format='WEBP',
                              upload_to='history/', blank=True)
    image_alt = models.CharField('описание фото', max_length=200, blank=True)
    properties = models.ManyToManyField(Property, verbose_name='объекты', blank=True, related_name='history')
    post = models.ForeignKey(Post, verbose_name='подробная публикация', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='history')
    order = models.PositiveSmallIntegerField('порядок внутри года', default=0)
    is_published = models.BooleanField('показывать', default=True)

    class Meta:
        ordering = ['year', 'order', 'id']
        verbose_name = 'событие истории'
        verbose_name_plural = 'история компании'

    def __str__(self):
        return f'{self.year} — {self.title}'


class Page(TimeStampedModel, SEOModel):
    """
    Свободная страница: миссия, команда, партнёры, вакансии, благотворительность —
    любой раздел, который появится позже, без участия программиста.
    """

    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField('адрес', unique=True, help_text='team → baytur.kg/team/')
    lead = models.TextField('подзаголовок', blank=True)
    body = CKEditor5Field('текст')
    cover = ResizedImageField('фото для шапки', size=[1920, 1280], quality=82, force_format='WEBP',
                              upload_to='pages/', blank=True)
    in_menu = models.BooleanField('показывать в меню', default=False)
    in_footer = models.BooleanField('показывать в подвале', default=True)
    order = models.PositiveSmallIntegerField('порядок', default=0)
    is_published = models.BooleanField('опубликовано', default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'страница'
        verbose_name_plural = 'страницы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:page', args=[self.slug])

    def clean(self):
        validate_top_slug(self.slug, Page, self.pk)

    @property
    def cover_url(self):
        return self.cover.url if self.cover else static('img/resort-aerial-1920.webp')

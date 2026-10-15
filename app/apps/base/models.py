from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('создано', auto_now_add=True)
    updated_at = models.DateTimeField('изменено', auto_now=True)

    class Meta:
        abstract = True


class SEOModel(models.Model):
    """Поля для заголовка и описания в выдаче. Пустые — берутся из основного текста."""

    seo_title = models.CharField(
        'SEO-заголовок', max_length=120, blank=True,
        help_text='Заголовок вкладки и сниппета. Пусто — используется название.',
    )
    seo_description = models.CharField(
        'SEO-описание', max_length=300, blank=True,
        help_text='Описание для поисковиков, 140–160 символов. Пусто — используется анонс.',
    )

    class Meta:
        abstract = True

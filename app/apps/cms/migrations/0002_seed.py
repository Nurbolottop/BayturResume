from django.db import migrations
from django.utils.dateparse import parse_datetime

from apps.cms.seed import CATEGORIES, POSTS, PROPERTIES


def seed(apps, schema_editor):
    Property = apps.get_model('cms', 'Property')
    Post = apps.get_model('cms', 'Post')
    Category = apps.get_model('cms', 'Category')

    categories = {}
    for data in CATEGORIES:
        cat, _ = Category.objects.update_or_create(slug=data['slug'], defaults=data)
        categories[cat.slug] = cat

    by_slug = {}
    for data in PROPERTIES:
        prop, _ = Property.objects.update_or_create(slug=data['slug'], defaults={
            k: v for k, v in data.items() if k != 'slug'
        })
        by_slug[prop.slug] = prop

    for data in POSTS:
        data = dict(data)
        slugs = data.pop('properties')
        data['published_at'] = parse_datetime(data['published_at'])
        data['category'] = categories[data['category']]
        post, _ = Post.objects.update_or_create(slug=data.pop('slug'), defaults=data)
        post.properties.set([by_slug[s] for s in slugs])


class Migration(migrations.Migration):
    dependencies = [('cms', '0001_initial')]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]

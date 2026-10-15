from django.contrib import admin
from django.utils.html import format_html

from .models import Category, HistoryEvent, Page, Post, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'kind', 'region', 'site_link', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'kind', 'region', 'season', 'order', 'is_active')}),
        ('Текст', {'fields': ('lead', 'body', 'facts', 'image', 'static_image')}),
        ('Ссылка на сайт объекта', {
            'description': 'Текст ссылки поисковик читает вместе с адресом — пишите, куда она ведёт.',
            'fields': ('site_url', 'link_text', 'link_note'),
        }),
        ('Контакты', {'fields': ('phone', 'phone_note', 'address', 'instagram')}),
        ('Разметка и SEO', {
            'classes': ('collapse',),
            'fields': ('schema_type', 'schema_id', 'seo_title', 'seo_description'),
        }),
    )

    @admin.display(description='сайт')
    def site_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.site_url, obj.site_host)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_at', 'is_published')
    list_filter = ('category', 'is_published', 'properties')
    list_editable = ('is_published',)
    search_fields = ('title', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('properties',)
    date_hierarchy = 'published_at'
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'category', 'properties', 'published_at', 'is_published')}),
        ('Текст', {'fields': ('excerpt', 'body', 'cover', 'cover_alt')}),
        ('SEO', {'classes': ('collapse',), 'fields': ('seo_title', 'seo_description')}),
    )


@admin.register(HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = ('year', 'date_label', 'title', 'is_published')
    list_display_links = ('title',)
    list_editable = ('is_published',)
    list_filter = ('properties', 'is_published')
    search_fields = ('title',)
    filter_horizontal = ('properties',)
    autocomplete_fields = ('post',)
    fieldsets = (
        (None, {'fields': ('year', 'date_label', 'order', 'title', 'is_published')}),
        ('Рассказ', {'fields': ('text', 'image', 'image_alt')}),
        ('Связи', {'fields': ('properties', 'post')}),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'in_menu', 'in_footer', 'order', 'is_published')
    list_editable = ('in_menu', 'in_footer', 'order', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'lead', 'is_published')}),
        ('Текст', {'fields': ('body', 'cover')}),
        ('Где показывать', {'fields': ('in_menu', 'in_footer', 'order')}),
        ('SEO', {'classes': ('collapse',), 'fields': ('seo_title', 'seo_description')}),
    )

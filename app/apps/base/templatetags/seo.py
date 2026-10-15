from django import template

from apps.base import seo

register = template.Library()


@register.simple_tag(takes_context=True)
def page_jsonld(context):
    """Organization + WebSite на каждой странице, крошки и узлы страницы — если есть."""
    crumbs = context.get('crumbs')
    nodes = [
        seo.organization(context['nav_properties']),
        seo.website(),
        seo.breadcrumbs(crumbs) if crumbs else None,
        *context.get('schema_nodes', []),
    ]
    return seo.graph(*nodes)

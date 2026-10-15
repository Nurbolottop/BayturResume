from django.shortcuts import render

from apps.cms.models import Property


def contacts(request):
    return render(request, 'pages/contacts.html', {
        'properties': Property.objects.filter(is_active=True),
        'crumbs': [('Главная', '/'), ('Контакты', request.path)],
    })

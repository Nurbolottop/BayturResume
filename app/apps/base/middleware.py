from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class LegacyRedirectMiddleware:
    """
    Раньше baytur.kg отдавал копию сайта курорта, и его адреса (/rooms/, /en/…)
    остались в поиске и в чужих ссылках. Всё, чего нет на хабе, навсегда
    переадресуем на тот же путь на курорте — чтобы он не терял позиции.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        target = getattr(settings, 'LEGACY_REDIRECT_URL', '')
        if (target and response.status_code == 404 and request.method in ('GET', 'HEAD')
                and not request.path.startswith(('/admin/', '/static/', '/media/', '/ckeditor5/'))):
            return HttpResponsePermanentRedirect(target + request.get_full_path())
        return response

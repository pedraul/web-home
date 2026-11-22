from .models import Service, SiteSettings


def get_site_settings():
    settings, _ = SiteSettings.objects.get_or_create(pk=1)
    return settings


def site_content(request):
    return {
        "site_settings": get_site_settings(),
        "footer_services": Service.objects.filter(is_published=True).only("name", "url"),
    }

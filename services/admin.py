from django.contrib import admin

from .models import ContactMessage, FaqItem, HeroSlide, Service, SiteSettings


admin.site.site_header = "Muzira Administration"
admin.site.site_title = "Muzira Admin"
admin.site.index_title = "Administration"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Company", {"fields": ("company_name", "logo", "meta_description")}),
        ("Home page", {"fields": ("ticker_text",)}),
        ("About page content", {
            "description": "Edit the heading, introduction and main story shown on the About page.",
            "fields": ("about_intro", "about_heading", "about_body"),
        }),
        ("Contact page content", {
            "description": "Edit the Contact page introduction, email, phone, address and opening hours.",
            "fields": ("contact_intro", "contact_email", "contact_phone", "office_address", "office_hours"),
        }),
        ("Support page content", {
            "description": "Edit the introduction shown at the top of the Support page.",
            "fields": ("support_intro",),
        }),
        ("Social media", {
            "description": "Paste the full link to each profile. Empty ones are hidden in the footer.",
            "fields": ("facebook_url", "instagram_url", "x_url", "linkedin_url", "youtube_url", "tiktok_url", "whatsapp_url"),
        }),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "status", "is_published", "display_order")
    list_editable = ("status", "is_published", "display_order")
    list_filter = ("is_published", "status", "category")
    search_fields = ("name", "description", "category")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "has_photo", "is_published", "display_order")
    list_editable = ("is_published", "display_order")

    @admin.display(boolean=True, description="photo")
    def has_photo(self, obj):
        return bool(obj.image)


@admin.register(FaqItem)
class FaqItemAdmin(admin.ModelAdmin):
    list_display = ("question", "is_published", "display_order")
    list_editable = ("is_published", "display_order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at", "is_handled")
    list_editable = ("is_handled",)
    list_filter = ("is_handled", "service")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "service", "message", "created_at")

    def has_add_permission(self, request):
        return False

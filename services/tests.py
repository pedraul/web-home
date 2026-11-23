import io
import tempfile

from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import ContactMessage, FaqItem, HeroSlide, Service, SiteSettings


class PublicPagesTests(TestCase):
    def test_site_settings_admin_exposes_page_content_fields(self):
        model_admin = admin.site._registry[SiteSettings]
        fieldsets = {name: options for name, options in model_admin.fieldsets}
        self.assertIn("about_intro", fieldsets["About page content"]["fields"])
        self.assertIn("contact_intro", fieldsets["Contact page content"]["fields"])
        self.assertIn("contact_email", fieldsets["Contact page content"]["fields"])
        self.assertIn("support_intro", fieldsets["Support page content"]["fields"])

    def test_about_contact_and_support_intro_are_editable(self):
        SiteSettings.objects.filter(pk=1).update(
            about_intro="Custom about introduction",
            contact_intro="Custom contact introduction",
            support_intro="Custom support introduction",
        )
        self.assertContains(self.client.get("/about/"), "Custom about introduction")
        self.assertContains(self.client.get("/contact/"), "Custom contact introduction")
        self.assertContains(self.client.get("/support/"), "Custom support introduction")

    def test_migration_seeds_sample_services_and_faqs(self):
        self.assertEqual(Service.objects.count(), 7)
        self.assertEqual(Service.objects.filter(is_published=False).get().name, "Analytics")
        self.assertEqual(FaqItem.objects.count(), 4)

    def test_home_lists_only_published_services_with_open_links(self):
        response = self.client.get("/")
        self.assertContains(response, "Nexora Billing")
        self.assertContains(response, 'href="https://billing.example.com"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertNotContains(response, "Analytics")
        self.assertNotContains(response, "Search services")

    def test_home_shows_slides_with_builtin_art_and_moving_text(self):
        response = self.client.get("/")
        self.assertContains(response, "Every service, one front door")
        self.assertContains(response, "img/slide-1.svg")
        self.assertContains(response, "img/slide-3.svg")
        self.assertContains(response, 'class="marquee"')
        self.assertContains(response, "Open any service in one tap")

    def test_uploaded_slide_photo_replaces_builtin_art(self):
        HeroSlide.objects.filter(display_order=1).update(image="slides/team.jpg")
        response = self.client.get("/")
        self.assertContains(response, "/media/slides/team.jpg")
        self.assertNotContains(response, "img/slide-1.svg")

    def test_unpublished_slide_hidden(self):
        HeroSlide.objects.filter(display_order=2).update(is_published=False)
        self.assertNotContains(self.client.get("/"), "Built for the way you work")

    def test_ticker_and_company_are_editable(self):
        SiteSettings.objects.filter(pk=1).update(company_name="Acme Works", ticker_text="Fast\n\nFriendly")
        response = self.client.get("/")
        self.assertContains(response, "Acme Works")
        self.assertContains(response, "<span>Friendly</span>", html=False)
        self.assertNotContains(response, "Open any service in one tap")

    def test_footer_social_links_only_show_when_set(self):
        response = self.client.get("/")
        self.assertNotContains(response, 'class="socials"')
        self.assertContains(response, "All rights reserved.")
        self.assertContains(response, 'href="https://billing.example.com"')  # services column

        SiteSettings.objects.filter(pk=1).update(
            instagram_url="https://instagram.com/muzira", whatsapp_url="https://wa.me/250788000000",
        )
        response = self.client.get("/")
        self.assertContains(response, 'class="socials"')
        self.assertContains(response, 'href="https://instagram.com/muzira"')
        self.assertContains(response, 'aria-label="WhatsApp (opens in a new tab)"')
        self.assertNotContains(response, 'class="social facebook"')

    def test_builtin_logo_and_uploaded_logo(self):
        response = self.client.get("/")
        self.assertContains(response, 'class="logo-mark"')
        self.assertContains(response, "muzira")
        SiteSettings.objects.filter(pk=1).update(logo="site/brand.png")
        response = self.client.get("/")
        self.assertContains(response, 'src="/media/site/brand.png"')
        self.assertNotContains(response, 'class="logo-mark"')

    def test_about_shows_live_stats(self):
        response = self.client.get("/about/")
        self.assertEqual(response.context["live_count"], 6)
        self.assertEqual(response.context["area_count"], 4)

    def test_about_lists_published_services(self):
        response = self.client.get("/about/")
        self.assertContains(response, "What we offer")
        self.assertContains(response, 'id="svc-hr-hub"')
        self.assertContains(response, "Leave requests, payslips and staff records")
        self.assertNotContains(response, "Analytics")

    def test_support_shows_status_and_faqs(self):
        Service.objects.filter(name="Bookings").update(status="maintenance")
        response = self.client.get("/support/")
        self.assertContains(response, "Maintenance")
        self.assertContains(response, "Do I need a separate login for each service?")
        self.assertNotContains(response, "Analytics")

    def test_contact_form_saves_and_emails_message(self):
        response = self.client.post("/contact/", {
            "name": "Ada", "email": "ada@example.org", "service": "Bookings", "message": "Hello there",
        }, follow=True)
        self.assertContains(response, "Thanks, Ada.")
        msg = ContactMessage.objects.get()
        self.assertEqual(msg.service, "Bookings")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, ["ada@example.org"])

    def test_contact_form_rejects_unpublished_service_and_missing_fields(self):
        response = self.client.post("/contact/", {"name": "", "email": "x", "service": "Analytics", "message": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(set(response.context["form"].errors), {"name", "email", "service", "message"})


class DashboardTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            "admin", "admin@example.org", "pass-12345", is_staff=True,
        )

    def login(self):
        self.client.force_login(self.staff)

    def test_dashboard_requires_staff_login(self):
        response = self.client.get("/dashboard/")
        self.assertRedirects(response, "/dashboard/login/?next=/dashboard/")

    def test_login_with_email(self):
        response = self.client.post("/dashboard/login/", {"username": "ADMIN@example.org", "password": "pass-12345"})
        self.assertRedirects(response, "/dashboard/")

    def test_non_staff_cannot_log_in(self):
        get_user_model().objects.create_user("bob", "bob@example.org", "pass-12345")
        response = self.client.post("/dashboard/login/", {"username": "bob@example.org", "password": "pass-12345"})
        self.assertContains(response, "can’t manage services")

    def test_add_service(self):
        self.login()
        response = self.client.post("/dashboard/", {
            "name": "Payroll", "category": "Finance", "description": "Run payroll.",
            "url": "https://pay.example.com", "color": "#ffd66b", "status": "online", "is_published": "on",
        }, follow=True)
        self.assertContains(response, "Added Payroll to the portal")
        service = Service.objects.get(name="Payroll")
        self.assertEqual(service.slug, "payroll")
        self.assertEqual(service.display_order, 8)
        entry = LogEntry.objects.get(object_id=str(service.pk))
        self.assertEqual(entry.action_flag, ADDITION)
        self.staff.is_superuser = True
        self.staff.save(update_fields=["is_superuser"])
        self.assertContains(
            self.client.get(reverse("admin:services_service_history", args=[service.pk])),
            "Added from the service dashboard.",
        )

    def test_add_service_with_image(self):
        self.login()
        with tempfile.TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            buf = io.BytesIO()
            Image.new("RGB", (32, 18), "#b8f5d0").save(buf, "PNG")
            upload = SimpleUploadedFile("tile.png", buf.getvalue(), content_type="image/png")
            response = self.client.post("/dashboard/", {
                "name": "Gallery", "category": "Media", "description": "Photos.",
                "url": "https://gallery.example.com", "color": "#ffd66b", "status": "online",
                "is_published": "on", "image": upload,
            }, follow=True)
            service = Service.objects.get(name="Gallery")
            self.assertTrue(service.image.name.startswith("services/tile"))
            self.assertTrue(service.image.url.startswith("/media/"))
            self.assertContains(self.client.get("/"), service.image.url)
            self.assertContains(response, f'src="{service.image.url}"')

    def test_add_service_rejects_non_http_url(self):
        self.login()
        response = self.client.post("/dashboard/", {
            "name": "Bad", "category": "X", "description": "d", "url": "ftp://files.example.com",
            "color": "#ffd66b", "status": "online",
        })
        self.assertContains(response, "The URL must start with http:// or https://")
        self.assertFalse(Service.objects.filter(name="Bad").exists())

    def test_edit_service(self):
        self.login()
        s = Service.objects.get(name="Bookings")
        self.client.post(f"/dashboard/?edit={s.pk}", {
            "name": "Bookings Pro", "category": "Customers", "description": s.description,
            "url": s.url, "color": s.color, "status": "online", "is_published": "on",
        })
        s.refresh_from_db()
        self.assertEqual(s.name, "Bookings Pro")
        entry = LogEntry.objects.filter(object_id=str(s.pk)).latest("action_time")
        self.assertEqual(entry.action_flag, CHANGE)

    def test_toggle_publish(self):
        self.login()
        s = Service.objects.get(name="Analytics")
        self.client.post(reverse("service_toggle", args=[s.pk]))
        s.refresh_from_db()
        self.assertTrue(s.is_published)

    def test_delete_and_undo(self):
        self.login()
        s = Service.objects.get(name="HR Hub")
        response = self.client.post(reverse("service_delete", args=[s.pk]), follow=True)
        self.assertContains(response, "Deleted HR Hub")
        self.assertContains(response, reverse("service_undo"))
        self.assertFalse(Service.objects.filter(name="HR Hub").exists())

        self.client.post(reverse("service_undo"))
        restored = Service.objects.get(name="HR Hub")
        self.assertEqual(restored.slug, "hr-hub")

    def test_reset_sample_data(self):
        self.login()
        Service.objects.all().delete()
        self.client.post(reverse("service_reset"))
        self.assertEqual(Service.objects.count(), 7)

    def test_actions_require_post_and_staff(self):
        s = Service.objects.first()
        self.assertEqual(self.client.post(reverse("service_delete", args=[s.pk])).status_code, 302)
        self.assertTrue(Service.objects.filter(pk=s.pk).exists())
        self.login()
        self.assertEqual(self.client.get(reverse("service_delete", args=[s.pk])).status_code, 405)


class WebImageTests(TestCase):
    def setUp(self):
        import tempfile
        self.media = tempfile.mkdtemp()
        self.override = self.settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        import shutil
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _png(self, size=(3000, 1500)):
        from io import BytesIO
        from PIL import Image
        buf = BytesIO()
        Image.new("RGB", size, "red").save(buf, "PNG")
        return buf.getvalue()

    def test_new_upload_is_stored_as_resized_webp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        s = Service.objects.create(
            name="Pics", description="d", url="https://x.example",
            image=SimpleUploadedFile("big.png", self._png(), content_type="image/png"),
        )
        self.assertTrue(s.image.name.endswith(".webp"))
        with Image.open(s.image.path) as img:
            self.assertEqual(img.format, "WEBP")
            self.assertEqual(max(img.size), 1000)

    def test_optimize_images_command_converts_existing_files(self):
        from django.core.files.base import ContentFile
        from django.core.management import call_command
        from io import StringIO
        s = Service.objects.create(name="Old", description="d", url="https://x.example")
        s.image.storage.save("services/old.png", ContentFile(self._png()))
        Service.objects.filter(pk=s.pk).update(image="services/old.png")
        out = StringIO()
        call_command("optimize_images", stdout=out)
        s.refresh_from_db()
        self.assertEqual(s.image.name, "services/old.webp")
        self.assertFalse(s.image.storage.exists("services/old.png"))
        self.assertIn("1 converted", out.getvalue())

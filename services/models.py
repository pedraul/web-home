from django.core.validators import URLValidator
from django.db import models
from django.utils.text import slugify


TILE_COLORS = [
    ("#b8f5d0", "Mint"),
    ("#ffd66b", "Sun"),
    ("#9fd0ff", "Sky"),
    ("#ffb3c7", "Rose"),
    ("#d6c2ff", "Lilac"),
    ("#ffc89e", "Peach"),
    ("#c9f0ff", "Ice"),
]


class SiteSettings(models.Model):
    company_name = models.CharField(max_length=100, default="Nexora")
    meta_description = models.CharField(
        max_length=200,
        default="Find the service you need and open it directly.",
    )
    logo = models.ImageField(
        upload_to="site/",
        blank=True,
        help_text="Optional. Leave empty to use the built-in muzira logo.",
    )
    ticker_text = models.TextField(
        "moving text",
        max_length=1000,
        default=(
            "One front door to every service\n"
            "Open any service in one tap\n"
            "Real help when you need it\n"
            "Built to keep your work moving"
        ),
        help_text="One phrase per line. These scroll across the home page.",
    )
    about_intro = models.CharField(
        max_length=240,
        default=(
            "One company, several focused services. Each service has its own team "
            "and its own website; the portal keeps them easy to find."
        ),
    )
    about_heading = models.CharField(max_length=80, default="What we do")
    about_body = models.TextField(
        max_length=1500,
        default=(
            "We provide business software and support services to small and "
            "mid-sized organisations. We built separate tools for separate jobs, "
            "so each one stays simple.\n\n"
            "This portal is the single address customers and staff need to remember."
        ),
    )
    contact_intro = models.CharField(
        max_length=240,
        default="Questions about a service, pricing or partnerships. We reply within one working day.",
    )
    contact_email = models.EmailField(
        default="hello@nexora.example",
        help_text="Shown on the site and receives contact form messages.",
    )
    contact_phone = models.CharField(max_length=40, blank=True, default="+27 21 555 0142")
    office_address = models.CharField(max_length=200, blank=True, default="12 Loop Street, Cape Town, 8001")
    office_hours = models.CharField(max_length=80, blank=True, default="Mon–Fri, 08:00–17:00")
    facebook_url = models.URLField("Facebook", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    x_url = models.URLField("X (Twitter)", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)
    youtube_url = models.URLField("YouTube", blank=True)
    tiktok_url = models.URLField("TikTok", blank=True)
    whatsapp_url = models.URLField(
        "WhatsApp",
        blank=True,
        help_text="Use the wa.me format, e.g. https://wa.me/250788000000",
    )
    support_intro = models.CharField(
        max_length=240,
        default=(
            "Most answers are here. For an account problem inside a service, use "
            "that service’s own help page."
        ),
    )

    class Meta:
        verbose_name = "website content"
        verbose_name_plural = "website content"

    def __str__(self):
        return f"Website content — {self.company_name}"

    @property
    def initials(self):
        return initials(self.company_name)

    SOCIAL_NETWORKS = [
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("x", "X"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
        ("whatsapp", "WhatsApp"),
    ]

    @property
    def social_links(self):
        return [
            {"key": key, "label": label, "url": getattr(self, f"{key}_url")}
            for key, label in self.SOCIAL_NETWORKS
            if getattr(self, f"{key}_url")
        ]

    @property
    def ticker_lines(self):
        return [line.strip() for line in self.ticker_text.splitlines() if line.strip()]


class HeroSlide(models.Model):
    title = models.CharField(max_length=80)
    caption = models.CharField(max_length=160, blank=True)
    image = models.ImageField(
        upload_to="slides/",
        blank=True,
        help_text="Wide photo, at least 1600×700. Leave empty to use a built-in illustration.",
    )
    display_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "home page slide"

    def __str__(self):
        return self.title


def initials(name):
    return "".join(word[0] for word in name.split())[:2].upper()


class Service(models.Model):
    STATUS_CHOICES = [
        ("online", "Online"),
        ("maintenance", "Maintenance"),
        ("offline", "Offline"),
    ]

    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=40, default="General")
    description = models.TextField(max_length=200)
    url = models.URLField(
        "service URL",
        validators=[URLValidator(schemes=["http", "https"])],
    )
    image = models.ImageField(upload_to="services/", blank=True, help_text="Optional picture shown on the service tile.")
    color = models.CharField("tile colour", max_length=7, choices=TILE_COLORS, default=TILE_COLORS[0][0])
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="online")
    is_published = models.BooleanField("publish on the portal", default=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return initials(self.name)

    @property
    def display_url(self):
        return self.url.split("://", 1)[-1]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:40] or "service"
            slug, n = base, 2
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)


class FaqItem(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField(max_length=1000)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "support question"

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    service = models.CharField(max_length=80, default="General enquiry")
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField("handled", default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.service}"

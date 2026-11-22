import django.core.validators
from django.db import migrations, models


def add_demo_services(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    Service.objects.bulk_create([
        Service(
            name="Client workspace",
            slug="client-workspace",
            tagline="Your projects, all in one place.",
            description="Keep up with project updates, shared files, and the next steps for your team.",
            url="https://example.com/client-workspace",
            category="For our clients",
            icon_label="CW",
            display_order=1,
        ),
        Service(
            name="Help center",
            slug="help-center",
            tagline="Answers when you need them.",
            description="Find useful guides and get help with the services you use every day.",
            url="https://example.com/help-center",
            category="Support",
            icon_label="HC",
            display_order=2,
        ),
        Service(
            name="Team portal",
            slug="team-portal",
            tagline="A better way to work together.",
            description="A single destination for your team’s tools, resources, and company updates.",
            url="https://example.com/team-portal",
            category="For our team",
            icon_label="TP",
            display_order=3,
        ),
    ])


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("slug", models.SlugField(unique=True)),
                ("tagline", models.CharField(max_length=120)),
                ("description", models.TextField(max_length=360)),
                ("url", models.URLField(validators=[django.core.validators.URLValidator(schemes=["http", "https"])])),
                ("category", models.CharField(default="Company service", max_length=40)),
                ("icon_label", models.CharField(default="↗", max_length=3)),
                ("is_published", models.BooleanField(default=True)),
                ("display_order", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"ordering": ["display_order", "name"]},
        ),
        migrations.RunPython(add_demo_services, migrations.RunPython.noop),
    ]

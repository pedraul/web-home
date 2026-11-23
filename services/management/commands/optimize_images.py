from django.core.management.base import BaseCommand

from services.images import to_webp
from services.models import HeroSlide, Service, SiteSettings


TARGETS = [
    (Service, "image", "service"),
    (HeroSlide, "image", "slide"),
    (SiteSettings, "logo", "logo"),
]


class Command(BaseCommand):
    help = "Convert every uploaded picture (services, slides, logo) to a resized WebP web image."

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-originals",
            action="store_true",
            help="Leave the original files in media/ instead of deleting them.",
        )

    def handle(self, *args, keep_originals=False, **options):
        converted = skipped = missing = failed = 0
        for model, attr, kind in TARGETS:
            for obj in model.objects.exclude(**{attr: ""}):
                field = getattr(obj, attr)
                label = f"{model._meta.verbose_name} “{obj}”"
                if not field.storage.exists(field.name):
                    self.stdout.write(self.style.WARNING(f"Missing file  {label}: {field.name} (upload it again)"))
                    missing += 1
                    continue
                old_name = field.name
                try:
                    changed = to_webp(field, kind)
                except ValueError as exc:
                    self.stdout.write(self.style.ERROR(f"Failed        {label}: {exc}"))
                    failed += 1
                    continue
                if not changed:
                    skipped += 1
                    continue
                obj.save(update_fields=[attr])
                if not keep_originals and old_name != field.name:
                    field.storage.delete(old_name)
                self.stdout.write(f"Converted     {label}: {old_name} -> {field.name}")
                converted += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {converted} converted, {skipped} already web images, "
            f"{missing} missing, {failed} failed."
        ))

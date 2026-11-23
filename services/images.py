"""Turn uploaded pictures into web-friendly images (resized WebP)."""
from io import BytesIO
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError


# Longest side, in pixels, for each kind of picture.
MAX_SIZES = {
    "slide": 1920,
    "service": 1000,
    "logo": 600,
}


def to_webp(field, kind, quality=82):
    """Convert the file in an ImageField to a resized WebP, in place.

    Returns True if the field now points to a new file. The model still has to
    be saved by the caller. Raises ValueError if the file is not a readable image.
    """
    if not field:
        return False
    max_side = MAX_SIZES[kind]
    field.open("rb")
    try:
        with Image.open(field) as img:
            img = ImageOps.exif_transpose(img)  # phone photos: respect rotation
            if (field.name.lower().endswith(".webp") and max(img.size) <= max_side):
                return False
            img.thumbnail((max_side, max_side), Image.LANCZOS)
            has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
            img = img.convert("RGBA" if has_alpha else "RGB")
            out = BytesIO()
            img.save(out, "WEBP", quality=quality, method=6)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"cannot read {field.name}: {exc}") from exc
    finally:
        field.close()

    name = PurePosixPath(field.name).stem + ".webp"
    field.save(name, ContentFile(out.getvalue()), save=False)
    return True

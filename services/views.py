from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .context_processors import get_site_settings
from .forms import ContactForm, EmailLoginForm, ServiceForm
from .models import ContactMessage, FaqItem, HeroSlide, Service
from .sample_data import reset_services


UNDO_KEY = "undo_service"
UNDO_FIELDS = ("name", "slug", "category", "description", "url", "color", "status", "is_published", "display_order")


BUILTIN_SLIDE_ART = ["img/slide-1.svg", "img/slide-2.svg", "img/slide-3.svg"]


def _categories(services):
    return list(dict.fromkeys(s.category for s in services))


def home(request):
    slides = list(HeroSlide.objects.filter(is_published=True))
    for i, slide in enumerate(slides):
        slide.art = BUILTIN_SLIDE_ART[i % len(BUILTIN_SLIDE_ART)]
    return render(request, "services/home.html", {
        "slides": slides,
        "services": Service.objects.filter(is_published=True),
    })


def about(request):
    services = Service.objects.filter(is_published=True)
    return render(request, "services/about.html", {
        "services": services,
        "live_count": services.count(),
        "area_count": len(_categories(services)),
    })


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        msg = form.save()
        site = get_site_settings()
        EmailMessage(
            subject=f"[{site.company_name}] {msg.service} — message from {msg.name}",
            body=f"From: {msg.name} <{msg.email}>\nService: {msg.service}\n\n{msg.message}",
            to=[site.contact_email],
            reply_to=[msg.email],
        ).send(fail_silently=True)
        messages.success(request, f"Thanks, {msg.name}. Your message is on its way; we reply within one working day.")
        return redirect("contact")
    return render(request, "services/contact.html", {"form": form})


def support(request):
    return render(request, "services/support.html", {
        "services": Service.objects.filter(is_published=True),
        "faqs": FaqItem.objects.filter(is_published=True),
    })


# --- Staff dashboard -------------------------------------------------------

class LoginView(auth_views.LoginView):
    template_name = "services/dashboard/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True


staff_required = staff_member_required(login_url="dashboard_login")


@staff_required
def dashboard(request):
    editing = None
    if edit_id := request.GET.get("edit"):
        editing = Service.objects.filter(pk=edit_id).first()

    form = ServiceForm(request.POST or None, request.FILES or None, instance=editing)
    if request.method == "POST" and form.is_valid():
        service = form.save()
        if editing:
            messages.success(request, f"Saved {service.name}")
        else:
            where = "to the portal" if service.is_published else "as a draft"
            messages.success(request, f"Added {service.name} {where}")
        return redirect("dashboard")

    services = list(Service.objects.all())
    published = sum(s.is_published for s in services)
    return render(request, "services/dashboard/index.html", {
        "services": services,
        "form": form,
        "editing": editing,
        "published_count": published,
        "draft_count": len(services) - published,
        "new_message_count": ContactMessage.objects.filter(is_handled=False).count(),
        "category_options": _categories(services),
    })


@require_POST
@staff_required
def toggle_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_published = not service.is_published
    service.save(update_fields=["is_published"])
    messages.success(request, f"{service.name} {'published' if service.is_published else 'moved to drafts'}")
    return redirect("dashboard")


@require_POST
@staff_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    request.session[UNDO_KEY] = {f: getattr(service, f) for f in UNDO_FIELDS} | {"image": service.image.name}
    service.delete()
    messages.success(request, f"Deleted {service.name}", extra_tags="undo")
    return redirect("dashboard")


@require_POST
@staff_required
def undo_delete(request):
    data = request.session.pop(UNDO_KEY, None)
    if data:
        if Service.objects.filter(slug=data["slug"]).exists():
            data["slug"] = ""
        service = Service.objects.create(**data)
        messages.success(request, f"Restored {service.name}")
    return redirect("dashboard")


@require_POST
@staff_required
def reset_sample_data(request):
    reset_services(Service)
    request.session.pop(UNDO_KEY, None)
    messages.success(request, "Sample data restored")
    return redirect(reverse("dashboard"))

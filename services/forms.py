from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import ContactMessage, Service


GENERAL_ENQUIRY = "General enquiry"


class ContactForm(forms.ModelForm):
    service = forms.ChoiceField()

    class Meta:
        model = ContactMessage
        fields = ("name", "email", "service", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        names = Service.objects.filter(is_published=True).values_list("name", flat=True)
        self.fields["service"].choices = [(GENERAL_ENQUIRY, GENERAL_ENQUIRY)] + [(n, n) for n in names]
        self.fields["name"].widget.attrs["autocomplete"] = "name"
        self.fields["email"].widget.attrs["autocomplete"] = "email"


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ("name", "category", "description", "url", "image", "color", "status", "is_published")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "url": forms.URLInput(attrs={"placeholder": "https://"}),
            "color": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget.attrs["list"] = "catList"

    def clean_url(self):
        url = self.cleaned_data["url"].strip()
        if not url.lower().startswith(("http://", "https://")):
            raise forms.ValidationError("The URL must start with http:// or https://")
        return url

    def save(self, commit=True):
        service = super().save(commit=False)
        if service.pk is None:
            last = Service.objects.order_by("-display_order").first()
            service.display_order = (last.display_order + 1) if last else 1
        if commit:
            service.save()
        return service


class EmailLoginForm(AuthenticationForm):
    """Sign in with an email address (or username); staff accounts only."""

    username = forms.CharField(
        label="Email",
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"}),
    )

    def clean(self):
        identifier = self.cleaned_data.get("username")
        if identifier and "@" in identifier:
            user = (
                get_user_model()._default_manager.filter(email__iexact=identifier).order_by("pk").first()
            )
            if user:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "This account can’t manage services. Ask an administrator for access.",
                code="not_staff",
            )

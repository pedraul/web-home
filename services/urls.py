from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("support/", views.support, name="support"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/admin/", RedirectView.as_view(pattern_name="admin:index")),
    path("dashboard/login/", views.LoginView.as_view(), name="dashboard_login"),
    path("dashboard/logout/", auth_views.LogoutView.as_view(next_page="home"), name="dashboard_logout"),
    path("dashboard/services/<int:pk>/toggle/", views.toggle_service, name="service_toggle"),
    path("dashboard/services/<int:pk>/delete/", views.delete_service, name="service_delete"),
    path("dashboard/services/undo/", views.undo_delete, name="service_undo"),
    path("dashboard/services/reset/", views.reset_sample_data, name="service_reset"),
]

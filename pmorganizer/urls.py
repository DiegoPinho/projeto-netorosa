"""
URL configuration for pmorganizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from cadastros import auth_views as cadastros_auth_views
from cadastros import public_views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path(
        "trabalhe-conosco/",
        public_views.CandidateApplicationCreateView.as_view(),
        name="candidate_application",
    ),
    path(
        "solicitar-proposta/",
        public_views.ProposalRequestCreateView.as_view(),
        name="proposal_request",
    ),
    path("forms/", TemplateView.as_view(template_name="forms.html"), name="forms"),
    path("cadastros/", TemplateView.as_view(template_name="cadastros.html"), name="cadastros"),
    path(
        "area-restrita/login/",
        cadastros_auth_views.PlatformLoginView.as_view(),
        name="login",
    ),
    path("area-restrita/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "area-restrita/senha/trocar/",
        cadastros_auth_views.PasswordChangeRequestView.as_view(),
        name="password_change_request",
    ),
    path(
        "area-restrita/senha/alterar/",
        cadastros_auth_views.PlatformPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "area-restrita/senha/alterada/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path(
        "area-restrita/senha/esqueci/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "area-restrita/senha/esqueci/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "area-restrita/senha/reset/<uidb64>/<token>/",
        cadastros_auth_views.PlatformPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "area-restrita/senha/reset/concluido/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path(
        "app/",
        include(("cadastros.web_urls", "cadastros_web"), namespace="cadastros_web"),
    ),
    path("admin/", admin.site.urls),
    path("api/", include("cadastros.urls")),
    path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

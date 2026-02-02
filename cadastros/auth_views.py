from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from .forms import PasswordChangeRequestForm


class PlatformLoginView(auth_views.LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        url = super().get_success_url()
        user = self.request.user
        profile = getattr(user, "profile", None)
        if profile and profile.must_change_password:
            return reverse("password_change")
        return url


class PlatformPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("password_change_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = getattr(self.request.user, "profile", None)
        if profile and profile.must_change_password:
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])
        return response


class PlatformPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = getattr(form, "user", None)
        profile = getattr(user, "profile", None) if user else None
        if profile and profile.must_change_password:
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])
        return response


class PasswordChangeRequestView(FormView):
    template_name = "registration/password_change_request.html"
    form_class = PasswordChangeRequestForm
    success_url = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("password_change")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        profile = getattr(user, "profile", None)
        if profile and profile.must_change_password:
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])
        messages.success(self.request, "Senha atualizada. Entre com a nova senha.")
        return super().form_valid(form)

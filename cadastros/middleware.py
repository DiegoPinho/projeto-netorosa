from __future__ import annotations

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._allowed_paths = None

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "profile", None)
            if profile and profile.must_change_password:
                if not self._is_allowed_path(request.path):
                    return redirect("password_change")
        return self.get_response(request)

    def _is_allowed_path(self, path: str) -> bool:
        if path in self._get_allowed_paths():
            return True
        static_url = getattr(settings, "STATIC_URL", "")
        if static_url and path.startswith(static_url):
            return True
        media_url = getattr(settings, "MEDIA_URL", "")
        if media_url and path.startswith(media_url):
            return True
        return False

    def _get_allowed_paths(self) -> set[str]:
        if self._allowed_paths is None:
            self._allowed_paths = {
                reverse("password_change"),
                reverse("password_change_done"),
                reverse("logout"),
            }
        return self._allowed_paths

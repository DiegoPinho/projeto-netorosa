from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile, UserRole

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    role = UserRole.ADMIN if instance.is_superuser or instance.is_staff else UserRole.CONSULTANT
    UserProfile.objects.get_or_create(
        user=instance,
        defaults={"role": role, "must_change_password": True},
    )

from __future__ import annotations

from django.db.models import QuerySet

from .models import ProjectVisibility, UserProfile, UserRole


def resolve_user_role(user) -> str | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if user.is_superuser or user.is_staff:
        return UserRole.ADMIN
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return UserRole.CONSULTANT


def can_view_financial(user) -> bool:
    return resolve_user_role(user) == UserRole.ADMIN


def filter_projects_for_user(queryset: QuerySet, user) -> QuerySet:
    role = resolve_user_role(user)
    if role == UserRole.ADMIN:
        return queryset
    if role == UserRole.GP_INTERNAL:
        return queryset.filter(internal_manager=user)
    if role == UserRole.GP_EXTERNAL:
        return queryset.filter(external_manager=user)
    if role == UserRole.CLIENT:
        return queryset.filter(client_user=user)
    if role == UserRole.CONSULTANT:
        return queryset.filter(activities__consultants__user=user).distinct()
    return queryset.none()


def filter_activities_for_user(queryset: QuerySet, user) -> QuerySet:
    role = resolve_user_role(user)
    if role == UserRole.ADMIN:
        return queryset
    if role == UserRole.GP_INTERNAL:
        return queryset.filter(project__internal_manager=user)
    if role == UserRole.GP_EXTERNAL:
        return queryset.filter(project__external_manager=user)
    if role == UserRole.CLIENT:
        return queryset.filter(project__client_user=user, client_visible=True)
    if role == UserRole.CONSULTANT:
        return queryset.filter(consultants__user=user)
    return queryset.none()


def allowed_project_visibility(role: str | None) -> set[str]:
    if role == UserRole.ADMIN:
        return set(ProjectVisibility.values)
    if role == UserRole.GP_INTERNAL:
        return {
            ProjectVisibility.ALL,
            ProjectVisibility.MANAGEMENT,
            ProjectVisibility.TEAM,
            ProjectVisibility.EXTERNAL_TEAM,
        }
    if role == UserRole.GP_EXTERNAL:
        return {ProjectVisibility.ALL, ProjectVisibility.EXTERNAL_TEAM}
    if role == UserRole.CONSULTANT:
        return {
            ProjectVisibility.ALL,
            ProjectVisibility.TEAM,
            ProjectVisibility.EXTERNAL_TEAM,
        }
    if role == UserRole.CLIENT:
        return {ProjectVisibility.ALL}
    return set()


def filter_by_visibility(
    queryset: QuerySet,
    role: str | None,
    field_name: str = "visibility",
) -> QuerySet:
    allowed = allowed_project_visibility(role)
    if not allowed:
        return queryset.none()
    return queryset.filter(**{f"{field_name}__in": allowed})

from __future__ import annotations

from typing import Iterable

from django.db import models
from django.utils import formats, timezone

from .models import Project, ProjectObservation, ProjectObservationType

PROJECT_CHANGE_FIELDS: tuple[str, ...] = (
    "billing_client",
    "project_client",
    "description",
    "cloud_environment",
    "database_type",
    "hml_url",
    "prd_url",
    "senior_client_code",
    "senior_project_code",
    "received_date",
    "planned_go_live_date",
    "explanation",
    "project_type",
    "contract_type",
    "criticality",
    "status",
    "total_value",
    "hourly_rate",
    "contingency_percent",
    "internal_manager",
    "external_manager",
    "client_user",
)


def _format_project_field(instance: Project, field_name: str) -> str:
    if instance is None:
        return "-"
    model_field = instance._meta.get_field(field_name)
    value = getattr(instance, field_name, None)
    if value in {None, ""}:
        return "-"
    if model_field.choices:
        display = getattr(instance, f"get_{field_name}_display", None)
        if display:
            return display()
    if isinstance(model_field, models.DateTimeField):
        value = timezone.localtime(value) if timezone.is_aware(value) else value
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(model_field, models.DateField):
        return value.strftime("%d/%m/%Y")
    if isinstance(model_field, models.DecimalField):
        return formats.number_format(
            value,
            decimal_pos=model_field.decimal_places,
            use_l10n=True,
            force_grouping=True,
        )
    if isinstance(model_field, models.BooleanField):
        return "Sim" if value else "Nao"
    return str(value)


def _normalize_project_field(instance: Project, field_name: str):
    if instance is None:
        return None
    model_field = instance._meta.get_field(field_name)
    if isinstance(model_field, models.ForeignKey):
        return getattr(instance, f"{field_name}_id")
    return getattr(instance, field_name, None)


def build_project_changes(
    before: Project,
    after: Project,
    fields: Iterable[str] | None = None,
) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for field_name in fields or PROJECT_CHANGE_FIELDS:
        model_field = after._meta.get_field(field_name)
        before_value = _normalize_project_field(before, field_name)
        after_value = _normalize_project_field(after, field_name)
        if before_value == after_value:
            continue
        changes.append(
            {
                "field": field_name,
                "label": str(model_field.verbose_name),
                "before": _format_project_field(before, field_name),
                "after": _format_project_field(after, field_name),
            }
        )
    return changes


def create_project_change_observation(
    before: Project,
    after: Project,
    user,
) -> ProjectObservation | None:
    changes = build_project_changes(before, after)
    if not changes:
        return None
    return ProjectObservation.objects.create(
        project=after,
        observation_type=ProjectObservationType.CHANGE,
        note="Alteracoes no cadastro do projeto.",
        changes=changes,
        created_by=user,
    )


def create_project_receipt_observation(
    project: Project,
    user,
    previous_date=None,
) -> ProjectObservation | None:
    if not project.received_date:
        return None
    if previous_date and previous_date == project.received_date:
        return None
    if previous_date:
        note = (
            "Data de recebimento atualizada: "
            f"{previous_date.strftime('%d/%m/%Y')} -> "
            f"{project.received_date.strftime('%d/%m/%Y')}."
        )
    else:
        note = (
            "Recebimento do projeto pela consultoria em "
            f"{project.received_date.strftime('%d/%m/%Y')}."
        )
    return ProjectObservation.objects.create(
        project=project,
        observation_type=ProjectObservationType.AUTO,
        note=note,
        created_by=user,
    )

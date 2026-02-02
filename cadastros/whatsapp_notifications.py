from decimal import Decimal

from django.db.models import Q
from django.utils import formats, timezone

from .models import (
    AccountsPayable,
    AccountsReceivable,
    ActivityStatus,
    Consultant,
    FinancialStatus,
    ProjectActivity,
    Ticket,
    TicketReply,
    TimeEntry,
    TimeEntryStatus,
    WhatsappSettings,
)
from .whatsapp_client import normalize_phone, send_text


def _format_decimal(value: Decimal | None) -> str:
    return formats.number_format(
        value or Decimal("0.00"),
        decimal_pos=2,
        use_l10n=True,
        force_grouping=True,
    )


def _format_currency(value: Decimal | None) -> str:
    return f"R$ {_format_decimal(value)}"


def _format_date(value) -> str:
    return value.strftime("%d/%m/%Y") if value else "-"


def _format_period(start_date, end_date) -> str:
    if not start_date:
        return "-"
    start_label = start_date.strftime("%d/%m/%Y")
    end_label = end_date.strftime("%d/%m/%Y") if end_date else "-"
    if start_label == end_label:
        return start_label
    return f"{start_label} a {end_label}"


def _split_numbers(text: str | None) -> list[str]:
    if not text:
        return []
    numbers = []
    for line in text.splitlines():
        normalized = normalize_phone(line)
        if normalized:
            numbers.append(normalized)
    return numbers


def _get_admin_numbers() -> list[str]:
    settings = WhatsappSettings.objects.first()
    if not settings:
        return []
    return _split_numbers(settings.financial_numbers)


def _get_opportunity_numbers() -> list[str]:
    settings = WhatsappSettings.objects.first()
    if not settings:
        return []
    return _split_numbers(settings.opportunities_numbers)


def _send_to_numbers(numbers: list[str], message: str) -> None:
    for phone in numbers:
        send_text(phone, message)


def _send_to_consultant(consultant: Consultant | None, message: str) -> None:
    if not consultant:
        return
    phone = normalize_phone(consultant.whatsapp_phone)
    if not phone:
        return
    send_text(phone, message)


def _resolve_user_label(user) -> str:
    if not user:
        return "-"
    consultant = getattr(user, "consultant_profile", None)
    if consultant and getattr(consultant, "full_name", ""):
        return consultant.full_name
    full_name = ""
    if hasattr(user, "get_full_name"):
        full_name = (user.get_full_name() or "").strip()
    if full_name:
        return full_name
    email = getattr(user, "email", "") or ""
    if email:
        return email
    return str(user)


def _clean_text(value) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text or "-"


def _short_text(value, limit: int = 400) -> str:
    text = _clean_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _consultant_from_user(user) -> Consultant | None:
    if not user:
        return None
    consultant = getattr(user, "consultant_profile", None)
    if consultant:
        return consultant
    return Consultant.objects.filter(user=user).first()


def _profile_phone(user) -> str:
    if not user:
        return ""
    profile = getattr(user, "profile", None)
    if not profile:
        return ""
    return normalize_phone(getattr(profile, "whatsapp_phone", "") or "")


def _collect_ticket_numbers(ticket: Ticket) -> list[str]:
    numbers = set(_get_admin_numbers())
    if ticket.consultant_responsible:
        phone = normalize_phone(ticket.consultant_responsible.whatsapp_phone)
        if phone:
            numbers.add(phone)
    opener_phone = _profile_phone(ticket.created_by)
    if opener_phone:
        numbers.add(opener_phone)
    opener = _consultant_from_user(ticket.created_by)
    if opener:
        phone = normalize_phone(opener.whatsapp_phone)
        if phone:
            numbers.add(phone)
    return list(numbers)


def _build_ticket_message(ticket: Ticket, prefix: str, extra: str | None = None) -> str:
    activity_label = "-"
    if ticket.activity_id:
        activity_label = _clean_text(ticket.activity.activity)
    message = (
        f"{prefix}\n"
        f"Titulo: {_clean_text(ticket.title)}\n"
        f"Projeto: {_clean_text(ticket.project)}\n"
        f"Atividade: {activity_label}\n"
        f"Tipo do chamado: {_clean_text(ticket.get_ticket_type_display())}\n"
        f"Criticidade: {_clean_text(ticket.get_criticality_display())}\n"
        f"Descricao: {_short_text(ticket.description)}"
    )
    if extra:
        message = f"{message}\n{extra}"
    return message


def notify_admin_receivable_created(receivable: AccountsReceivable) -> None:
    numbers = _get_admin_numbers()
    if not numbers:
        return
    message = (
        "Titulo a receber criado.\n"
        f"Cliente: {receivable.client}\n"
        f"Titulo: {receivable.document_number}\n"
        f"Valor: {_format_currency(receivable.total_amount())}\n"
        f"Vencimento: {_format_date(receivable.due_date)}\n"
        f"ID: {receivable.id or '-'}"
    )
    _send_to_numbers(numbers, message)


def notify_admin_receivable_paid(receivable: AccountsReceivable) -> None:
    numbers = _get_admin_numbers()
    if not numbers:
        return
    message = (
        "Titulo a receber pago.\n"
        f"Cliente: {receivable.client}\n"
        f"Titulo: {receivable.document_number}\n"
        f"Valor: {_format_currency(receivable.total_amount())}\n"
        f"Pago em: {_format_date(receivable.settlement_date)}\n"
        f"ID: {receivable.id or '-'}"
    )
    _send_to_numbers(numbers, message)


def _payable_party_label(payable: AccountsPayable) -> str:
    if payable.consultant_id:
        return str(payable.consultant)
    return str(payable.supplier)


def notify_admin_payable_created(payable: AccountsPayable) -> None:
    numbers = _get_admin_numbers()
    if not numbers:
        return
    message = (
        "Titulo a pagar criado.\n"
        f"Fornecedor/Consultor: {_payable_party_label(payable)}\n"
        f"Titulo: {payable.document_number}\n"
        f"Valor: {_format_currency(payable.total_amount())}\n"
        f"Vencimento: {_format_date(payable.due_date)}\n"
        f"ID: {payable.id or '-'}"
    )
    _send_to_numbers(numbers, message)


def notify_admin_payable_paid(payable: AccountsPayable) -> None:
    numbers = _get_admin_numbers()
    if not numbers:
        return
    message = (
        "Titulo a pagar pago.\n"
        f"Fornecedor/Consultor: {_payable_party_label(payable)}\n"
        f"Titulo: {payable.document_number}\n"
        f"Valor: {_format_currency(payable.total_amount())}\n"
        f"Pago em: {_format_date(payable.settlement_date)}\n"
        f"ID: {payable.id or '-'}"
    )
    _send_to_numbers(numbers, message)


def notify_consultant_payable_created(payable: AccountsPayable) -> None:
    consultant = payable.consultant
    if not consultant:
        return
    message = (
        "Seu titulo a receber foi criado.\n"
        f"Titulo: {payable.document_number}\n"
        f"Valor: {_format_currency(payable.total_amount())}\n"
        f"Vencimento: {_format_date(payable.due_date)}\n"
        f"ID: {payable.id or '-'}"
    )
    _send_to_consultant(consultant, message)


def notify_consultant_payable_paid(payable: AccountsPayable) -> None:
    consultant = payable.consultant
    if not consultant:
        return
    message = (
        "Seu titulo foi pago.\n"
        f"Titulo: {payable.document_number}\n"
        f"Valor: {_format_currency(payable.total_amount())}\n"
        f"Pago em: {_format_date(payable.settlement_date)}\n"
        f"ID: {payable.id or '-'}"
    )
    _send_to_consultant(consultant, message)


def notify_time_entry_pending(entry: TimeEntry) -> None:
    numbers = _get_admin_numbers()
    if not numbers:
        return
    period = _format_period(entry.start_date, entry.end_date)
    hours = f"{_format_decimal(entry.total_hours)}h"
    message = (
        "Apontamento aguardando aprovacao.\n"
        f"Consultor: {entry.consultant}\n"
        f"Projeto: {entry.activity.project}\n"
        f"Atividade: {entry.activity.activity}\n"
        f"Periodo: {period}\n"
        f"Horas: {hours}\n"
        f"ID: {entry.id or '-'}"
    )
    _send_to_numbers(numbers, message)


def notify_time_entry_reviewed(entry: TimeEntry) -> None:
    if entry.status not in {TimeEntryStatus.APPROVED, TimeEntryStatus.REJECTED}:
        return
    period = _format_period(entry.start_date, entry.end_date)
    hours = f"{_format_decimal(entry.total_hours)}h"
    if entry.status == TimeEntryStatus.APPROVED:
        message = (
            "Seu apontamento foi aprovado.\n"
            f"Projeto: {entry.activity.project}\n"
            f"Atividade: {entry.activity.activity}\n"
            f"Periodo: {period}\n"
            f"Horas: {hours}"
        )
    else:
        reason = entry.rejection_reason.strip() if entry.rejection_reason else "-"
        message = (
            "Seu apontamento foi rejeitado.\n"
            f"Projeto: {entry.activity.project}\n"
            f"Atividade: {entry.activity.activity}\n"
            f"Periodo: {period}\n"
            f"Horas: {hours}\n"
            f"Motivo: {reason}"
        )
    _send_to_consultant(entry.consultant, message)


def notify_consultant_billing_closure(
    consultant: Consultant,
    period_start,
    period_end,
    hours: Decimal,
    total: Decimal,
    payment_date,
) -> None:
    period = _format_period(period_start, period_end)
    message = (
        "Fechamento concluido.\n"
        f"Periodo: {period}\n"
        f"Horas faturadas: {_format_decimal(hours)}h\n"
        f"Valor a receber: {_format_currency(total)}\n"
        f"Previsao de pagamento: {_format_date(payment_date)}"
    )
    _send_to_consultant(consultant, message)


def notify_consultant_activity_assigned(
    activity: ProjectActivity,
    consultants: list[Consultant],
) -> None:
    if not consultants:
        return
    subactivities = activity.subactivities_label() or "-"
    message = (
        "Atividade atribuida.\n"
        f"Projeto: {activity.project}\n"
        f"Fase: {activity.phase}\n"
        f"Produto: {activity.product}\n"
        f"Modulo: {activity.module}\n"
        f"SubModulo: {activity.submodule}\n"
        f"Atividade: {activity.activity}\n"
        f"Subatividades: {subactivities}\n"
        f"Criticidade: {activity.get_criticality_display()}\n"
        f"Dias: {_format_decimal(activity.days)}\n"
        f"Horas: {_format_decimal(activity.hours)}h\n"
        f"Inicio previsto: {_format_date(activity.planned_start)}"
    )
    for consultant in consultants:
        _send_to_consultant(consultant, message)


def _activity_queryset():
    return (
        ProjectActivity.objects.select_related(
            "project",
            "phase",
            "product",
            "module",
            "submodule",
        )
        .prefetch_related("consultants", "subactivity_items")
        .exclude(status__in=[ActivityStatus.DONE, ActivityStatus.CANCELED])
    )


def _send_activity_report(activity: ProjectActivity, label: str) -> int:
    consultants = list(activity.consultants.all())
    if not consultants:
        return 0
    subactivities = activity.subactivities_label() or "-"
    message = (
        f"Atividade {label}.\n"
        f"Projeto: {activity.project}\n"
        f"Fase: {activity.phase}\n"
        f"Produto: {activity.product}\n"
        f"Modulo: {activity.module}\n"
        f"SubModulo: {activity.submodule}\n"
        f"Atividade: {activity.activity}\n"
        f"Subatividades: {subactivities}\n"
        f"Criticidade: {activity.get_criticality_display()}\n"
        f"Dias: {_format_decimal(activity.days)}\n"
        f"Horas: {_format_decimal(activity.hours)}h\n"
        f"Inicio previsto: {_format_date(activity.planned_start)}"
    )
    for consultant in consultants:
        _send_to_consultant(consultant, message)
    return len(consultants)


def notify_consultant_activities_today(target_date=None) -> int:
    day = target_date or timezone.localdate()
    date_filter = (
        Q(planned_start__lte=day, planned_end__gte=day)
        | Q(planned_start=day, planned_end__isnull=True)
        | Q(planned_end=day, planned_start__isnull=True)
    )
    activities = (
        _activity_queryset()
        .filter(date_filter)
        .filter(consultants__isnull=False)
        .distinct()
    )
    sent = 0
    for activity in activities:
        sent += _send_activity_report(activity, "de hoje")
    return sent


def notify_consultant_overdue_activities(reference_date=None) -> int:
    day = reference_date or timezone.localdate()
    activities = (
        _activity_queryset()
        .filter(planned_end__lt=day)
        .filter(consultants__isnull=False)
        .distinct()
    )
    sent = 0
    for activity in activities:
        sent += _send_activity_report(activity, "em atraso")
    return sent


def notify_admin_titles_due_today(target_date=None) -> int:
    day = target_date or timezone.localdate()
    numbers = _get_admin_numbers()
    if not numbers:
        return 0
    receivables = (
        AccountsReceivable.objects.select_related("client")
        .filter(due_date=day)
        .exclude(status__in=[FinancialStatus.PAID, FinancialStatus.CANCELED])
    )
    payables = (
        AccountsPayable.objects.select_related("supplier", "consultant")
        .filter(due_date=day)
        .exclude(status__in=[FinancialStatus.PAID, FinancialStatus.CANCELED])
    )
    sent = 0
    for receivable in receivables:
        message = (
            "Titulo a receber vencendo hoje.\n"
            f"Cliente: {receivable.client}\n"
            f"Titulo: {receivable.document_number}\n"
            f"Valor: {_format_currency(receivable.total_amount())}\n"
            f"Vencimento: {_format_date(receivable.due_date)}\n"
            f"ID: {receivable.id or '-'}"
        )
        _send_to_numbers(numbers, message)
        sent += 1
    for payable in payables:
        message = (
            "Titulo a pagar vencendo hoje.\n"
            f"Fornecedor/Consultor: {_payable_party_label(payable)}\n"
            f"Titulo: {payable.document_number}\n"
            f"Valor: {_format_currency(payable.total_amount())}\n"
            f"Vencimento: {_format_date(payable.due_date)}\n"
            f"ID: {payable.id or '-'}"
        )
        _send_to_numbers(numbers, message)
        sent += 1
    return sent


def dispatch_daily_whatsapp_reports(now=None, force: bool = False) -> dict[str, int]:
    current = now or timezone.localtime()
    today = current.date()
    settings = WhatsappSettings.objects.first()
    results = {
        "activities_today": 0,
        "activities_overdue": 0,
        "admin_due_titles": 0,
    }
    if not settings:
        return results

    def should_send(schedule_time, last_sent) -> bool:
        if not schedule_time:
            return False
        if not force and last_sent == today:
            return False
        if force:
            return True
        return (
            schedule_time.hour == current.time().hour
            and schedule_time.minute == current.time().minute
        )

    update_fields = []
    if should_send(settings.daily_activities_time, settings.last_daily_activities_sent):
        results["activities_today"] = notify_consultant_activities_today(today)
        settings.last_daily_activities_sent = today
        update_fields.append("last_daily_activities_sent")
    if should_send(settings.daily_overdue_time, settings.last_daily_overdue_sent):
        results["activities_overdue"] = notify_consultant_overdue_activities(today)
        settings.last_daily_overdue_sent = today
        update_fields.append("last_daily_overdue_sent")
    if should_send(settings.daily_admin_due_time, settings.last_daily_admin_due_sent):
        results["admin_due_titles"] = notify_admin_titles_due_today(today)
        settings.last_daily_admin_due_sent = today
        update_fields.append("last_daily_admin_due_sent")

    if update_fields:
        settings.save(update_fields=update_fields)

    return results


def notify_opportunity_candidate(user, demand: dict) -> bool:
    numbers = _get_opportunity_numbers()
    consultant = getattr(user, "consultant_profile", None)
    if not numbers and not (consultant and normalize_phone(consultant.whatsapp_phone)):
        return False
    demand_id = _clean_text(demand.get("idDemanda") or demand.get("id"))
    title = _clean_text(demand.get("titulo"))
    client = _clean_text(demand.get("nomeERP"))
    product = _clean_text(demand.get("produto"))
    demand_type = _clean_text(demand.get("tipoDemanda"))
    service_type = _clean_text(demand.get("tipoAtendimento"))
    scope_type = _clean_text(demand.get("tipoEscopo"))
    model_type = _clean_text(demand.get("tipoModelo"))
    hours_raw = demand.get("horasvalor")
    hours_label = f"{hours_raw}h" if hours_raw not in (None, "", "-") else "-"
    start_label = _clean_text(demand.get("previsaoInicio"))
    end_label = _clean_text(demand.get("previsaoFim"))
    urgent_label = "Sim" if demand.get("urgente") else "Nao"
    status_label = _clean_text(demand.get("status"))
    user_label = _resolve_user_label(user)

    message = (
        "Candidatura para oportunidade.\n"
        f"Solicitante: {user_label}\n"
        f"Demanda: {demand_id} - {title}\n"
        f"Cliente: {client}\n"
        f"Produto: {product}\n"
        f"Tipo: {demand_type}\n"
        f"Atendimento: {service_type}\n"
        f"Escopo: {scope_type}\n"
        f"Modelo: {model_type}\n"
        f"Horas: {hours_label}\n"
        f"Inicio: {start_label}\n"
        f"Fim: {end_label}\n"
        f"Urgente: {urgent_label}\n"
        f"Status: {status_label}"
    )
    if numbers:
        _send_to_numbers(numbers, message)
    if consultant:
        _send_to_consultant(consultant, message)
    return True


def notify_ticket_created(ticket: Ticket) -> None:
    numbers = _collect_ticket_numbers(ticket)
    if not numbers:
        return
    message = _build_ticket_message(ticket, "Chamado aberto.")
    _send_to_numbers(numbers, message)


def notify_ticket_reply(ticket: Ticket, reply: TicketReply) -> None:
    numbers = _collect_ticket_numbers(ticket)
    if not numbers:
        return
    author = _resolve_user_label(reply.author)
    extra = f"Tramite: {_short_text(reply.message)}\nAutor: {author}"
    message = _build_ticket_message(ticket, "Novo tramite no chamado.", extra=extra)
    _send_to_numbers(numbers, message)


def notify_ticket_updated(ticket: Ticket) -> None:
    numbers = _collect_ticket_numbers(ticket)
    if not numbers:
        return
    message = _build_ticket_message(ticket, "Chamado atualizado.")
    _send_to_numbers(numbers, message)


def notify_ticket_closed(ticket: Ticket) -> None:
    numbers = _collect_ticket_numbers(ticket)
    if not numbers:
        return
    message = _build_ticket_message(ticket, "Chamado encerrado.")
    _send_to_numbers(numbers, message)

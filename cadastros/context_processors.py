from __future__ import annotations

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from .models import (
    AccountsPayable,
    AccountsReceivable,
    ActivityStatus,
    FinancialStatus,
    ProjectActivity,
    Ticket,
    TicketReply,
    TicketStatus,
)
from .roles import (
    can_view_financial,
    filter_activities_for_user,
    resolve_user_role,
)


def _append_notification(notifications, label: str, count: int, url: str = "") -> None:
    if count <= 0:
        return
    notifications.append(
        {
            "label": label,
            "count": int(count),
            "url": url,
        }
    )


def _build_notifications(user):
    payload = {
        "items": [],
        "ticket_open": 0,
        "ticket_reply": 0,
    }
    if not user or not getattr(user, "is_authenticated", False):
        return payload

    notifications = payload["items"]
    today = timezone.localdate()
    since = timezone.now() - timedelta(days=7)

    if can_view_financial(user):
        due_statuses = (FinancialStatus.OPEN, FinancialStatus.OVERDUE)
        receivable_due = AccountsReceivable.objects.filter(
            due_date=today,
            status__in=due_statuses,
        ).count()
        _append_notification(
            notifications,
            "Titulo a receber vencendo hoje"
            if receivable_due == 1
            else "Titulos a receber vencendo hoje",
            receivable_due,
            reverse("cadastros_web:accounts_receivable_list"),
        )
        payable_due = AccountsPayable.objects.filter(
            due_date=today,
            status__in=due_statuses,
        ).count()
        _append_notification(
            notifications,
            "Titulo a pagar vencendo hoje"
            if payable_due == 1
            else "Titulos a pagar vencendo hoje",
            payable_due,
            reverse("cadastros_web:accounts_payable_list"),
        )

        receivable_paid = AccountsReceivable.objects.filter(
            settlement_date=today,
            status=FinancialStatus.PAID,
        ).count()
        _append_notification(
            notifications,
            "Recebimento de titulo realizado hoje"
            if receivable_paid == 1
            else "Recebimentos de titulos realizados hoje",
            receivable_paid,
            reverse("cadastros_web:accounts_receivable_list"),
        )
        payable_paid = AccountsPayable.objects.filter(
            settlement_date=today,
            status=FinancialStatus.PAID,
        ).count()
        _append_notification(
            notifications,
            "Pagamento de titulo realizado hoje"
            if payable_paid == 1
            else "Pagamentos de titulos realizados hoje",
            payable_paid,
            reverse("cadastros_web:accounts_payable_list"),
        )

    open_assigned = Ticket.objects.filter(
        status=TicketStatus.OPEN,
        assigned_to=user,
    ).count()
    payload["ticket_open"] = open_assigned
    _append_notification(
        notifications,
        "Chamado aberto direcionado para voce"
        if open_assigned == 1
        else "Chamados abertos direcionados para voce",
        open_assigned,
        reverse("cadastros_web:ticket_list"),
    )

    reply_count = (
        TicketReply.objects.filter(ticket__created_by=user, created_at__gte=since)
        .exclude(author=user)
        .count()
    )
    payload["ticket_reply"] = reply_count
    _append_notification(
        notifications,
        "Resposta em chamado que voce abriu"
        if reply_count == 1
        else "Respostas em chamados que voce abriu",
        reply_count,
        reverse("cadastros_web:ticket_list"),
    )

    activities = filter_activities_for_user(ProjectActivity.objects.all(), user)
    late_count = (
        activities.filter(planned_end__lt=today)
        .exclude(status__in=[ActivityStatus.DONE, ActivityStatus.CANCELED])
        .count()
    )
    _append_notification(
        notifications,
        "Tarefa atrasada" if late_count == 1 else "Tarefas atrasadas",
        late_count,
        reverse("cadastros_web:project_activity_list"),
    )
    new_count = (
        activities.filter(created_at__gte=since)
        .exclude(status__in=[ActivityStatus.DONE, ActivityStatus.CANCELED])
        .count()
    )
    _append_notification(
        notifications,
        "Tarefa nova" if new_count == 1 else "Tarefas novas",
        new_count,
        reverse("cadastros_web:project_activity_list"),
    )
    return payload


def user_role(request):
    user = getattr(request, "user", None)
    role = resolve_user_role(user)
    notifications_payload = _build_notifications(user)
    notifications = notifications_payload["items"]
    return {
        "user_role": role,
        "can_view_financial": can_view_financial(user),
        "notifications": notifications,
        "notifications_count": sum(
            item.get("count", 0) for item in notifications
        ),
        "notify_ticket_open_count": notifications_payload["ticket_open"],
        "notify_ticket_reply_count": notifications_payload["ticket_reply"],
    }

from django.core.management.base import BaseCommand

from cadastros.models import (
    BillingInvoice,
    BillingPaymentStatus,
    FinancialStatus,
)


class Command(BaseCommand):
    help = "Sync BillingInvoice payment_status based on AccountsReceivable status."

    def add_arguments(self, parser):
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Apply changes to the database. Default is dry-run.",
        )

    def handle(self, *args, **options):
        commit = options["commit"]
        invoices = BillingInvoice.objects.prefetch_related(
            "accounts_receivable_titles"
        ).order_by("id")
        total = 0
        updated = 0
        unchanged = 0

        for invoice in invoices:
            total += 1
            receivables = list(invoice.accounts_receivable_titles.all())
            if not receivables:
                new_status = BillingPaymentStatus.UNPAID
            else:
                unpaid_exists = any(
                    receivable.status != FinancialStatus.PAID
                    for receivable in receivables
                )
                new_status = (
                    BillingPaymentStatus.UNPAID
                    if unpaid_exists
                    else BillingPaymentStatus.PAID
                )

            if invoice.payment_status == new_status:
                unchanged += 1
                continue

            updated += 1
            if commit:
                invoice.payment_status = new_status
                invoice.save(update_fields=["payment_status"])

        if commit:
            message = f"Sync complete. Updated {updated} of {total} invoices."
            self.stdout.write(self.style.SUCCESS(message))
        else:
            message = (
                f"Dry-run only. {updated} of {total} invoices would be updated."
            )
            self.stdout.write(self.style.WARNING(message))

import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from cadastros.whatsapp_notifications import dispatch_daily_whatsapp_reports


class Command(BaseCommand):
    help = "Run WhatsApp daily report scheduler."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run one check and exit.",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Seconds between checks in loop mode.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send regardless of configured time (use with --once).",
        )

    def handle(self, *args, **options):
        run_once = options["once"]
        interval = max(10, int(options["interval"] or 30))
        force = bool(options["force"])

        if force and not run_once:
            self.stdout.write(
                self.style.WARNING(
                    "Force mode with loop can resend repeatedly; disabling force."
                )
            )
            force = False

        while True:
            results = dispatch_daily_whatsapp_reports(
                now=timezone.localtime(), force=force
            )
            if run_once or any(results.values()):
                summary = (
                    "WhatsApp diarios: "
                    f"hoje={results['activities_today']}, "
                    f"atrasadas={results['activities_overdue']}, "
                    f"titulos={results['admin_due_titles']}"
                )
                self.stdout.write(self.style.SUCCESS(summary))
            if run_once:
                break
            time.sleep(interval)

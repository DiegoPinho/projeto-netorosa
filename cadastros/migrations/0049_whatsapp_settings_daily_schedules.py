from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0048_whatsapp_settings_api_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="whatsappsettings",
            name="daily_activities_time",
            field=models.TimeField(
                blank=True,
                help_text="Formato HH:MM.",
                null=True,
                verbose_name="Horario atividades de hoje (consultor)",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="daily_overdue_time",
            field=models.TimeField(
                blank=True,
                help_text="Formato HH:MM.",
                null=True,
                verbose_name="Horario atividades em atraso (consultor)",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="daily_admin_due_time",
            field=models.TimeField(
                blank=True,
                help_text="Formato HH:MM.",
                null=True,
                verbose_name="Horario titulos vencendo hoje (admin)",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="last_daily_activities_sent",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Ultimo envio atividades de hoje",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="last_daily_overdue_sent",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Ultimo envio atividades em atraso",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="last_daily_admin_due_sent",
            field=models.DateField(
                blank=True,
                editable=False,
                null=True,
                verbose_name="Ultimo envio titulos vencendo hoje",
            ),
        ),
    ]

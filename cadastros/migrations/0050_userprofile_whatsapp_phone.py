from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0049_whatsapp_settings_daily_schedules"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="whatsapp_phone",
            field=models.CharField(
                blank=True,
                help_text="Recebe mensagens de WhatsApp do sistema.",
                max_length=30,
                verbose_name="Telefone WhatsApp",
            ),
        ),
    ]

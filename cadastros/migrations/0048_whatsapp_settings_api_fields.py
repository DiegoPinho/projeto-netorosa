from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0047_whatsapp_settings_and_consultant_whatsapp_phone"),
    ]

    operations = [
        migrations.AddField(
            model_name="whatsappsettings",
            name="zapi_base_url",
            field=models.CharField(
                blank=True,
                default="https://api.z-api.io",
                max_length=200,
                verbose_name="API base Z-API",
                help_text="Ex.: https://api.z-api.io",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="zapi_instance_id",
            field=models.CharField(
                blank=True,
                max_length=120,
                verbose_name="Z-API Instance ID",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="zapi_token",
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name="Z-API Token",
            ),
        ),
        migrations.AddField(
            model_name="whatsappsettings",
            name="zapi_client_token",
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name="Z-API Client Token",
                help_text="Header exigido pela Z-API (client-token).",
            ),
        ),
    ]

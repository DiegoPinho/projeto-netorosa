from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0046_projectactivity_assumed_reason_and_billing_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="WhatsappSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                (
                    "opportunities_numbers",
                    models.TextField(
                        blank=True,
                        help_text="Informe um numero por linha.",
                        verbose_name="Numeros WhatsApp - oportunidades",
                    ),
                ),
                (
                    "financial_numbers",
                    models.TextField(
                        blank=True,
                        help_text="Informe um numero por linha.",
                        verbose_name="Numeros WhatsApp - financeiro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Parametrizacao WhatsApp",
                "verbose_name_plural": "Parametrizacao WhatsApp",
            },
        ),
        migrations.AddField(
            model_name="consultant",
            name="whatsapp_phone",
            field=models.CharField(
                blank=True,
                help_text=(
                    "Recebe mensagens de WhatsApp sobre titulos criados, pagos, "
                    "vencendo no dia e fechamentos."
                ),
                max_length=30,
                verbose_name="Telefone WhatsApp financeiro",
            ),
        ),
    ]

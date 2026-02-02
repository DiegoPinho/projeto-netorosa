from django.db import migrations, models


def map_billing_types(apps, schema_editor):
    ProjectActivity = apps.get_model("cadastros", "ProjectActivity")
    ProjectActivity.objects.filter(billing_type="assumed_rework").update(
        billing_type="assumed_company",
        assumed_reason="rework",
    )
    ProjectActivity.objects.filter(billing_type="assumed_unplanned").update(
        billing_type="assumed_company",
        assumed_reason="unplanned",
    )
    ProjectActivity.objects.filter(billing_type="assumed_courtesy").update(
        billing_type="assumed_company",
        assumed_reason="courtesy",
    )


def unmap_billing_types(apps, schema_editor):
    ProjectActivity = apps.get_model("cadastros", "ProjectActivity")
    ProjectActivity.objects.filter(
        billing_type="assumed_company",
        assumed_reason="rework",
    ).update(billing_type="assumed_rework")
    ProjectActivity.objects.filter(
        billing_type="assumed_company",
        assumed_reason="unplanned",
    ).update(billing_type="assumed_unplanned")
    ProjectActivity.objects.filter(
        billing_type="assumed_company",
        assumed_reason="courtesy",
    ).update(billing_type="assumed_courtesy")
    ProjectActivity.objects.filter(
        billing_type="assumed_company",
        assumed_reason="",
    ).update(billing_type="assumed_rework")
    ProjectActivity.objects.filter(billing_type="assumed_consultant").update(
        billing_type="billable"
    )
    ProjectActivity.objects.filter(billing_type="client_assigned").update(
        billing_type="billable"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("cadastros", "0045_project_contract_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectactivity",
            name="assumed_reason",
            field=models.CharField(
                blank=True,
                choices=[
                    ("rework", "Retrabalho"),
                    ("unplanned", "Nao Planejadas"),
                    ("courtesy", "Cortezia"),
                ],
                default="",
                max_length=20,
                verbose_name="Motivo",
            ),
        ),
        migrations.RunPython(map_billing_types, unmap_billing_types),
        migrations.AlterField(
            model_name="projectactivity",
            name="billing_type",
            field=models.CharField(
                choices=[
                    ("billable", "Faturavel"),
                    ("assumed_company", "Horas Assumidas (empresa)"),
                    ("assumed_consultant", "Horas Assumidas (Consultor)"),
                    ("client_assigned", "Atividade atribuida ao Cliente"),
                ],
                default="billable",
                max_length=20,
                verbose_name="Classificacao de horas",
            ),
        ),
    ]

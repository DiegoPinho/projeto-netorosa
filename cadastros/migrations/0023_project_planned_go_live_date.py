from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cadastros", "0022_candidateapplication_proposalrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="planned_go_live_date",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Go live planejado",
            ),
        ),
    ]

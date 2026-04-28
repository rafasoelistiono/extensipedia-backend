from django.db import migrations, models


def migrate_career_scope_to_competency(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(dashboard_access_scope="career").update(dashboard_access_scope="competency")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_user_dashboard_access_scope"),
    ]

    operations = [
        migrations.RunPython(migrate_career_scope_to_competency, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="dashboard_access_scope",
            field=models.CharField(
                choices=[
                    ("full", "Superadmin"),
                    ("academic", "Akademik"),
                    ("competency", "Kompetensi"),
                    ("advocacy", "Advokasi"),
                ],
                default="full",
                max_length=20,
            ),
        ),
    ]

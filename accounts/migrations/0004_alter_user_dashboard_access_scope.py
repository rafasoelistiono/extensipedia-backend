from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_dashboard_access_scope_and_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="dashboard_access_scope",
            field=models.CharField(
                choices=[
                    ("full", "Superadmin"),
                    ("academic", "Akademik"),
                    ("competency", "Kompetensi"),
                    ("career", "Karir"),
                    ("advocacy", "Advokasi"),
                ],
                default="full",
                max_length=20,
            ),
        ),
    ]
